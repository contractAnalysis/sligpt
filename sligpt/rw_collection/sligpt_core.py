import ast
import json
import random
from time import sleep

import sligpt.config
from sligpt.config import condition_types, GPT4_model, result_path, sleep_time
from sligpt.utils_openai import gpt_request_chatComplection_new
from sligpt.utils import load_a_json_file, remove_comments, load_specific_prompt_data, \
    color_print, present_list_as_str_or, \
    check_equal_data, write_a_kv_pair_to_a_json_file, \
    get_a_kv_pair_from_a_json, present_examples, \
    get_json_data_from_response_in_dict, present_examples_for_dict

prompt_json="rw_prompt_formats_5"


def get_contract_code(solidity_file_name:str, contract_name:str, contracts_data_path:str)->str:
    """
    prepare for the Solidity code
    :param solidity_file_name:
    :param contract_name:
    :param contracts_data_path:
    :return:
    """
    # get contract code for the prompt preparation
    contract_data_path_name = contracts_data_path + f"{solidity_file_name}_{contract_name}_contract_level_data.json"
    contract_level_data = load_a_json_file(contract_data_path_name)
    # prepare for the code of the contract and the code of the inherited contracts
    contract_code = ""
    if contract_name in contract_level_data.keys():
        contract_code = contract_level_data[contract_name]["code"]
    for name in contract_level_data.keys():
        if name not in [contract_name,
                        'SafeMath']:  # to-do-list: how to ignore libraries
            contract_code += "\n" + contract_level_data[name]["code"]
    if len(contract_code) == 0: return contract_code
    contract_code_no_comment = remove_comments(contract_code)
    return contract_code_no_comment


