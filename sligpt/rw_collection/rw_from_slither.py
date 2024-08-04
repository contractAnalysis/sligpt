import os

import solcx
from slither import Slither
from slither.core.declarations import Contract
from slither.core.variables import StateVariable

from sligpt.utils import dump_json_object_to_json, load_a_json_file

import logging

from sligpt.evaluation.evaluate import result_statistics_from_2_json_files

logger=logging.getLogger(__name__)



def get_contract_from_slither(solidity_file_path:str,solidity_file_name:str,contract_name:str, solc_version:str=""):

    if len(solc_version)==0:
        solc_version="0.4.24"

    if solc_version not in solcx.get_installed_solc_versions():
        solcx.install_solc(solc_version)
    solcx.set_solc_version(solc_version)

    solc_path = str(solcx.get_solcx_install_folder()) + "\solc-v{}\solc.exe".format(solc_version)
    if not os.path.exists(solc_path):
        logger.error(f"Does not exist: {solc_path}")
        print(f"Does not exist: {solc_path}")
        return None
    solidity_file_path_name=solidity_file_path+solidity_file_name

    if os.path.exists(solidity_file_path_name):
        try:
            contract=None
            # Init slither
            slither = Slither(solidity_file_path_name, solc=solc_path)

            # Get the contract
            contracts = slither.get_contract_from_name(contract_name=contract_name)
            assert len(contracts) == 1
            contract = contracts[0]

        except:
            print('have exception when getting slither contract')
        finally:
            return contract
    else:
        logger.error(f"Does not exist: {solidity_file_path_name}")
        print(f"Does not exist: {solidity_file_path_name}")
        return None



class FuncDependency():
    """
    consider all state variables and functions (i.e., including state variables and functions from base contracts)
    """
    def __init__(self,contract:Contract):
        self.contract = contract
        self.func_r_w_data={}
        self.function_dependency_dict={}
        self.function_dependency_list=[]
        self.involved_functions=[]

        self.state_variables={}
        self.function_code={}
        self.function_code_meta={} # save the function names that are used by each function
        self.constructors={}


    def get_function_r_w_data(self):
        """
        get the state variables read in conditions and written by functions
        :return:
        """
        sv_names =list(self.state_variables.keys())
        # for sv in self.contract.state_variables:
        #     sv_names.append(sv.name)
        # print(f'state variables:{sv_names}')

        for function in self.contract.functions:
            # do not consider constructor
            if function.is_constructor:  continue

            # only consider public and external functions which can be invoked by users.
            if function.visibility not in ['public', 'external']: continue

            # do not consider the functions of public state variables
            pure_name = function.name
            if pure_name in sv_names: continue

            sv_read_in_condition_1 = function.all_conditional_state_variables_read()
            sv_read_in_condition_1_0 = [sv.name for sv in sv_read_in_condition_1]

            sv_written = [sv.name for sv in function.all_state_variables_written()]

            self.func_r_w_data[function.canonical_name] = {
                "state_variables_read_in_BC": sv_read_in_condition_1_0,
                "state_variables_written": sv_written,
                "modifiers": [modifier.name for modifier in function.modifiers]
            }


    def get_function_dependency(self):
        """
        collect all functions.
         if a function name appear in the target contract and the parent contracts, then only consider the function in the target contract. The assumption is that when the function is the target contract would override the function in the parent contracts.
        :return:
        """

        for function_from,func_data_from in self.func_r_w_data.items():
            self.function_dependency_dict[function_from]={}

            sv_written=func_data_from['state_variables_written']

            for function_to, func_data_to in self.func_r_w_data.items():
                sv_read=func_data_to['state_variables_read_in_BC']
                share_sv=[item for item in sv_written if item in sv_read]
                if len(share_sv)>0:
                    self.function_dependency_dict[function_from][function_to]=share_sv
                    for sv in share_sv:
                        if [function_from,function_to,sv] not in self.function_dependency_list:
                            self.function_dependency_list.append([function_from,function_to,sv])
                    if function_from not in self.involved_functions:
                        self.involved_functions.append(function_from)
                    if function_to not in self.involved_functions:
                        self.involved_functions.append(function_to)


    def get_function_code(self):
        """
        modifiers are also treated as functions
        :return:
        """
        for modifier in self.contract.modifiers:
            self.function_code[modifier.canonical_name]={"parameters":modifier.parameters,
                                                         "code":modifier.source_mapping.content}
        for function in self.contract.functions:
            if function.is_constructor:
                if function.name not in self.constructors.keys():
                    self.constructors[function.name] = {"parameters": function.parameters,
                                                        "code": function.source_mapping.content}
                else:
                    print(f'constructor name is already encountered:{function.name}. More than two constructors?')
            else:
                self.function_code[function.canonical_name]={"parameters":function.parameters,"code":function.source_mapping.content}
                self.function_code_meta[function.canonical_name]=[]
                for modifier in function.modifiers:
                    self.function_code_meta[function.canonical_name].append(modifier.canonical_name)

                # to-do: add external call

    def get_state_variables(self):
        def sv_value(sv:StateVariable):
            type=sv.type.__str__()
            if not sv.initialized:
                if '[]' in type:
                    return '[]'
                elif 'mapping' in type:
                    return "{}"
                elif type in ['address','string','bytes']:
                    return ""
                elif 'int' in type:
                    return 0
                elif type in ['bool']:
                    return 'false'

                else:
                    return ""
            else:
                return sv.expression.source_mapping.content

        state_variables=self.contract.state_variables
        for sv in self.contract.all_state_variables_read+self.contract.all_state_variables_written:
            if sv not in state_variables:
                state_variables.append(sv)
        for sv in state_variables:
            self.state_variables[sv.name]={
                "name":sv.name,
                "type":sv.type.__str__(),
                "initial_value":sv_value(sv),
                "is_constant":"{}".format(sv.is_constant)
            }

    def prepare_data(self):
        self.get_state_variables()
        self.get_function_r_w_data()
        self.get_function_dependency()
        self.get_function_code()

    def output_function_pairs(self, result_path:str, name_prefix:str,start_index:int=0,contract_info:dict={}):
        index=start_index
        for func_d_list in self.function_dependency_list:
            assert len(func_d_list)==3

            related_functions_1=self.function_code_meta[func_d_list[0]]
            related_functions_2=self.function_code_meta[func_d_list[1]]
            union_functions=list(set(related_functions_1+related_functions_2))
            dependent_code=""
            for name in union_functions:
                dependent_code+=self.function_code[name]['code']


            index += 1
            id= "{}_{}".format(name_prefix,index)
            json_data={
                "id":id,
                "solidity_file_path":contract_info['solidity_file_path'],
                "solidity_file_name":contract_info['solidity_file_name'],
                "contract_name":contract_info['contract_name'],
                "solc_version":contract_info['solc_version'],
                "function1_name":func_d_list[0],
                "function2_name":func_d_list[1],
                "state_variable":func_d_list[2],
                "all_state_variables":self.state_variables,
                "function1_code":self.function_code[func_d_list[0]]['code'],
                "function2_code":  "same code as {}".format(func_d_list[0]) if func_d_list[1]==func_d_list[0] else self.function_code[func_d_list[1]]['code'],

                "dependent_code":dependent_code,
                "constructors":{ name:value["code"] for name,value in self.constructors.items()}
            }

            result_path_name=result_path+id+".json"
            dump_json_object_to_json(json_data, result_path_name,indent = 4)

        return index


