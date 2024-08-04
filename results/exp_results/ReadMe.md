The experiment data for Sligpt are located under the directory "*/results/exp_results/". The 10 contracts are in "*/datasets/rw_contracts/". "*" denotes the path of the root of the project.

- ***/results/exp_results/**
  - **gpt4/** <span style="color: gray;">the experimental data of GPT-4o. </span>
    - rw_10_contracts_gpt4_results_1st_5_25/ <span style="color: gray;">the data of the first run of using GPT-4o to collect dependency data.</span>
      - _contract_rw_data_gpt.json_ <span style="color: gray;">the resulted dependency data.</span>
      - _evaluation_results_gpt_alone.json_ <span style="color: gray;">the responses of GPT-4o saved during the experiments.</span>
      - _rw_prompt_formats.json_ <span style="color: gray;">the prompts used to construct requests.</span>
    - ...
  - **sligpt/** <span style="color: gray;">the experimental data of Sligpt.</span>  
    - rw_10_contracts_sligpt_results_1st_5_24/ <span style="color: gray;">the data of the first run of using sligpt to collect dependency data.</span>
      - _contract_rw_data_sligpt.json_ <span style="color: gray;">the resulted dependency data.</span>
      - _evaluation_results_multiple_prompts_accept.json_ <span style="color: gray;">the responses saved for the evaluator.</span>
      - _evaluation_results_multiple_prompts_verify.json_ <span style="color: gray;">the responses saved for the verifier.</span>
      - _need_to_check_results.json_ <span style="color: gray;">the responses saved for the checker.</span>
      - _rw_prompt_formats_4.json_ <span style="color: gray;">the prompts used to construct requests.</span>
    - ...
  - **slither/** <span style="color: gray;">the experimental data of Slither.</span> 
    - _contract_rw_data_slither.json_ <span style="color: gray;">the resulted dependency data.</span>
  - _collect_results.py_ <span style="color: gray;">the script to collect statistics from the experimental data of Sligpt, Slither, and GPT-4o.</span>
  - _contract_rw_data_gt.json_ <span style="color: gray;">the ground truth of the dependency data. </span> 
  - _Sligpt_data_column_chart.pdf_ <span style="color: gray;">the column chart showing the metric results from _statistics_in_csv_xlxs.xlsx_.</span>
  - _statistics_in_csv.csv_ <span style="color: gray;">the collected results by executing _collect_results.py_.</span>
  - _statistics_in_csv_xlxs.xlsx_ <span style="color: gray;">the data analysis based on the results in _statistics_in_csv.csv_.</span>

