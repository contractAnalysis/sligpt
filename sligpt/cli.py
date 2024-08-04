import argparse
import logging
import os

import sligpt.config

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sligpt.config.project_path=f'{get_project_root()}/'


from sligpt.config import rw_contracts_info, contract_index, dataset_path, \
    result_path, \
    contract_data_path, dataset_solidity_path, GPT4_model
from sligpt.evaluation.evaluate import result_statistics_from_2_json_files
from sligpt.get_contract_data import get_contract_data
from sligpt.rw_collection.rw_from_gpt import get_rw_data_from_gpt_one_contract
from sligpt.rw_collection.rw_from_sligpt import \
    obtain_rw_data_sligpt_for_a_contract, obtain_rw_data_sligpt_for_a_function
from sligpt.rw_collection.rw_from_slither import get_function_rw_data_slither
from sligpt.utils import get_a_kv_pair_from_a_json, \
    write_a_kv_pair_to_a_json_file


def register_basic_arguments(parser: argparse.ArgumentParser):

    parser.add_argument('--solidity_file_name', type=str,
                        default=rw_contracts_info[contract_index][0])
    parser.add_argument('--contract_name', type=str,
                        default=rw_contracts_info[contract_index][1])
    parser.add_argument('--solc_version', type=str,
                        default=rw_contracts_info[contract_index][2])
    parser.add_argument('--log_level', type=int, default=3)
    parser.add_argument('--function', type=str, default="")
    parser.add_argument('--task', type=str, default="dependency,slither",
                        help="specify the task",
                        choices = ['dependency,slither','dependency,gpt4','dependency,sligpt','function_dependency,sligpt', 'contract_data',"statistics"])


    parser.add_argument('--dataset_path', type=str, default=dataset_path)
    parser.add_argument('--solidity_file_path', type=str, default=dataset_solidity_path)
    parser.add_argument('--result_path', type=str, default=result_path)
    parser.add_argument('--contract_data_path', type=str,
                        default=contract_data_path)

    parser.add_argument('--contract_info_csv_name', type=str,default="",
                        help="the name of the csv file containing contract info.")

    parser.add_argument('--contract_info_file_name', type=str,default="",
                        help="the name of the json file containing contract info.")

    parser.add_argument('--contract_info_file_path', type=str,default="",
                        help="the path of the json file containing contract info.")

    parser.add_argument('--contract_info_json_keys', type=str, default="",
                        help="the keys to get contract info.")

    parser.add_argument('--json_rw_file', type=str, default="",
                        help="the json file containing the rw data")
    parser.add_argument('--json_rw_gt', type=str, default="",
                        help="the json file containing the rw data")
    return parser



def register_openai_arguments(parser:argparse.ArgumentParser):
    parser.add_argument('--engine', default=GPT4_model, choices=[
        "gpt-3.5-turbo-0301",GPT4_model])
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--prompt_file_name', type=str, default="",
                        help="specify the name of the file containing prompts.")
    parser.add_argument('--prompt_keys', type=str, default="",
                        help="specify the keys to retrieve prompt content.")
    return parser


