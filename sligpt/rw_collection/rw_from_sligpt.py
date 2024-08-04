from sligpt.evaluation.evaluate import result_statistics_from_2_json_files
from sligpt.rw_collection.sligpt_core import need_to_check, \
    get_svar_in_BC_in_multiple_prompts
from sligpt.utils import load_a_json_file, dump_json_object_to_json, \
    write_a_kv_pair_to_a_json_file


def obtain_rw_data_sligpt(rw_data_path:str, rw_data_json_slither:str, contract_data_path:str):
    # the information of the 10 contracts used to evalute Sligpt

    # ================================
    contract_rw_data_sligpt={}

    rw_result_file_path = rw_data_path

    contract_function_rw_data_slither = load_a_json_file(
        rw_result_file_path + rw_data_json_slither)


    # the directory that holds the contract code saved in json files
    contract_data_path = contract_data_path


    for key, contract_data in contract_function_rw_data_slither.items():

        contract_rw_data={}
        for func, func_data in contract_data.items():
            if func not in ['stateVariables']:

                func_data_slither = contract_data[func]
                items=str(key).split('.sol')
                solidity_file_name=items[0]+".sol"
                contract_name=items[1]
                target_function = func
                state_variables_list =list(
                    contract_function_rw_data_slither[key]['stateVariables'].keys())

                # check if the function required to be checked
                check_status,check_results=need_to_check(solidity_file_name,contract_name,contract_data_path,target_function,state_variables_list)

                if check_status:
                    # need to further check
                    # prepare for the read information
                    function_rw_data_slither = {
                        func: {k: v for k, v in func_data_slither.items() if
                               k in ["state_variables_read_in_BC"]}}
                    modifiers = func_data_slither[
                        'modifiers'] if 'modifiers' in func_data_slither.keys() else []
                    # --------------------------------
                    # get rw data with multiple prompt
                    rw_data=get_svar_in_BC_in_multiple_prompts(
                        solidity_file_name, contract_name,contract_data_path,
                        target_function, function_rw_data_slither,
                        state_variables_list,modifiers=modifiers,check_response=check_results)

                    # keep the writes obtained from Slither
                    rw_data[func]['state_variables_written']=func_data_slither['state_variables_written']
                    contract_rw_data[func]=rw_data[func]
                else:
                    # keep the data from Slither
                    rw_data={func:{k:v for k,v in func_data_slither.items() if k in ["state_variables_read_in_BC",'state_variables_written']}}
                    contract_rw_data[func] = rw_data[func]

        contract_rw_data_sligpt[f'{solidity_file_name}{contract_name}'] = contract_rw_data
        contract_rw_data_sligpt[f'{solidity_file_name}{contract_name}']['stateVariables'] = state_variables_list


    # save the rw data
    dump_json_object_to_json(contract_rw_data_sligpt,f'{rw_result_file_path }contract_rw_data_sligpt.json')