def message_preparation(state:str, contract_name:str, contract_code:str, target_function:str, function_rw_data:dict, state_variables_list:list, msg:list=[], runtime_msg:dict={},modifiers:list=[], iteration:int=1):
    # prepare prompt data
    check= load_specific_prompt_data(prompt_json, 'need_to_check')
    acceptance=load_specific_prompt_data(prompt_json,'acceptance')
    acceptance_1 = load_specific_prompt_data(prompt_json, 'acceptance_1')
    verification = load_specific_prompt_data(prompt_json, 'verification')

    consider_items=[]
    if state in ['check']:
        consider_items=check['user']['data']
    elif state in ['accept']:
        if iteration>1:
            consider_items = acceptance_1['user']['data']
        else:
            consider_items=acceptance['user']['data']
    elif state in ['verify']:
        consider_items=verification['user']['data']
    else:
        pass

    all_data_items_values = {}
    all_data_items = list(set(
        check['user']['data'] +
        acceptance['user']['data'] +
        acceptance_1['user']['data'] +
        verification['user']['data']))

    for data_item in all_data_items:
        value=''
        if data_item not in consider_items:continue
        if data_item in ['questions',"answer_specification","acceptance_examples"]:continue
        if data_item == 'contract_name':
            value = contract_name
        elif data_item == 'contract_code':
            value = contract_code
        elif data_item == 'function_name':
            value = target_function
        elif data_item == 'function_rw_data':
            value = function_rw_data
        elif data_item == 'state_variables_list':
            value = state_variables_list
        elif data_item == 'condition_types':
            value = present_list_as_str_or(condition_types)

        elif data_item=='check_examples':
            value=present_examples(list(check['check_examples'].values()))

        elif data_item=='identification_rules':
            value=acceptance['identification_rules']
        # elif data_item=='acceptance_examples':
        #     value=present_examples(list(acceptance['acceptance_examples'].values()))

        elif data_item=='verification_examples':
            value=present_examples(list(verification['verification_examples'].values()))

        else:
            print(f'{data_item} is not provided. ')
        all_data_items_values[data_item]=value

    cur_msg=[]
    if state in ['check','accept','verify']:
        if state in ['accept']:
            if iteration>1:
                cur_msg=msg

    # prepare for the system message
    if state in ['check','verify','accept']:
        if len(cur_msg)==0:
            sys_msg = check['system']['content']
            for data_item in check['system']['data']:
                if f'##{data_item}##' in sys_msg:
                    sys_msg = sys_msg.replace(f'##{data_item}##',
                                              f'##{all_data_items_values[data_item]}##')
            cur_msg = [{"role": "system", "content": sys_msg}]


    # prepare for the user message
    if state in ['check']:
        #---------------------------
        user_msg = check["user"]["content"]
        for data_item in check["user"]["data"]:
            user_msg=user_msg.replace(f'##check_examples##',f'{all_data_items_values["check_examples"]}')
            if data_item in ['check_examples']:continue
            user_msg = user_msg.replace("##{}##".format(data_item),
                                        "{}".format(
                                            all_data_items_values[data_item]))
        cur_msg.append({"role": "user", "content": user_msg})

    elif state in ['accept']:
        #----------------------------
        if iteration==1:
            content=acceptance["user"]["content"]
            #examples_keys=["case5","FP2","FN1", "case7","case3"]
            basic_keys=["case5","FP2","case7"]
            selected=random.choice(["FN1","case3"])
            acceptance_examples=present_examples_for_dict(acceptance['acceptance_examples'],basic_keys+[selected])

            content = content.replace(f'##acceptance_examples##',
                                        acceptance_examples)
            content = content.replace(f'##identification_rules##',
                                      all_data_items_values[
                                          'identification_rules'])
            data=acceptance["user"]["data"]
        else:
            content = acceptance_1["user"]["content"]
            data = acceptance_1["user"]["data"]

        user_msg = content
        for data_item in data:
            if data_item in ["acceptance_examples"]: continue
            user_msg = user_msg.replace("##{}##".format(data_item),
                                        "{}".format(
                                            all_data_items_values[data_item]))
        # in case of there is runtime feedback
        run_msg=""
        for value in runtime_msg.values():
            run_msg += f'{value}\n'
        user_msg=f'{run_msg}{user_msg}'
        cur_msg.append({"role": "user", "content": user_msg})

    elif state in ['verify']:
        #----------------------------
        # prepare values for certain data items
        svar_in_BC = []
        if target_function in function_rw_data.keys():
            if "state_variables_read_in_BC" in function_rw_data[
                target_function].keys():
                svar_in_BC = function_rw_data[target_function][
                    "state_variables_read_in_BC"]
        question_keys=[
                       ["miss_svar_in_functions_invoked_in_conditions","a)"],
                       ["miss_svar_in_conditions_in_functions_invoked","b)"],
                       ["miss_svar_in_conditions_in_modifiers","c)"],
                       ["contain_svar_in_conditions_from_return_statement","d)"],
                       ["all_given_svar_having_related_conditions","e)"],
                       ["miss_svar_in_local_svar_in_conditions","f)"],
                       ]
        indices=[0,1,5]
        if len(svar_in_BC) > 0:
            indices+=[3,4]
        if len(modifiers)>0:
            indices+=[2]

        questions=""
        indices.sort()
        for idx in indices:
            key=question_keys[idx]
            if idx==4:
                q_content=verification["user"]["questions"][key[0]]
                q_content=q_content.replace(f'##svar_in_BC##',f"{svar_in_BC}")
            elif idx==2:
                q_content = verification["user"]["questions"][key[0]]
                q_content = q_content.replace(f'##modifiers##',
                                              f"{modifiers}")
            else:
                q_content=verification["user"]["questions"][key[0]]
            questions+=f'{key[-1]} {q_content}'



        user_msg = verification["user"]["content"]
        user_msg=user_msg.replace("##{}##".format("questions"),questions)
        user_msg = user_msg.replace("##{}##".format("answer_specification"), verification["user"]["answer_specification"])
        user_msg = user_msg.replace("##{}##".format("verification_examples"),
                                    all_data_items_values['verification_examples'])
        user_msg = user_msg.replace("##{}##".format("identification_rules"),
                                    all_data_items_values['identification_rules'])

        for data_item in verification["user"]["data"]:
            if data_item in ["modifiers","questions","answer_specification","verification_examples","identification_rules"]:continue

            replace_value = all_data_items_values[data_item]

            user_msg = user_msg.replace("##{}##".format(data_item),
                                        "{}".format(replace_value))
        cur_msg.append({"role": "user", "content": user_msg})

    else:
        print(f'no prompt message is prepared!')
        pass
    return cur_msg


