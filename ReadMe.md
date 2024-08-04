
## Sligpt
Sligpt is an LLM-based tool to perform function dependency analysis on Solidity smart contracts. It employs GPT-4o to refine the function dependency data produced by Slither. 

[Sligpt paper](https://github.com/contractAnalysis/sligpt)

[Experimenetal data](./results/exp_results/ReadMe.md)


### How to use Sligpt based on Pycharm IDE
1, Set environment variable  OPENAI_API_KEY

This [page](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) shows how to set the variable.

2, Clone the project.
```shell
git clone https://github.com/contractAnalysis/sligpt.git
```
3, Prepare for the development environment.

- Open the project with Pycharm IDE by clicking 'File'->'Open' and selecting the downloaded project name. 
- Create a virtual environment by clicking 'OK' on the pop window of "Creating Virtual Environment".

- Install the required packages in the virtual environment. Execute the following command in terminal of Pycharm IDE to install packages in case the packages failed to be installed in the above step.
```
pip install -r requirements.txt --no-deps
```

4, Run rw.py with proper arguments.
Take an example on the contract test.sol coming alone with this project.
To get dependency data for the contract test.sol, the parameters given to rw.py are as follows: 
```
--task dependency,sligpt
--solidity_file_name test.sol
--contract_name test
--solc_version 0.4.25
--solidity_file_path project_path/datasets/rw_contracts/
--contract_data_path project_path/results/contract_data/
--result_path project_path/results/rw_results/
```
Note, change the **--task** option to get the dependency data using GPT-4o and Slither with _**dependency,gpt4**_, _**dependency,slither**_ respectively.


To get the dependency data for function **add** in the contract test.sol, the parameters given to rw.py are as follows:

```
--task function_dependency,sligpt
--solidity_file_name test.sol
--contract_name test
--function test.add(int8)
--solc_version 0.4.25
--solidity_file_path project_path/datasets/rw_contracts/
--contract_data_path project_path/results/contract_data/
--result_path project_path/results/rw_results/
```
_--function_ is required to specify the function and the name of the _--task_ option is **function_dependency,sligpt**. The other options are the same as the case of getting the dependency data for a contract.





### Importance
 To reduce the unnecessary requests sent to GPT-4o , all the responses from GPT-4o are saved so that they can be reused when validating and debugging. To see how GPT-4o responses at the current moment for a contract, the saved results should be removed.

Take an example on the contract test.sol, you need to remove the all key-value pairs with the keys prefixed with **test.sol_test** in:<br>

- "need_to_check_results.json", 
- "evaluation_results_multiple_prompts_accept.json", and 
- "evaluation_results_multiple_prompts_verify.json" 

under the directory "project_path/results/gpt_evaluation_intermediate_results/".

To check on a particular function, for example, function **add** in test.sol, you need to remove all key-value pairs with the keys prefixed with **test.sol_test_test.add(int8)**.


