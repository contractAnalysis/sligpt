
import time


from sligpt.config import solidity_built_in_variables, GPT4_model, \
    assignment_operators, condition_types, \
    contract_data_path, result_path, sleep_time, rw_contracts_info

from sligpt.get_contract_data import get_contract_data
from sligpt.utils_openai import gpt_request_chatComplection, \
    gpt_request_chatComplection_new
from sligpt.utils import load_specific_prompt_data, dump_json, \
    extract_json_data_from_response_in_dict, load_a_json_file, remove_comments, \
    present_list_as_str, dump_json_object_to_json, get_a_kv_pair_from_a_json, \
    write_a_kv_pair_to_a_json_file

from sligpt.evaluation.evaluate import result_statistics_from_2_json_files


def generate_from_gpt(solidity_file_name: str, contract_name: str,
                      contract_code: str, contracts_data_path: str, target_functions:list, prompt_file_name:str, msg_key:str, purpose:str,
                      times: int = 1) -> dict:
    # get prompt data
    prompt_data = load_specific_prompt_data(prompt_file_name,msg_key)

    # prepare prompt required data
    msg_data = {}
    for data_item in prompt_data['user']['data']:
        if data_item == 'contract_name':
            value = contract_name
        elif data_item == 'contract_code':
            value = contract_code
        elif data_item=='functions':
            value=present_list_as_str(target_functions)
        elif data_item == 'solidity_based_variables':
            value = present_list_as_str(solidity_built_in_variables)
        elif data_item == "assignment_operators":
            value = assignment_operators
        elif data_item == 'condition_types':
            value = present_list_as_str(condition_types)
        else:
            assert False,f"required data {data_item} for message is not provided"
            print(f'{data_item} is not provided. ')
            return
        msg_data[data_item] = value

    # add system message
    sys_content= prompt_data["system"]["content"]
    sys_content=sys_content.replace(f'##condition_types##',f"{msg_data['condition_types']}")
    msg = [{"role": "system", "content": sys_content}]

    # add user message
    user_msg = prompt_data["user"]["content"]
    for data_item in prompt_data["user"]["data"]:
        user_msg = user_msg.replace("##{}##".format(data_item),
                                    "{}".format(msg_data[data_item]))
    msg.append({"role": "user", "content": user_msg})

    results = {}

    for i in range(times):
        # save the results
        json_file_path = result_path + "gpt_evaluation_intermediate_results\\" + "evaluation_result_gpt_alone.json"
        key = f'{solidity_file_name}_{contract_name}_target_functions_evaluation_result_gpt_alone_{i}'
        saved_value = get_a_kv_pair_from_a_json(json_file_path, key)
        if len(saved_value)==0:
            time.sleep(sleep_time)
            # requst ChatGPT
            response = gpt_request_chatComplection_new(GPT4_model, msg)
            all_tasks_results = extract_json_data_from_response_in_dict(response)
            write_a_kv_pair_to_a_json_file(json_file_path, key, all_tasks_results)
        else:
            all_tasks_results=get_a_kv_pair_from_a_json(json_file_path, key)

        results[i] = all_tasks_results
    return results




def get_function_rw_data_gpt(solidity_file_name, contract_name, contract_data_path: str,
                                 result_path: str,target_functions:list,times:int=1):

    # get contract code for the prompt preparation
    contract_data_path_name = contract_data_path + f"{solidity_file_name}_{contract_name}_contract_level_data.json"
    contract_level_data = load_a_json_file(contract_data_path_name)

    # prepare for the code of the contract and the code of the inherited contracts
    contract_code=""
    if contract_name in contract_level_data.keys():
        contract_code = contract_level_data[contract_name]["code"]
    for name in contract_level_data.keys():
        if name not in [contract_name,'SafeMath']: # to-do-list: how to ignore libraries
            contract_code+="\n"+contract_level_data[name]["code"]
    results=[]
    if len(contract_code)>0:
        contract_code_no_comment=remove_comments(contract_code)

        results=generate_from_gpt(solidity_file_name,
                               contract_name,
                               contract_code_no_comment,
                               result_path,
                               target_functions,
                               "rw_prompt_formats",
                                "function_rw_one_prompt",
                                "function_rw_data",
                               times)
    else:
        print(f'Fail to get contract code for {contract_name}')
    return results