def extract_response_with_gpt(given_response:str):
    correct_response = load_specific_prompt_data(prompt_json,
                                              'extract_correct_response')
    # add system message
    sys_msg =  correct_response["system"]["content"]
    msg = [{"role": "system", "content": sys_msg}]

    # add user message
    user_msg =  correct_response["user"]['content']
    for data_item in correct_response['user']['data']:
        if data_item=='given_response':
            user_msg=user_msg.replace(f'##{data_item}##',given_response)
    msg.append({"role": "user", "content": user_msg})
    sleep(sleep_time)
    response0 = gpt_request_chatComplection_new("gpt-4-1106-preview", msg)
    if "```json" in response0:
        response0=response0.strip("```json")
        response0=response0.strip("```")
        return json.loads(response0)
    else:
        if response0.startswith("{") and response0.endswith('}'):
            response0=json.loads(response0)
        return response0


def need_to_check(solidity_file_name:str,contract_name:str,contracts_data_path:str,function_name:str,state_variables_list:list, result_save_path:str=""):

    # get contract code for the prompt preparation
    contract_code_no_comment =get_contract_code(solidity_file_name, contract_name, contracts_data_path)
    # prepare for message
    function_rw_data={}
    msg=message_preparation('check',contract_name,contract_code_no_comment,function_name,function_rw_data,state_variables_list)

    # save the results
    json_file_path = result_path + "gpt_evaluation_intermediate_results\\" + "need_to_check_results.json"
    key = f'{solidity_file_name}_{contract_name}_{function_name}_need_to_check_result'
    saved_value=get_a_kv_pair_from_a_json(json_file_path,key)

    if len(saved_value)==0:
        sleep(sleep_time)
        response1 = gpt_request_chatComplection_new(GPT4_model, msg)
        check_results = get_json_data_from_response_in_dict(response1)
        write_a_kv_pair_to_a_json_file(json_file_path, key, check_results)
    else:
        check_results=saved_value

    color_print('Red',
                f'\n\n===={solidity_file_name}===={contract_name}===={function_name}====')
    color_print('Red',
                f'============== check results ===================')

    for k,v in check_results.items():
        color_print('Blue', f'{k}:')
        color_print('Gray', f'\t{v}')
    if check_results['Answer'] in ['yes']:
        return True,check_results
    else:
        return False,check_results

