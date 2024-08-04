
project_path="./"
dataset_path= project_path+"datasets\\"
result_path= project_path+"results\\"
prompt_path= project_path+"sligpt\\prompts\\"
contract_data_path= project_path+"results\\contract_data\\"

dataset_solidity_path=dataset_path+"rw_contracts\\"





# ChatGPT_model="gpt-3.5-turbo-0301"  # the response format is more flexible
# ChatGPT_model="gpt-4-1106-preview"
GPT4_model= "gpt-4o-2024-05-13"
sleep_time=20 # the time between two requests sent to GPT-4o to prevent from crowding GPT-4o
evaluation_loops=4

# dataset_solidity_path="C:\\Users\\18178\\PycharmProjects\\code_understanding\\dataset\\temp\\governance_contracts\\"


color_prefix={
"Black": "\033[30m",
"Red": "\033[31m",
"Green": "\033[32m",
"Yellow": "\033[33m",
"Blue": "\033[34m",
"Magenta": "\033[35m",
"Cyan": "\033[36m",
"White": "\033[37m",
"Gray": "\033[0m",
}

account_address_mapping = {
    "contract": "0x03C6FcED478cBbC9a4FAB34eF9f40767739D1Ff7",
    "user": "0x1aE0EA34a72D944a8C7603FfB3eC30a6669E454C",
    "owner": "0x14723A09ACff6D2A60DcdF7aA4AFf308FDDC160C"
}

solidity_built_in_variables=["now",'msg.value','msg.sender','msg.data','block.number','block.timestamp','tx.origin','block.coinbase']
condition_types=["assert","require","if","while","for","ternary operation"]
assignment_operators=["=","-=","+=","/=","*="]


rw_contracts_info= [
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
         "0.4.21"], # 8-3
        ["0x1b80c5d3a76176c7119558a6b4b250a6421e893b.sol", "PiggericksShop",
         "0.5.8"],  # 9-3
        ["0xdb6bcae929767e657884b03974c849d46352cde4.sol", "ERC20Latte",
         "0.5.0"],  # 10-3
        ["0x95a6a3f44a70172e7d50a9e28c85dfd712756b8c.sol", "SynthSummaryUtil",
         "0.4.25"],  # 11-3
        ["0xe4c154be0b17359527a25e6ab45b7ce86c8795c7.sol", "digitalNotary",
         "0.6.4"],  # 12-3
    ]
contract_index=0 # specify which contract will be evaluated.