def obtain_rw_data_sligpt_for_a_contract(solidity_file_name:str, contract_name:str, contract_data_path:str, rw_data_path:str, rw_data_json_slither:str):

    rw_result_file_path = rw_data_path

    contract_function_rw_data_slither = load_a_json_file(
        rw_result_file_path + rw_data_json_slither)

    key=f'{solidity_file_name}{contract_name}'
    contract_data = contract_function_rw_data_slither[key]


    contract_rw_data={}
    for func, func_data in contract_data.items():
        if func not in ['stateVariables']:

            func_data_slither = contract_data[func]
            items=str(key).split('.sol')
            solidity_file_name=items[0]+".sol"
            contract_name=items[1]
            target_function = func
            state_variables_list =list(
                contract_function_rw_data_slither[key]['stateVariables'].keys())

            # check if the function required to be checked
            check_status,check_results=need_to_check(solidity_file_name,contract_name,contract_data_path,target_function,state_variables_list)

            if check_status:
                # need to further check
                # prepare for the read information
                function_rw_data_slither = {
                    func: {k: v for k, v in func_data_slither.items() if
                           k in ["state_variables_read_in_BC"]}}
                modifiers = func_data_slither[
                    'modifiers'] if 'modifiers' in func_data_slither.keys() else []
                # --------------------------------
                # get rw data with multiple prompt
                rw_data=get_svar_in_BC_in_multiple_prompts(
                    solidity_file_name, contract_name,contract_data_path,
                    target_function, function_rw_data_slither,
                    state_variables_list,modifiers=modifiers,check_response=check_results)

                # keep the writes obtained from Slither
                rw_data[func]['state_variables_written']=func_data_slither['state_variables_written']
                contract_rw_data[func]=rw_data[func]
            else:
                # keep the data from Slither
                rw_data={func:{k:v for k,v in func_data_slither.items() if k in ["state_variables_read_in_BC",'state_variables_written']}}
                contract_rw_data[func] = rw_data[func]

    contract_rw_data['stateVariables'] = state_variables_list
    # save the rw data
    write_a_kv_pair_to_a_json_file(
        rw_result_file_path + "contract_rw_data_sligpt.json", key, contract_rw_data)


def obtain_rw_data_sligpt_for_a_function(solidity_file_name:str, contract_name:str, function_name:str, contract_data_path:str, rw_data_path:str, rw_data_json_slither:str):

    rw_result_file_path = rw_data_path

    contract_function_rw_data_slither = load_a_json_file(
        rw_result_file_path + rw_data_json_slither)

    key=f'{solidity_file_name}{contract_name}'
    contract_data = contract_function_rw_data_slither[key]


    contract_rw_data={}
    for func, func_data in contract_data.items():
        if func not in ['stateVariables'] and func in [function_name]:

            func_data_slither = contract_data[func]
            items=str(key).split('.sol')
            solidity_file_name=items[0]+".sol"
            contract_name=items[1]
            target_function = func
            state_variables_list =list(
                contract_function_rw_data_slither[key]['stateVariables'].keys())

            # check if the function required to be checked
            check_status,check_results=need_to_check(solidity_file_name,contract_name,contract_data_path,target_function,state_variables_list)

            if check_status:
                # need to further check
                # prepare for the read information
                function_rw_data_slither = {
                    func: {k: v for k, v in func_data_slither.items() if
                           k in ["state_variables_read_in_BC"]}}
                modifiers = func_data_slither[
                    'modifiers'] if 'modifiers' in func_data_slither.keys() else []
                # --------------------------------
                # get rw data with multiple prompt
                rw_data=get_svar_in_BC_in_multiple_prompts(
                    solidity_file_name, contract_name,contract_data_path,
                    target_function, function_rw_data_slither,
                    state_variables_list,modifiers=modifiers,check_response=check_results)

                # keep the writes obtained from Slither
                rw_data[func]['state_variables_written']=func_data_slither['state_variables_written']
                contract_rw_data[func]=rw_data[func]
            else:
                # keep the data from Slither
                rw_data={func:{k:v for k,v in func_data_slither.items() if k in ["state_variables_read_in_BC",'state_variables_written']}}
                contract_rw_data[func] = rw_data[func]

    contract_rw_data['stateVariables'] = state_variables_list
    # save the rw data
    write_a_kv_pair_to_a_json_file(
        rw_result_file_path + "contract_rw_data_sligpt.json", key, contract_rw_data)



def result_statistics(rw_result_file_path:str,sligpt_rw_data_json:str,gt_rw_data_json:str,flag_read:bool=True):
    # ================================
    # evaluate

    result_statistics_from_2_json_files(rw_result_file_path,sligpt_rw_data_json,gt_rw_data_json,"sligpt_and_gt",flag_read=flag_read)




if __name__=="__main__":

    obtain_rw_data_sligpt("../../results/rw_results/","contract_rw_data_slither.json","../../results/contract_data/")


    # result_statistics("../../results/rw_results/","contract_rw_data_sligpt.json","contract_rw_data_gt.json")



