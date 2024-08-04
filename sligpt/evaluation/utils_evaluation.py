from sligpt.evaluation.utils_x import remove_string_space, \
    clean_state_variable_names


def evaluate_list_pair_as_elements(actual_pair_list:list, expected_pair_list:list):
    try:

        actual_str_list=[ele_str for (ele_str,_) in actual_pair_list]
        expected_list = [ele for (_,ele) in expected_pair_list]
        expected_str_list=[ele_str for (ele_str,_) in expected_pair_list]
        results = {'expected': expected_list}
        results['success'] =  list(set([ele for (ele_str,ele) in actual_pair_list if ele_str in expected_str_list]))
        results['failure'] =  list(set([ele for (ele_str,ele) in expected_pair_list if ele_str not in actual_str_list]))
        results['other'] =  list(set([ele for (ele_str,ele) in actual_pair_list if ele_str not in expected_str_list]))
        TP = len(results["success"])
        FP = len(results["other"])
        TN = 0
        FN = len(results['failure'])
        metric_results = metric_values(TP, TN, FP, FN)
        results["precision"] = metric_results["precision"]
        results["recall"] = metric_results["recall"]
        results["accuracy"] = metric_results["accuracy"]
        return results
    except TypeError as e:
        print(f'{e} in evaluate_list() evaluation')


def evaluate_list(actual_list:list, expected_list:list):
    try:
        actual_space_removed_list=[remove_string_space(item) for item in actual_list]
        expected_space_removed_list = [remove_string_space(item) for item in expected_list]
        results = {'expected': expected_list}
        results['success'] =  list(set([ele for ele_space_removed,ele in zip(actual_space_removed_list,actual_list) if ele_space_removed in expected_space_removed_list]))
        results['failure'] =  list(set([ele for ele_space_removed,ele in zip(expected_space_removed_list,expected_list) if ele_space_removed  not in actual_space_removed_list]))
        results['other'] =  list(set([ele for ele_space_removed,ele in zip(actual_space_removed_list,actual_list) if ele_space_removed not in expected_space_removed_list]))
        TP = len(results["success"])
        FP = len(results["other"])
        TN = 0
        FN = len(results['failure'])
        metric_results = metric_values(TP, TN, FP, FN)
        results["precision"] = metric_results["precision"]
        results["recall"] = metric_results["recall"]
        results["accuracy"] = metric_results["accuracy"]
        return results
    except TypeError as e:
        print(f'{e} in evaluate_list() evaluation\n actual list: {actual_space_removed_list}\n expected list: {expected_space_removed_list}')


def evaluate_name_list(actual_list:list, expected_list:list):
    try:
        actual_pure_name_list=clean_state_variable_names(actual_list)
        expected_pure_name_list = clean_state_variable_names(expected_list)
        results = {'expected': expected_list}
        results['success'] = list(set([ele for ele_pure_name,ele in zip(actual_pure_name_list,actual_list) if ele_pure_name in expected_pure_name_list]))
        results['failure'] = list(set([ele for ele_pure_name,ele in zip(expected_pure_name_list,expected_list) if ele_pure_name  not in actual_pure_name_list]))
        results['other'] = list(set([ele for ele_pure_name,ele in zip(actual_pure_name_list,actual_list) if ele_pure_name not in expected_pure_name_list]))
        TP = len(results["success"])
        FP = len(results["other"])
        TN = 0
        FN = len(results['failure'])
        metric_results = metric_values(TP, TN, FP, FN)
        results["precision"] = metric_results["precision"]
        results["recall"] = metric_results["recall"]
        results["accuracy"] = metric_results["accuracy"]
        return results
    except TypeError as e:
        print(f'{e} in evaluate_list() evaluation\n actual list: {actual_pure_name_list}\n expected list: {expected_pure_name_list}')
        return {}

def evaluate_condition_list(actual_list:list, expected_list:list):
    def is_contained(condition_list:list,condition):

        for condi in condition_list:
            if condition in condi:
                return True
            elif condi in condition:
                return True
        return False
    try:
        actual_condition_no_space_list=[remove_string_space(item) for item in actual_list]
        expected_condition_no_space_list=[remove_string_space(item) for item in expected_list]
        actual_pure_name_list=clean_state_variable_names(actual_list)
        expected_pure_name_list = clean_state_variable_names(expected_list)
        results = {'expected': expected_list}
        results['success'] = [condi for condi_no_space,condi in zip(actual_condition_no_space_list,actual_list) if is_contained(expected_condition_no_space_list,condi_no_space)]
        results['failure'] = [condi for condi_no_space,condi in zip(expected_condition_no_space_list,expected_list) if not is_contained(actual_condition_no_space_list,condi_no_space)]
        results['other'] = [condi for condi_no_space,condi in zip(actual_condition_no_space_list,actual_list) if not is_contained(expected_condition_no_space_list,condi_no_space)]
        TP = len(results["success"])
        FP = len(results["other"])
        TN = 0
        FN = len(results['failure'])
        metric_results=metric_values(TP,TN,FP,FN)
        results["precision"] = metric_results["precision"]
        results["recall"] = metric_results["recall"]
        results["accuracy"] = metric_results["accuracy"]
        return results
    except TypeError as e:
        print(f'{e} in evaluate_list() evaluation\n actual list: {actual_pure_name_list}\n expected list: {expected_pure_name_list}')
        return {}

def metric_values(TP:int=0,TN:int=0,FP:int=0,FN:int=0):
    return {
        "precision":f'{TP}/{TP + FP}',
        "recall":f'{TP}/{TP + FN}',
        "accuracy":f'{TP + TN}/{TP + FP + FN + TN}'
    }

def evaluate_initial_value_list(actual_list:list, expected_list:list):
    try:
        actual_normalized_list=['NULL'if len(item)==0 else item for item in actual_list]
        expected_normalized_list =['NULL'if len(item)==0 else item for item in expected_list]
        results = {'expected': expected_list}
        results['success'] = list(set([ele_ for ele_,ele in zip(actual_normalized_list,actual_list) if ele_ in expected_normalized_list]))
        results['failure'] = list(set([ele_ for ele_,ele in zip(expected_normalized_list,expected_list) if ele_  not in actual_normalized_list]))
        results['other'] = list(set([ele_ for ele_,ele in zip(actual_normalized_list,actual_list) if ele_ not in expected_normalized_list]))
        TP = len(results["success"])
        FP = len(results["other"])
        TN = 0
        FN = len(results['failure'])
        results["precision"] = f'{TP}/{TP + FP}'
        results["recall"] = f'{TP}/{TP + FN}'
        results["accuracy"] = f'{TP + TN}/{TP + FP + FN + TN}'
        return results
    except TypeError as e:
        print(f'{e} in evaluate_list() evaluation\n actual list: {actual_normalized_list}\n expected list: {expected_normalized_list}')
