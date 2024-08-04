import json
import os
import re
from json import JSONDecodeError

from sligpt.config import prompt_path, color_prefix

import json


def write_a_kv_pair_to_a_json_file(json_file_path_name:str,key:str,value:str):
    # Open the existing JSON file for reading
    with open(json_file_path_name, 'r') as file:
        data = json.load(file)

    # Modify the data as needed
    data[key] = value

    # Write the modified data back to the same JSON file
    with open(json_file_path_name, 'w') as file:
        json.dump(data, file,
                  indent=4)  # Optionally, use 'indent' to format the JSON for readability


def get_a_kv_pair_from_a_json(json_file_path_name:str,key:str):
    # Open the existing JSON file for reading
    if os.path.exists(json_file_path_name):
        with open(json_file_path_name, 'r') as file:
            data = json.load(file)
            if key in data.keys():
                return data[key]
            else:
                return ""
    else:
        print(f"File does not exist: {json_file_path_name}")
        return ""

def dump_json_object_to_json(data,file_path:str,indent=4):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)

def dump_to_json(data,file_path:str,indent:int=4):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data.to_json(), f, indent=indent)

def dump_json(obj, fname, indent:int=4):
    with open(fname, 'w', encoding='utf-8') as f:
        return json.dump(obj, f, indent=indent)

def load_a_json_file(file_path:str):
    data = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

        except json.JSONDecodeError as e:
            print(f"Error loading JSON from {file_path}: {e}")
        finally:
            return data

    else:
        print(f"File does not exist: {file_path}")
        return data

def load_specific_prompt_data(prompt_file_name:str,prompt_key:str)->dict:
    path=prompt_path+"{}.json".format(prompt_file_name)
    data=load_a_json_file(path)
    if prompt_key in data.keys():
        return data[prompt_key]
    return {}

def extract_json_data_from_response_in_dict(response: str):
    data = {}
    try:
        if "```json" in response:
            response_seg=response.split("```")
            for seg in response_seg:
                if seg.startswith('json'):
                    if "{" in seg:
                        if "}" in seg:
                            first_idx = seg.index('{')
                            last_idx = seg.rindex('}')
                            raw_data=seg[first_idx:last_idx + 1]
                            if "'" in raw_data:
                                raw_data=raw_data.replace("'","\"")
                            data = json.loads(f"{raw_data}")

    except JSONDecodeError:
        print(f'JSONDecodeError')
        print(response)
        assert False

    return data

def extract_json_data_from_response_in_dict_wc(response: str,function_name:str):
    """

    :param response:
    :param function_name: used to check if the extracted data is what is needed
    :return:
    """
    data = {}

    try:
        if "```json" in response:
            response_seg=response.split("```")
            for seg in response_seg:
                if seg.startswith('json'):
                    if "{" in seg:
                        if "}" in seg:
                            first_idx = seg.index('{')
                            last_idx = seg.rindex('}')
                            raw_data=seg[first_idx:last_idx + 1]
                            if "\'" in raw_data:
                                raw_data=raw_data.replace("\'","\"")
                            data = json.loads(f"{raw_data}")
                            if len(function_name)==0:
                                break
                            else:
                                if function_name in data.keys():
                                    break
                                else:
                                    data={}
        else:
            try:
                data =json.loads(response)
                if len(function_name)==0:
                    return data
                else:
                    if not function_name in data.keys():
                        data = {}
            except JSONDecodeError:
                if '{' in response and '}' in response:
                    first_idx = response.index('{')
                    last_idx = response.rindex('}')
                    raw_data = response[first_idx:last_idx + 1]
                    if "'" in raw_data:
                        raw_data = raw_data.replace("'", "\"")
                    data = json.loads(f"{raw_data}")
                    if not function_name in data.keys():
                        data={}

    except JSONDecodeError:
        print(f'JSONDecodeError')
    return data

def get_json_data_from_response_in_dict(response: str,function_name:str=""):
    """

    :param response:
    :param function_name: used to check if the extracted data is what is needed
    :return:
    """
    data = {}
    response=response.strip()
    try:
        if "```json" in response:
            if response.startswith("```json") and response.endswith("```"):
                data=response.strip("```json").strip("```")
                return json.loads(data)
            else:
                response_seg = response.split("```")
                for seg in response_seg:
                    if seg.startswith('json'):
                        if "{" in seg:
                            if "}" in seg:
                                first_idx = seg.index('{')
                                last_idx = seg.rindex('}')
                                raw_data = seg[first_idx:last_idx + 1]

                                data = json.loads(raw_data)
                                if len(function_name) == 0:
                                    return data
                                else:
                                    if function_name in data.keys():
                                        return data
                                    else:
                                        data = {}
                                        return data

        else:
            if response.startswith("{") and response.endswith("}"):
                data = response.strip("```json").strip("```")
                return json.loads(data)
            else:
                return data
    except JSONDecodeError:
        print(f'JSONDecodeError')
    return data