def set_logging_level(args):
    if args.log_level==4:
        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )
    elif args.log_level==5:
        logging.basicConfig(
            level=logging.ERROR,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )
    elif args.log_level == 3:
        logging.basicConfig(
            level=logging.WARNING,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',
            # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )


def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        description="A simple script with command-line arguments.")

    parser = register_basic_arguments(parser)
    parser = register_openai_arguments(parser)

    # Parse the command-line arguments
    args = parser.parse_args()
    set_logging_level(args)

    results={}
    if args.task == 'dependency,gpt4':

        key=f'{args.solidity_file_name}{args.contract_name}'
        # --------------------------------
        # check if rw data from Slither
        json_file_path = f'{args.result_path}contract_rw_data_slither.json'
        saved_value = get_a_kv_pair_from_a_json(json_file_path, key)
        if len(saved_value)==0:
            func_r_w_data, state_variables = get_function_rw_data_slither(
                args.solidity_file_path,
                args.solidity_file_name,
                args.contract_name,
                args.solc_version
            )
            func_r_w_data["stateVariables"] = state_variables
            write_a_kv_pair_to_a_json_file(json_file_path, key, func_r_w_data)

        #--------------------------------
        # check if there are contract data
        path = "{}{}_{}_{}.json".format(contract_data_path,
                                        args.solidity_file_name,
                                        args.contract_name,
                                        "contract_detailed_data")
        if not os.path.exists(path):
            get_contract_data(
                args.solidity_file_path,
                args.solidity_file_name,
                args.contract_name,
                args.solc_version,
                args.contract_data_path
            )

        results=get_rw_data_from_gpt_one_contract(
            args.solidity_file_name,
            args.contract_name,
            args.contract_data_path,
            args.result_path,
            "contract_rw_data_slither.json"
        )


    elif args.task == 'dependency,slither':
        key = f'{args.solidity_file_name}{args.contract_name}'
        json_file_path=f'{args.result_path}contract_rw_data_slither.json'
        saved_value = get_a_kv_pair_from_a_json(json_file_path, key)
        results=saved_value
        if len(saved_value)==0:
            func_r_w_data,state_variables=get_function_rw_data_slither(
                args.solidity_file_path,
                 args.solidity_file_name,
                 args.contract_name,
                 args.solc_version
            )
            func_r_w_data["stateVariables"]=state_variables
            write_a_kv_pair_to_a_json_file(json_file_path, key, func_r_w_data)
            results=func_r_w_data
        else:
            print(f"The data of {key} are collected.")



    elif args.task == 'dependency,sligpt':
        key = f'{args.solidity_file_name}{args.contract_name}'
        # --------------------------------
        # check if rw data from Slither
        json_file_path = f'{args.result_path}contract_rw_data_slither.json'
        saved_value = get_a_kv_pair_from_a_json(json_file_path, key)
        if len(saved_value) == 0:
            func_r_w_data, state_variables = get_function_rw_data_slither(
                args.solidity_file_path,
                args.solidity_file_name,
                args.contract_name,
                args.solc_version
            )
            func_r_w_data["stateVariables"] = state_variables
            write_a_kv_pair_to_a_json_file(json_file_path, key, func_r_w_data)

        # --------------------------------
        # check if there are contract data
        path = "{}{}_{}_{}.json".format(contract_data_path,
                                        args.solidity_file_name,
                                        args.contract_name,
                                        "contract_detailed_data")
        if not os.path.exists(path):
            get_contract_data(
                args.solidity_file_path,
                args.solidity_file_name,
                args.contract_name,
                args.solc_version,
                args.contract_data_path
            )

        results=obtain_rw_data_sligpt_for_a_contract(
            args.solidity_file_name,
            args.contract_name,
            args.contract_data_path,
            args.result_path,
            "contract_rw_data_slither.json"
        )

    elif args.task == 'function_dependency,sligpt':
        if len(args.function)==0:
            print(f'Please provide the function name.')
            exit()

        key = f'{args.solidity_file_name}{args.contract_name}'
        # --------------------------------
        # check if rw data from Slither
        json_file_path = f'{args.result_path}contract_rw_data_slither.json'
        saved_value = get_a_kv_pair_from_a_json(json_file_path, key)
        if len(saved_value) == 0:
            func_r_w_data, state_variables = get_function_rw_data_slither(
                args.solidity_file_path,
                args.solidity_file_name,
                args.contract_name,
                args.solc_version
            )
            func_r_w_data["stateVariables"] = state_variables
            write_a_kv_pair_to_a_json_file(json_file_path, key, func_r_w_data)

        # --------------------------------
        # check if there are contract data
        path = "{}{}_{}_{}.json".format(contract_data_path,
                                        args.solidity_file_name,
                                        args.contract_name,
                                        "contract_detailed_data")
        if not os.path.exists(path):
            get_contract_data(
                args.solidity_file_path,
                args.solidity_file_name,
                args.contract_name,
                args.solc_version,
                args.contract_data_path
            )

        results=obtain_rw_data_sligpt_for_a_function(
            args.solidity_file_name,
            args.contract_name,
            args.function,
            args.contract_data_path,
            args.result_path,
            "contract_rw_data_slither.json"
        )

    elif args.task == 'contract_data':
        path="{}{}_{}_{}.json".format(contract_data_path,args.solidity_file_name,args.contract_name,"contract_detailed_data")
        if not os.path.exists(path):
            get_contract_data(
                args.solidity_file_path,
                args.solidity_file_name,
                args.contract_name,
                args.solc_version,
                args.contract_data_path
            )
        else:
            key=f'{args.solidity_file_name}{args.contract_name}'
            print(f'the data of {key} are collected.')

    elif args.task=='statistics':
        json_file=args.json_rw_file
        json_gt=args.json_rw_gt

        if os.path.exists(f'{args.result_path}{json_file}') and \
                os.path.exists(f'{args.result_path}{json_gt}'):

            result_statistics_from_2_json_files(args.result_path, json_file, json_gt, "file1_file2", flag_read=True)
        else:
            print(f'Files not found:{args.result_path}{json_file}\n{args.result_path}{json_gt}')
    else:
        print(f'{args.task} is not implemented yet.')

    if results is not None and len(results)>0:
        if isinstance(results,dict):
            for k,v in results.items():
                print(f'{k}')
                print(f'\t{v}')
    exit()