def get_function_rw_data_slither(solidity_file_path:str,solidity_file_name:str,contract_name:str,solc_version:str)->dict:


    contract = get_contract_from_slither(solidity_file_path,
                                         solidity_file_name, contract_name,
                                         solc_version)

    funD = FuncDependency(contract)
    funD.get_state_variables()
    funD.get_function_r_w_data()
    return funD.func_r_w_data,funD.state_variables






def obtain_rw_data_slither(contract_info:list, solidity_file_path:str,rw_data_path:str):

    contract_rw_data_slither={}
    for con_info in contract_info:
        solidity_file_name = con_info[0]
        contract_name = con_info[1]
        solc_version = con_info[2]

        key=f'{solidity_file_name}{contract_name}'

        function_rw_data, state_variables = get_function_rw_data_slither(
            solidity_file_path,
            solidity_file_name, contract_name,
            solc_version)
        contract_rw_data_slither[key]=function_rw_data
        contract_rw_data_slither[key]["stateVariables"] = state_variables

    # save the rw data
    dump_json_object_to_json(contract_rw_data_slither,
                             f'{rw_data_path}contract_rw_data_slither.json')


def result_statistics(rw_result_file_path:str, slither_rw_data_json:str, gt_rw_data_json:str, flag_read:bool=True):
    # ================================
    # evaluate

    result_statistics_from_2_json_files(rw_result_file_path, slither_rw_data_json, gt_rw_data_json, "slither_and_gt", flag_read=flag_read)



if __name__=="__main__":
    parameters = [
        ["HoloToken.sol", "HoloToken", "0.4.18", [], ""],
        ["0x89f9749ce943281b8c65fec7f15e126f8cf4edb1.sol", "DepositGame",
         "0.4.25"],  # 1
        ["0x822d7b7f27713598e7e19410257e80517916032c.sol", "StandardERC20Token",
         "0.5.12"],  # 2
        ["0x2600004fd1585f7270756ddc88ad9cfa10dd0428.sol", "GemJoin5",
         "0.5.12"],  # 3
        ["0x38ca0421e2ba6ffc1920ec11d93c3da2b15e4131.sol", "SirotTokenICO",
         "0.6.0"],  # 7-3
        ["0x4c969A8Fe3e79Ce8AEB9f40E4406385A36c11112.sol", "simpleToken",
         "0.4.21"],  # 8-3
        ["0x1b80c5d3a76176c7119558a6b4b250a6421e893b.sol", "PiggericksShop",
         "0.5.8"],  # 9-3
        ["0xdb6bcae929767e657884b03974c849d46352cde4.sol", "ERC20Latte",
         "0.5.0"],  # 10-3
        ["0x95a6a3f44a70172e7d50a9e28c85dfd712756b8c.sol", "SynthSummaryUtil",
         "0.4.25"],  # 11-3
        ["0xe4c154be0b17359527a25e6ab45b7ce86c8795c7.sol","digitalNotary","0.6.4"],#12-3
    ]
    # obtain_rw_data_slither(parameters,"../../datasets/rw_contracts/","../../results/rw_results/")



    # result_statistics("../../results/rw_results/","contract_rw_data_slither.json","contract_rw_data_gt.json")