def remove_comments(input_str):
    # Remove single-line comments (// ...)
    input_str = re.sub(r'\/\/.*', '', input_str)

    # Remove multi-line comments (/* ... */)
    input_str = re.sub(r'\/\*.*?\*\/', '', input_str, flags=re.DOTALL)

    # Remove unnecessary space lines
    input_str = re.sub(r'\n\s*\n', '\n', input_str, flags=re.MULTILINE)

    return input_str


def present_list_as_str(lst:list)->str:
    if len(lst)==0:return ''
    elif len(lst)==1: return str(lst[0])
    elif len(lst)==2:return f'{lst[0]} and {lst[1]}'
    else:
        v=str(lst[0])
        for e in lst[1:-1]:
            v+=f', {e}'
        v+=f', and {lst[-1]}'
        return v

def present_list_as_str_or(lst:list)->str:
    if len(lst)==0:return ''
    elif len(lst)==1: return str(lst[0])
    elif len(lst)==2:return f'{lst[0]} or {lst[1]}'
    else:
        v=str(lst[0])
        for e in lst[1:-1]:
            v+=f', {e}'
        v+=f', or {lst[-1]}'
        return v

def present_examples(lst:list)->str:
    if len(lst)==0:return ''
    elif len(lst)==1: return f'Example:\n{lst[0]}'
    elif len(lst)==2:return f'Example 1:\n{lst[0]}\nExample 2:\n{lst[1]}'
    else:
        v=""
        for idx, e in enumerate(lst):
            v += f'\nExample {idx+1}:\n{e}'
        return v

def present_examples_for_dict(data_dict:dict,keys:list=[])->str:
    if len(data_dict)==0:return ''
    elif len(data_dict)==1: return f'Example:\n{list(data_dict.values())[0]}'
    else:
        idx=0
        v=""
        for key in keys:
            if key in data_dict.keys():
                idx+=1
                v+=f'\nExample {idx}:\n{data_dict[key]}'
        return v


def color_print(color_name:str,print_content:str):
    if color_name not in ['Magenta',"Green","Red","Blue",'Gray']:
        color_v="Red"
    else:color_v=color_name
    content= "{}{}{}".format(
        color_prefix[color_v],
        print_content,
        color_prefix["Gray"],
    )
    print(content)

def check_accept_status(response:str)->bool:
    if '\n' not in response:
        if 'accept' in response or 'Accept' in response:
            if f'not "accept"' not in response:
                return True
    else:
        for item in response.split('\n')[-2:]:
            if 'accept' in item or 'Accept' in item:
                if f'not "accept"' not in item:
                    return True

    return False

def check_yes_status(response:str)->bool:
    if '\n' not in response:
        if 'yes' in response or 'Yes' in response:
            if 'not yes' not in response:
                return True

        return False
    for item in response.split('\n')[-2:]:
        if 'yes' in item or 'Yes' in item:
            if 'not yes' not in item:
                return True
    return False

def check_pass_status(response:str)->bool:
    if '\n' not in response:
        if 'pass' in response or 'Pass' in response:
            if 'not pass' not in response:
                return True

        return False
    for item in response.split('\n')[-2:]:
        if 'pass' in item or 'Pass' in item:
            if 'not pass' not in item:
                return True
    return False

def check_equal_data(d1:dict,d2:dict)->bool:
    def equal_list(l1:list,l2:list)->bool:
        if len(l1)!=len(l2):return False
        if len([e1 for e1 in l1 if e1 not in l2])>0:
            return False
        if len([e2 for e2 in l2 if e2 not in l1])>0:
            return False
        return True
    if len(d1)!=len(d2):return False
    for k,v in d1.items():
        if k not in d2:return False
        v1=d2[k]
        if isinstance(v,dict) and isinstance(v1,dict):
            if not check_equal_data(v,v1):
                return False
        else:
            if isinstance(v,list) and isinstance(v1,list):
                if not equal_list(v,v1):
                    return False
            else:
                return False
    return True