def accept(solidity_file_name:str, contract_name:str,contracts_data_path:str, function_name:str, function_rw_data:dict, state_variables_list:list, msg:list, my_msg:dict={}, modifiers:list=[],iteration:int=1):
    # get contract code for the prompt preparation
    contract_code_no_comment = get_contract_code(solidity_file_name,
                                                 contract_name,
                                                 contracts_data_path)

    msg=message_preparation('accept',  contract_name,contract_code_no_comment, function_name, function_rw_data, state_variables_list, msg, runtime_msg=my_msg,
                            iteration=iteration)

    # get the saved results if there are
    json_file_path = result_path + "gpt_evaluation_intermediate_results\\" + "evaluation_results_multiple_prompts_accept.json"
    key1 = f'{solidity_file_name}_{contract_name}_{function_name}_evaluation_results_multiple_prompts_accept_extraction_{iteration}'
    key2 = f'{solidity_file_name}_{contract_name}_{function_name}_evaluation_results_multiple_prompts_accept_response_{iteration}'

    saved_value = get_a_kv_pair_from_a_json(json_file_path, key1)
    response2= get_a_kv_pair_from_a_json(json_file_path,key2)

    if len(saved_value) == 0:
        sleep(sleep_time)
        response2 = gpt_request_chatComplection_new(GPT4_model, msg)
        # acceptance_results = extract_json_data_from_response_in_dict_wc(
        #     response2, function_name)
        # acceptance_results = extract_response_with_gpt(response2)
        acceptance_results = get_json_data_from_response_in_dict(response2,function_name=function_name)
        if len(acceptance_results)==0 or (isinstance(acceptance_results,str) and len(acceptance_results)>20) :
            acceptance_results = extract_response_with_gpt(response2)
        if len(acceptance_results)>0:
            write_a_kv_pair_to_a_json_file(json_file_path, key1, acceptance_results)
            write_a_kv_pair_to_a_json_file(json_file_path, key2, f"""{response2}""" )

    else:
        acceptance_results= saved_value

    msg.append(
        {"role": "assistant",
         "content": response2})

    color_print('Red',
                f'\n\n============== acceptance results ===================')
    answer=acceptance_results
    if isinstance(acceptance_results,dict):
        if "Answer" in answer.keys():
            answer=answer['Answer']
    elif isinstance(answer,str):
        if len(answer)>20:
            # very likely contain reasons and/or updates
            try:
                answer=ast.literal_eval(answer)
                answer = json.loads(answer)
            except:
                answer=acceptance_results
                pass
            if isinstance(answer,dict):
                if "Answer" in answer.keys():
                    answer=answer['Answer']

    if isinstance(answer,str) and ('not accept' not in answer and 'Not accept' not in answer) and ('accept' in answer or 'Accept' in answer):
        # accept the given data
        color_print('Blue', f'\n------ accept the data -----')
        print(f'the data:\n\t{function_rw_data}')
        print(f'Response:\n\t{response2}')
        return msg, 'accept'
    else:
        if isinstance(answer,dict):
            if function_name in answer.keys():
                color_print('Blue', f'\n------ update the data -----')
                print(f'Given data:\n\t{function_rw_data}')
                print(f'Response:\n\t{response2}')
                print(f'extraction:\n\t{answer}')
                return msg,answer

        color_print('Blue', f'\n------ not sure about the data -----')
        print(f'Given data:\n\t{function_rw_data}')
        print(f'Response:\n\t{response2}')
        print(f'extraction:\n\t{answer}')
        return msg,'not sure'


