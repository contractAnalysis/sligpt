def clean_state_variable_names(sv_list:list)->list:
    results=[]
    for item in sv_list:
        if '[' not in item:
            results.append(item)
        else:
            results.append(str(item).split('[')[0].strip())

    # results=[item if "[" not in item else str(item).split('[')[0].strip() for item in sv_list]
    # return list(set(results)) # this can change the order of elements while the order should not be changed.
    return results


def sv_list_clean(sv_name_list: list,state_variables:list) -> list:
    results = []
    for item in sv_name_list:
        if '[' not in item:
            results.append(item)
        else:
            results.append(str(item).split('[')[0].strip())
            # example case: balances[destroyer]
            rest_part=item[item.index('['):]
            for sv in state_variables:
                if sv in rest_part:
                    results.append(sv)
    return list(set(results))


def convert_tuple_to_str(data):
    # there are cases that a str type of field is converted to a tuple of size 1
    return data[0] if isinstance(data, tuple) else data

def none_value_handle(data,type:str):
    """
    used to handle the actual data. It is possible that no data is collected.
    :param data:
    :param type:
    :return:
    """
    if type=='list':
        if data is None:
            return []
        else: return data
    elif type=='str':
        if data is None:
            return ""
        else: return data
    else:
        print(f'strange value not list and str: {data}')
        return data

def remove_string_space(str_data:str)->str:
    str_data.replace("\n","")
    output_string = ''.join([char for char in str_data if char != ' '])
    return output_string