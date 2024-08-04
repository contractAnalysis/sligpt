import logging
import os

from daconx.solc_compile import get_ast_nodes
from daconx.traverse_data_collection import contract_level_data_collection,  contract_detailed_data_collection, output_contract_level_data
from daconx.utils import dump_to_json



logger=logging.getLogger(__name__)


def get_contract_data(solidity_file_path:str,solidity_file_name:str,contract_name:str,solc_version:str,contract_data_path:str=""):
    """
    apply daconx to collect contract data.
    :param solidity_file_path:
    :param solidity_file_name:
    :param contract_name:
    :param solc_version:
    :param contract_data_path:
    :return:
    """
    # compile to get ast nodes and the file content that solc compiles from it
    try:
        nodes, solidity_file_content = get_ast_nodes(solidity_file_path, solidity_file_name, solc_version)
    except Exception as e:
        print(f'Exception: {e}')
        return {},{}
    # collect contract level data
    contract_level_info = contract_level_data_collection(nodes, solidity_file_content)

    # for each contract, collect more data
    contract_detailed_data = contract_detailed_data_collection(solidity_file_name, solc_version, contract_level_info,
                                                               solidity_file_content)
    if len(contract_data_path)>0:
        if os.path.exists(contract_data_path):
            path = "{}{}_{}_{}.json".format(contract_data_path, solidity_file_name,contract_name, "contract_level_data")
            output_contract_level_data(contract_level_info, path)

            for con_name, contractInfo in contract_detailed_data.items():
                path="{}{}_{}_{}.json".format(contract_data_path,solidity_file_name,contract_name,"contract_detailed_data")
                dump_to_json(contractInfo,path)
        else:
            logger.info(f'{contract_data_path} does not exist.')

    return contract_level_info,contract_detailed_data














