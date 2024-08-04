from sligpt.data_presentation.data_markdown import markdown_table_detailed_1
from sligpt.evaluation.utils_evaluation import evaluate_name_list, \
    evaluate_condition_list, evaluate_list

from sligpt.utils import dump_json, load_a_json_file


def evaluate_names(actual_generated_names:dict,expected_names:dict, result_path_name:str):
    results_all={}
    for name_category,names in expected_names.items():
        if name_category not in actual_generated_names.keys():
            actual_names=[]
        else:
            actual_names=actual_generated_names[name_category]
        result=evaluate_name_list(actual_names,names)
        results_all[name_category]=result

    # output
    dump_json(results_all,result_path_name)
    return results_all



def evaluate_conditions(actual_generated_conditions: dict, expected_conditions: dict,
                   result_path_name: str):
    results_all = {}

    all_modifier_or_function_names=list(set(list(actual_generated_conditions.keys())+list(expected_conditions.keys())))

    for m_or_f_name in all_modifier_or_function_names:
        if m_or_f_name in expected_conditions.keys():
            expected_condi=expected_conditions[m_or_f_name]
        else:
            expected_condi=[]
        if m_or_f_name in actual_generated_conditions.keys():
            actual_condi=actual_generated_conditions[m_or_f_name]
        else:
            actual_condi=[]

        result = evaluate_condition_list(actual_condi, expected_condi)
        results_all[m_or_f_name] = result

    # output
    dump_json(results_all, result_path_name)
    return results_all


def evaluate_assignments(actual_generated_assignments: dict, expected_assignments: dict,
                         result_path_name: str):
    results_all = {}

    all_modifier_or_function_names = list(
        set(list(actual_generated_assignments.keys()) + list(
            expected_assignments.keys())))

    for m_or_f_name in all_modifier_or_function_names:
        if m_or_f_name in expected_assignments.keys():
            expected_condi = expected_assignments[m_or_f_name]
        else:
            expected_condi = []
        if m_or_f_name in actual_generated_assignments.keys():
            actual_condi = actual_generated_assignments[m_or_f_name]
        else:
            actual_condi = []

        result = evaluate_list(actual_condi, expected_condi)
        results_all[m_or_f_name] = result

    # output
    dump_json(results_all, result_path_name)
    return results_all


def result_statistics_from_2_json_files(json_file_path:str,file_target:str,file_gt:str,comparison_result_name_prefix:str,flag_read: bool = True,flag_save_in_file:bool=True):
    # ================================
    # evaluate
    rw_result_file_path = json_file_path
    contract_function_rw_data_target = load_a_json_file(
        rw_result_file_path + file_target)

    contract_function_rw_data_gt = load_a_json_file(
        rw_result_file_path + file_gt)

    if flag_read:
        contract_evaluation_read_result = {}
        for key, contract_data in contract_function_rw_data_gt.items():
            if key not in contract_function_rw_data_target.keys(): continue
            for func, func_data in contract_data.items():
                if func not in ['stateVariables']:
                    func_data_target=[]
                    if func in contract_function_rw_data_target[key].keys():
                        func_data_target = contract_function_rw_data_target[key][
                            func]
                    else:
                        if "." in func:
                            func_name=func.split('.')[-1]
                            if "(" in func_name:
                                func_name=func_name.split(f'(')[0]
                            if func_name in contract_function_rw_data_target[key].keys():
                                func_data_target = \
                                contract_function_rw_data_target[key][func_name]
                            else:
                                if "(" in func:
                                    p_name=func.split(f'(')[0]
                                    if p_name in contract_function_rw_data_target[key].keys():
                                        func_data_target = \
                                            contract_function_rw_data_target[
                                                key][p_name]

                    if len(func_data_target)>0:
                        # evaluate the read
                        if "state_variables_read_in_BC" in func_data_target.keys():
                            result = evaluate_name_list(
                                func_data_target['state_variables_read_in_BC'],
                                func_data['state_variables_read_in_BC'])
                        else:
                            result = evaluate_name_list(
                                func_data_target['state_variables_read_BC'],
                                func_data['state_variables_read_in_BC'])

                        contract_evaluation_read_result[f'{key}#{func}'] = result
                    else:
                        print('x-----------------------')

        # organize results
        if flag_save_in_file:
            save_result_file_path_name = f'{rw_result_file_path}{comparison_result_name_prefix}_comparison_results_reads.csv'
        else:
            save_result_file_path_name = ""
        statistics=markdown_table_detailed_1(contract_evaluation_read_result, "",
                                  "", "",
                                  task_name="reads",
                                  output_result_path_name=save_result_file_path_name)
    else:
        contract_evaluation_write_result = {}
        for key, contract_data in contract_function_rw_data_gt.items():
            if key not in contract_function_rw_data_target.keys(): continue
            for func, func_data in contract_data.items():
                if func not in ['stateVariables']:
                    func_data_target = contract_function_rw_data_target[key][
                        func]
                    # evaluate the writes
                    result = evaluate_name_list(
                        func_data_target['state_variables_written'],
                        func_data['state_variables_written'])
                    contract_evaluation_write_result[f'{key}#{func}'] = result
        # organize results
        if flag_save_in_file:
            save_result_file_path_name = f'{rw_result_file_path}{comparison_result_name_prefix}_comparison_results_writes.csv'
        else:
            save_result_file_path_name = ""

        statistics=markdown_table_detailed_1(contract_evaluation_write_result, "",
                                  "", "",
                                  task_name="writes",
                                  output_result_path_name=save_result_file_path_name)

    return statistics