def get_key_from_list(data:list)->str:
    if len(data)==0: return ""
    if len(data)==1: return f'{data[0]}'
    key=f'{data[0]}'
    for item in data[1:]:
        key+=f'#{item}'
    return key
def get_list_from_key(key:str)->list:
    if '#' not in key: return int(key)
    return [int(item) for item in key.split('#')]

def be_a_prefix(lst1:list,lst2:list)->bool:
    if len(lst1)>=len(lst2):
        s=lst2
        b=lst1
    else:
        s=lst1
        b=lst2
    for e1,e2 in zip(s,b[0:len(s)]):
        if not e1==e2:
            return False
    return True

if __name__=="__main__":
    data="""
    Based on the provided Solidity code for the `HoloToken` contract and the inherited `Ownable` contract, we need to evaluate the `approve` function to check if all the state variables read in branching conditions are correctly identified. The `approve` function uses the `whenMintingFinished` modifier, which contains a branching condition that checks the state of the `mintingFinished` variable.

Here is the `approve` function and the `whenMintingFinished` modifier:

```solidity
function approve(address _spender, uint256 _value) public whenMintingFinished returns (bool) {
  allowed[msg.sender][_spender] = _value;
  Approval(msg.sender, _spender, _value);
  return true;
}

modifier whenMintingFinished() {
  require(mintingFinished);
  _;
}
```

The `whenMintingFinished` modifier reads the `mintingFinished` state variable in a branching condition (the `require` statement). Since the `approve` function uses this modifier, the `mintingFinished` state variable is indeed read in a branching condition of the `approve` function.

The provided data about the state variables read in branching conditions of the function `HoloToken.approve(address,uint256)` is:

```json
{'HoloToken.approve(address,uint256)': {'state_variables_read_in_BC': ['mintingFinished']}}
```

After reviewing the code, we can confirm that the provided data is correct. The `approve` function does not read any other state variables in branching conditions, either directly or indirectly through called functions or local variables.

Therefore, the answer is: "yes".
    """

    data1="""
    Upon re-evaluation and considering the additional details provided, let's re-examine the `transfer` function and its related modifiers for any state variables read in branching conditions.

The `transfer` function in the `HoloToken` contract is as follows:

```solidity
function transfer(address _to, uint256 _value) public whenMintingFinished returns (bool) {
  require(_to != address(0));
  require(_value <= balances[msg.sender]);
  balances[msg.sender] = balances[msg.sender].sub(_value);
  balances[_to] = balances[_to].add(_value);
  Transfer(msg.sender, _to, _value);
  return true;
}
```

The `whenMintingFinished` modifier is used, which has a branching condition that checks the `mintingFinished` state variable:

```solidity
modifier whenMintingFinished() {
  require(mintingFinished);
  _;
}
```

Within the `transfer` function itself, there are two `require` statements that act as branching conditions. The first one checks that the `_to` address is not the zero address, and the second one checks that the `_value` is less than or equal to the sender's balance in the `balances` mapping.

The updated data for the `HoloToken.transfer(address,uint256)` function should include the `mintingFinished` state variable read in the `whenMintingFinished` modifier and the `balances` state variable read in the `require` statement within the function itself.

Here is the updated JSON response with the conditions that read the state variables:

```json
{
  "HoloToken.transfer(address,uint256)": {
    "state_variables_read_in_BC": ["mintingFinished", "balances"]
  }
}
```

This accept includes the state variables read in branching conditions within the `transfer` function and the `whenMintingFinished` modifier. Since the conditions are from `require` statements and not from a `return` statement or from functions calling `transfer`, the updated data is correct. Therefore, my response is:

    """


    # re= extract_json_data_from_response_in_dict_wc(data,"HoloToken.approve(address,uint256")
    # print(f're={re}')

    # print(check_accept_status(data1))
    # v={'DepositGame.GetBonusWithdraw()': {'state_variables_read_in_BC': ['FirstTimeBonus', '_balances']}}
    # v1={'DepositGame.GetBonusWithdraw()': {'state_variables_read_in_BC': ['FirstTimeBonus','_balances'],"xx":[]}}
    # print(check_equal_data(v,v1))

    data2="""fff
    {"StandardERC20Token.transfer(address,uint256)":{"balances":["balances[msg.sender] >= _value"]}}
    """
    re=extract_json_data_from_response_in_dict_wc(data2,"StandardERC20Token.transfer(address,uint256)")
    print(f're={re}')