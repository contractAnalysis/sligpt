import os

import markdown2
# from weasyprint import HTML
import pandas as pd
from tabulate import tabulate

from sligpt.config import color_prefix
from sligpt.data_presentation.utils_presentation import present_as_markdown_table

bold="\033[1m"


name__category_to_text={
        "state_variable_names":"State variable names",
        "modifier_names":"Modifier names",
        "event_names":"Event names",
        "function_names":"Function names"
    }


def markdown_table_general(data:dict,object:str,solidity_file_name:str="",contract_name:str="",task_name:str=""):
    """

    :param data: {"expected":[],"success":[],"failure":[],"other":[],"precision": 2/3,"recall":1/3,accuracy:x/3}
    :param object: from which the results belong to
    :param solidity_file_name: useful to know which solidity file the results belong to
    :param contract_name: useful to know which contract the results belong to
    :return:
    """

    # print contract data info
    if len(solidity_file_name) > 0:
        before_title = "\n==== {}:{} ({}) ====".format(solidity_file_name, contract_name,task_name)
    else:
        before_title = ""

    # check the case when no data is given
    if len(data) == 0:
        title = "{}\n##  {}{}{}: No results.".format(
            before_title,
            color_prefix["Magenta"],
            object,
            color_prefix["Gray"],
        )
        print(title)
        return

    header = ['Category', 'Result']
    header = ["{}{}{}".format(bold, item, color_prefix['Gray']) for item in header]
    data_present = [
        ["Success", data['success']],
        ["Failure", data['failure']],
        ["Other", data['other']],
    ]

    title = "{}\n {}{}{}: precision: {}{}{}; recall: {}{}{}; accuracy: {}{}{}".format(
        before_title,
        color_prefix["Magenta"],
        object,
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{data["precision"]}',
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{data["recall"]}',
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{data["accuracy"]}',
        color_prefix["Gray"],
    )

    present_as_markdown_table(data_present, header=header, title=title)


def markdown_table_detailed(data:dict,object:str,solidity_file_name:str="",contract_name:str="",task_name:str=""):
    """

    :param data: {category1:{"expected":[],"success":[],"failure":[],"other":[],"precision": 2/3,"recall":1/3,accuracy:x/3},...}
    :param object:
    :param solidity_file_name:
    :param contract_name:
    :param task_name:
    :return:
    """

    # print contract data info
    if len(solidity_file_name) > 0:
        before_title = "\n==== {}:{} ({}) ====".format(solidity_file_name, contract_name,task_name)
    else:
        before_title = ""

    if len(data) == 0:
        title = "{}\n## {}{}{}: No results.".format(
            before_title,
            color_prefix["Magenta"],
            object,
            color_prefix["Gray"],
        )
        print(title)
        return

    header = ['No','Name','status', 'target','Success', 'Failure', 'Other', 'Precision', 'Recall', 'Accuracy']
    header=["{}\n{}{}{}".format(before_title,bold,item,color_prefix['Gray']) for item in header]

    data_present = []
    precision_data = [0, 0]
    recall_data = [0, 0]
    accuracy_data = [0, 0]

    index=0
    for category in ['success','failure','other']:
        for results_dict in data[category]:
            for key,value_dict in results_dict.items():
                try:
                    if key=='name':continue
                    index+=1
                    each_data=[
                        index,
                        "{}{}{}".format(color_prefix['Blue'],results_dict['name'],color_prefix['Gray']),
                        category,  # the status of the state variable, modifier, or function
                        "{}{}{}".format(color_prefix['Cyan'],key,color_prefix['Gray']),# the component of a state variable, modifier, or funcion
                        "{}{}{}".format(color_prefix['Green'],value_dict['success'],color_prefix['Gray']), # the successfully identified results on the component of a state variable, modifier, or function.
                        "{}{}{}".format(color_prefix['Red'],value_dict['failure'],color_prefix['Gray']),
                        "{}{}{}".format(color_prefix['Yellow'],value_dict['other'],color_prefix['Gray']),  # something that does not exist.
                        value_dict['precision'],
                        value_dict['recall'],
                        value_dict['accuracy']
                    ]

                    data_present+=[each_data]

                    if "/" in str(value_dict['precision']):
                        precision_items = str(value_dict['precision']).split("/")
                        precision_data = [value + int(item) for value, item in zip(precision_data, precision_items)]

                        recall_items = str(value_dict['recall']).split("/")
                        recall_data = [value + int(item) for value, item in zip(recall_data, recall_items)]

                        accuracy_items = str(value_dict['accuracy']).split("/")
                        accuracy_data = [value + int(item) for value, item in zip(accuracy_data, accuracy_items)]

                except TypeError as e:
                    print(f'{e}')


    title = "{}{}{}: precision: {}{}{}; recall: {}{}{}; accuracy: {}{}{}".format(
        color_prefix["Magenta"],
        object,
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{precision_data[0]}/{precision_data[1]}',
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{recall_data[0]}/{recall_data[1]}',
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{accuracy_data[0]}/{accuracy_data[1]}',
        color_prefix["Gray"],
    )

    present_as_markdown_table(data_present, header=header, title=title)


