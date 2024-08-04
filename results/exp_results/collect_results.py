import pandas
from sligpt.evaluation.evaluate import result_statistics_from_2_json_files



def collect_exp_results_sligpt(exp_results_path:str):

    gt_json_file=f"contract_rw_data_gt.json"

    tools=['slither','gpt4','sligpt']



    tool_results_in_json={
        "slither":["contract_rw_data_slither.json"],
        "gpt4":[
            "rw_10_contracts_gpt4_results_1st_5_25/contract_rw_data_gpt.json",
            "rw_10_contracts_gpt4_results_2nd_5_25/contract_rw_data_gpt.json",
            "rw_10_contracts_gpt4_results_3rd_5_25/contract_rw_data_gpt.json",
            "rw_10_contracts_gpt4_results_4th_5_25/contract_rw_data_gpt.json",
            "rw_10_contracts_gpt4_results_5th_5_25/contract_rw_data_gpt.json",
            ],
        "sligpt":[
            "rw_10_contracts_sligpt_results_1st_5_24/contract_rw_data_sligpt.json",
            "rw_10_contracts_sligpt_results_2nd_5_24/contract_rw_data_sligpt.json",
            "rw_10_contracts_sligpt_results_3rd_5_25/contract_rw_data_sligpt.json",
            "rw_10_contracts_sligpt_results_4th_5_25/contract_rw_data_sligpt.json",
            "rw_10_contracts_sligpt_results_5th_5_25/contract_rw_data_sligpt.json",
        ]
    }

    tools_results=[]
    for tool in tools:
        tools_results.append([tool,"","",""])
        json_files=tool_results_in_json[tool]
        for idx,file in enumerate(json_files):
            file_path_name=f'{exp_results_path}{tool}/{file}'
            statistics=result_statistics_from_2_json_files(exp_results_path, f'{tool}/{file}',
                                                gt_json_file, "file1_gt",
                                                flag_read=True,flag_save_in_file=False)
            if len(statistics)==3:
                tools_results.append([idx,f'{statistics[0][0]}/{statistics[0][1]}',f'{statistics[1][0]}/{statistics[1][1]}',f'{statistics[2][0]}/{statistics[2][1]}'])

    df_data=pandas.DataFrame(tools_results)
    df_data.to_csv(f'{exp_results_path}statistics_in_csv.csv')

if __name__=="__main__":
    exp_results_path = "C:/Users/18178/PycharmProjects/sligpt/results/exp_results/"
    collect_exp_results_sligpt(exp_results_path)


