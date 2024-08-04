The experiment data for Sligpt are located under the directory "*/results/exp_results/". The 10 contracts are in "*/datasets/rw_contracts/". "*" denotes the path of the root of the project.

- */results/exp_results/
  - gpt4/: the experimental data of GPT-4o. 
    - rw_10_contracts_gpt4_results_1st_5_25/: the data of the first run of using GPT-4o to collect dependency data.
      - _contract_rw_data_gpt.json_: the resulted dependency data.
      - _evaluation_results_gpt_alone.json_: the responses of GPT-4o saved during the experiments.
      - _rw_prompt_formats.json_: the prompts used to construct requests.
    - ...
  - sligpt/: the experimental data of Sligpt.  
    - rw_10_contracts_sligpt_results_1st_5_24/:the data of the first run of using sligpt to collect dependency data.
      - _contract_rw_data_sligpt.json_: the resulted dependency data.
      - _evaluation_results_multiple_prompts_accept.json_: the responses saved for the evaluator.
      - _evaluation_results_multiple_prompts_verify.json_: the responses saved for the verifier.
      - _need_to_check_results.json_: the responses saved for the checker.
      - _rw_prompt_formats_4.json_: the prompts used to construct requests.
    - ...
  - slither/: the experimental data of Slither. 
    - _contract_rw_data_slither.json_: the resulted dependency data.
  - _collect_results.py_: the script to collect statistics from the experimental data of Sligpt, Slither, and GPT-4o.
  - _contract_rw_data_gt.json_: the ground truth of the dependency data.  
  - _Sligpt_data_column_chart.pdf_: the column chart showing the metric results from _statistics_in_csv_xlxs.xlsx_.
  - _statistics_in_csv.csv_: the collected results by executing _collect_results.py_.
  - _statistics_in_csv_xlxs.xlsx_: the data analysis based on the results in _statistics_in_csv.csv_.