def verify(solidity_file_name:str, contract_name:str, contracts_data_path:str, function_name:str, function_rw_data:dict, state_variables_list:list,modifiers:list=[], iteration:int=1,verify_inner_loop_index:int=1):
    contract_code_no_comment = get_contract_code(solidity_file_name,
                                                 contract_name,
                                                 contracts_data_path)
    msg = message_preparation('verify', contract_name,
                              contract_code_no_comment, function_name,
                              function_rw_data, state_variables_list,modifiers=modifiers)
    # get the saved results if there are
    json_file_path = result_path + "gpt_evaluation_intermediate_results\\" + "evaluation_results_multiple_prompts_verify.json"
    key1 = f'{solidity_file_name}_{contract_name}_{function_name}_evaluation_results_multiple_prompts_verify_extraction_{iteration}'
    key2=f'{solidity_file_name}_{contract_name}_{function_name}_evaluation_results_multiple_prompts_verify_response_{iteration}'

    saved_value = get_a_kv_pair_from_a_json(json_file_path, key1)
    response3=get_a_kv_pair_from_a_json(json_file_path,key2)

    if len(saved_value)==0:
        sleep(sleep_time)
        response3 = gpt_request_chatComplection_new(GPT4_model, msg)

        # verification_results = extract_json_data_from_response_in_dict_wc(response3, function_name)
        # verification_results = extract_response_with_gpt(response3)
        verification_results = get_json_data_from_response_in_dict(response3)
        if len(verification_results)==0 or (isinstance(verification_results,str) and len(verification_results)>20):
            verification_results = extract_response_with_gpt(response3)
        if len(verification_results)>0:
            # save results
            write_a_kv_pair_to_a_json_file(json_file_path, key1, verification_results)
            write_a_kv_pair_to_a_json_file(json_file_path, key2, f"""{response3}""")

    else:
        verification_results=saved_value

    # add the response
    msg.append({"role": "assistant", "content": response3})

    color_print('Red',
                f'\n\n============== verification results ===================')

    answer=verification_results
    if isinstance(verification_results,dict):
        if "Answer" in verification_results.keys():
            answer=verification_results["Answer"]

    if isinstance(answer,str):
        if "not pass" in answer or 'Not pass' in answer:
            # assume that the updated data
            color_print('Blue',
                        f'\n------ does not verify the given data -----')
            print(f'Given data:\n\t{function_rw_data}')
            print(f'Response:\n\t{response3}')
            print(f'extraction:\n\t{answer}')
            return msg, "not pass"
        else:
            if 'pass' in answer or 'Pass' in answer:
                # agree the data is correct
                color_print('Blue',
                            '\n------ verified the given data -----')
                print(f'Given data:\n\t{function_rw_data}')
                print(f'Response:\n\t{response3}')
                print(f'extraction:\n\t{answer}')
                return msg, 'pass'


    color_print('Blue', f'\n------ not sure -----')
    print(f'Given data:\n\t{function_rw_data}')
    print(f'Response:\n\t{response3}')
    print(f'extraction:\n\t{answer}')
    return msg, answer


def get_svar_in_BC_in_multiple_prompts(solidity_file_name:str, contract_name:str, contracts_data_path:str, target_function:str, function_rw_data:dict, state_variables_list:list,modifiers:list=[],check_response:dict={}):
    color_print('Red',f'============== {target_function} ==============')
    print(f'Initial given data:\n\t{function_rw_data}')
    loop_idx=0
    msg = []
    my_msg={}
    updated_func_rw_data=function_rw_data
    flag_termination=False
    while True:
        loop_idx+=1
        if loop_idx>sligpt.config.evaluation_loops: break
        #------------------------------------------
        # accept the given data or update the data
        msg,accept_results=accept(solidity_file_name,contract_name,contracts_data_path,target_function,updated_func_rw_data,state_variables_list,msg,my_msg,iteration=loop_idx)

        if isinstance(accept_results,str):
            if 'not sure' in accept_results:
                my_msg = {
                    "from_accept": f'We are not able to extract or understand your response.'}
                continue
            else:
                # accept
                pass
        else:
            # updated data, to get more details
            if not check_equal_data(
                    updated_func_rw_data[target_function],
                    accept_results[target_function]):
                updated_func_rw_data = accept_results




        # ----------------------
        # verity the given data
        verify_loop_idx=0
        while True:
            verify_loop_idx+=1
            if verify_loop_idx>4:break
            msg_verify, verify_results = verify(solidity_file_name,
                                                contract_name,
                                                contracts_data_path,
                                                target_function,
                                                updated_func_rw_data,
                                                state_variables_list,
                                                modifiers=modifiers,
                                                iteration=loop_idx,verify_inner_loop_index=verify_loop_idx)
            if isinstance(verify_results, str):
                if "not pass" in verify_results:
                    # assume that the messages for verification are in a separate thread
                    my_msg = {
                        "from_verify": f"However, the given data do not pass verification. This is the feedback:{msg_verify[2]['content']}. "}
                    # end of the verification step
                    break
                else:
                    # pass and terminate
                    if 'pass' in verify_results:
                        flag_termination=True
                        break
                    else:
                        # not sure the anser
                        continue
            else:
                # we are not able to extract or undertand your reply
                # continue to verify
                continue

        if flag_termination:
            break

    # return
    if len(updated_func_rw_data)>0:
        return updated_func_rw_data
    else:
        return function_rw_data