def markdown_table_detailed_1(data:dict,object:str,solidity_file_name:str="",contract_name:str="",task_name:str="", output_result_path_name:str=""):
    """

    :param data: {category1:{"expected":[],"success":[],"failure":[],"other":[],"precision": 2/3,"recall":1/3,accuracy:x/3},...}
    :param object:
    :param solidity_file_name:
    :param contract_name:
    :param task_name:
    :return:
    """
    data_to_output=[]
    # print contract data info
    if len(solidity_file_name) > 0:
        before_title = "\n==== {}:{} ({}) ====".format(solidity_file_name, contract_name,task_name)
    else:
        before_title = ""

    if len(data) == 0:
        title = "{}\n## {}{}{}: No results.".format(
            before_title,
            color_prefix["Magenta"],
            object,
            color_prefix["Gray"],
        )
        print(title)
        return

    if task_name in ['name detection']:
        header = ['No','category','Success', 'Failure', 'Other', 'Precision', 'Recall', 'Accuracy']
    else:
        header = ['No', 'modifier or function bane', 'Success', 'Failure', 'Other', 'Precision',
                  'Recall', 'Accuracy']
    header=["{}{}{}".format(bold,item,color_prefix['Gray']) for item in header]

    data_present = []
    precision_data = [0, 0]
    recall_data = [0, 0]
    accuracy_data = [0, 0]

    index=0
    for category,results_dict in data.items():
        try:

            index += 1
            each_data = [
                index,
                "{}{}{}".format(color_prefix['Blue'],name__category_to_text[category] if category in name__category_to_text else category,
                                color_prefix['Gray']),

                # the component of a state variable, modifier, or funcion
                "{}{}{}".format(color_prefix['Green'], results_dict['success'],
                                color_prefix['Gray']),
                # the successfully identified results on the component of a state variable, modifier, or function.
                "{}{}{}".format(color_prefix['Red'], results_dict['failure'],
                                color_prefix['Gray']),
                "{}{}{}".format(color_prefix['Yellow'], results_dict['other'],
                                color_prefix['Gray']),
                # something that does not exist.
                results_dict['precision'],
                results_dict['recall'],
                results_dict['accuracy']
            ]

            data_present += [each_data]
            data_to_output.append([index,
                                   name__category_to_text[category] if category in name__category_to_text else category,
                                   results_dict['success'],
                                   results_dict['failure'],
                                   results_dict['other'],
                                   f'{str(results_dict["precision"])}',
                                   f'{str(results_dict["recall"])}',
                                   f'{str(results_dict["accuracy"])}'
                                   ])

            # get accumulated results
            if "/" in str(results_dict['precision']):
                precision_items = str(results_dict['precision']).split("/")
                precision_data = [value + int(item) for value, item in
                                  zip(precision_data, precision_items)]

                recall_items = str(results_dict['recall']).split("/")
                recall_data = [value + int(item) for value, item in
                               zip(recall_data, recall_items)]

                accuracy_items = str(results_dict['accuracy']).split("/")
                accuracy_data = [value + int(item) for value, item in
                                 zip(accuracy_data, accuracy_items)]

        except TypeError as e:
            print(f'{e}')



    title = "{}\n{}{}{}: precision: {}{}{}; recall: {}{}{}; accuracy: {}{}{}".format(
        before_title,
        color_prefix["Magenta"],
        object,
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{precision_data[0]}/{precision_data[1]}',
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{recall_data[0]}/{recall_data[1]}',
        color_prefix["Gray"],
        color_prefix["Green"],
        f'{accuracy_data[0]}/{accuracy_data[1]}',
        color_prefix["Gray"],
    )
    data_to_output.append(["","","","","",f'{precision_data[0]}/{precision_data[1]}', f'{recall_data[0]}/{recall_data[1]}',f'{accuracy_data[0]}/{accuracy_data[1]}'])

    if len(output_result_path_name)>0:
        df = pd.DataFrame(data_to_output)

        if task_name in ['name detection']:
            df.columns=['No','Category','Success','Failure','Other','Precision','Recall','Accuracy']
        else:
            df.columns = ['No', 'modifier or function bane', 'Success', 'Failure',
                      'Other', 'Precision',
                      'Recall', 'Accuracy']


        df['Precision'] = df['Precision'].astype(str)
        df['Recall'] = df['Recall'].astype(str)
        df['Accuracy'] = df['Accuracy'].astype(str)
        df.to_csv(output_result_path_name,index=False)
    present_as_markdown_table(data_present, header=header, title=title)
    return [precision_data,recall_data,accuracy_data]