def get_function_rw_data_gpt_test():
    index = 0
    param = rw_contracts_info[index]
    solidity_file_name = param[0]
    contract_name = param[1]
    # solc_version = param[2]
    # here_dataset_solidity_path = dataset_solidity_path
    target_functions=['Ownable.transferOwnership(address)', 'HoloToken.transfer(address,uint256)', 'HoloToken.balanceOf(address)', 'HoloToken.transferFrom(address,address,uint256)', 'HoloToken.approve(address,uint256)', 'HoloToken.allowance(address,address)', 'HoloToken.increaseApproval(address,uint256)', 'HoloToken.decreaseApproval(address,uint256)', 'HoloToken.setMinter(address)', 'HoloToken.mint(address,uint256)', 'HoloToken.finishMinting()', 'HoloToken.setDestroyer(address)', 'HoloToken.burn(uint256)']
    get_function_rw_data_gpt( solidity_file_name,
                                  contract_name,
                                  contract_data_path,
                                  result_path,
                                  target_functions,
                                  times=1)


def result_statistics(rw_result_file_path:str, gpt4_rw_data_json:str, gt_rw_data_json:str, flag_read:bool=True):
    # ================================
    # evaluate
    result_statistics_from_2_json_files(rw_result_file_path, gpt4_rw_data_json, gt_rw_data_json, "gpt4_and_gt", flag_read=flag_read)


def get_rw_data_from_gpt_one_contract(solidity_file_name:str,contract_name:str,contract_data_path:str,rw_data_json_path:str,rw_data_json_slither:str, flag_save_result:bool=True):
    # =====================================
    contract_function_rw_data_slither=load_a_json_file(rw_data_json_path+rw_data_json_slither)

    key=f'{solidity_file_name}{contract_name}'
    con_data=contract_function_rw_data_slither[key]
    target_functions = [name for name in con_data.keys() if
                        name not in ['stateVariables']]
    results = get_function_rw_data_gpt(solidity_file_name,
                                       contract_name,
                                       contract_data_path,
                                       result_path,
                                       target_functions,
                                       times=1)
    if flag_save_result:
        write_a_kv_pair_to_a_json_file(rw_data_json_path+"contract_rw_data_gpt.json", key, results[0])
    return results[0]


def get_rw_data_from_gpt(rw_data_path:str, rw_data_json_file_name:str,contract_data_path:str):
    # =====================================
    contract_function_rw_data_slither=load_a_json_file(rw_data_path+rw_data_json_file_name)


    contract_rw_data_gpt = {}
    for key, contract_data in contract_function_rw_data_slither.items():
        items = str(key).split('.sol')
        solidity_file_name = items[0] + ".sol"
        contract_name = items[1]
        if key in contract_function_rw_data_slither.keys():
            con_data=contract_function_rw_data_slither[key]
            target_functions=[name for name in con_data.keys() if name not in ['stateVariables']]

            results=get_function_rw_data_gpt(solidity_file_name,
                                     contract_name,
                                     contract_data_path,
                                     result_path,
                                     target_functions,
                                     times=1)

            contract_rw_data_gpt[f'{solidity_file_name}{contract_name}'] = results[0]

    dump_json_object_to_json(contract_rw_data_gpt,
                             f'{rw_data_path}contract_rw_data_gpt.json')


if __name__=="__main__":


    # # =====================================
    # get the contract level data
    # get_contract_level_data(parameters)

    # # =====================================
    # get_rw_data_from_gpt("../../results/rw_results/","contract_rw_data_slither.json","../../results/contract_data/")

    #=========================
    # evaluation
    result_statistics("../../results/rw_results/","contract_rw_data_gpt.json","contract_rw_data_gt.json")




