from modules.strapi import *
from modules.tensorsocial import *
import json
from time import sleep
from pandas import json_normalize


#######################################################
### CREATE A FILE WITH TOTAL RESULTS FOR EACH QUERY ###
#######################################################

def print_totals():
    hg_total_results_dict = {}
    ts_query_limit = 1
    ts_query_skip = 0
    for d_key in sp_hashtag_group_dict:
        ts_query = get_ts_query(sp_hashtag_group_dict[d_key])
        ts_api_req = update_ts_query(ts_query, ts_query_limit, ts_query_skip, sp_hashtag_group_dict[d_key])
        total_results = get_total_results(ts_api_req)
        hg_total_results_dict.update({d_key: str(total_results)})
        print(hg_total_results_dict)
        sleep(3)
    with open(TS_QUERY_RES_PATH + 'ts_query_total_results.json', 'w') as file:
        json.dump(hg_total_results_dict, file, indent=4)
    write_log(f'{TS_QUERY_RES_PATH}ts_query_total_results.json updated')


# print_totals()


#######################################################
###### CREATE CSVs FROM JSON FILES QUERY RESULTS ######
#######################################################

def json_to_csv():
    hg_group = "ads-sky-news"
    date = "2022-10-02"
    ts_res_today_folder_csv = TS_QUERY_RES_PATH_CSV + '' + date
    is_ts_res_dir_csv = os.path.exists(ts_res_today_folder_csv)
    if not is_ts_res_dir_csv:
        os.makedirs(ts_res_today_folder_csv)

    ts_res_folder_csv = ts_res_today_folder_csv + '/' + hg_group
    is_ts_res_dir_csv = os.path.exists(ts_res_folder_csv)
    if not is_ts_res_dir_csv:
        os.makedirs(ts_res_folder_csv)

    raw_ts_res_file_list = os.listdir(TS_QUERY_RES_PATH_JSON + '' + date + '/' + hg_group)
    ts_res_file_list = [item for item in raw_ts_res_file_list if item.startswith('hg_')]
    ts_res_file_list.sort()

    for ts_res_file in ts_res_file_list:
        with open(TS_QUERY_RES_PATH_JSON + '' + date + '/' + hg_group + '/' + ts_res_file) as json_file:
            json_data = json.load(json_file)
            df = json_normalize(json_data['users'])
        csv_name = ts_res_file[:-5]
        df.to_csv(ts_res_folder_csv + '/' + csv_name + '.csv', index=False)
        write_log(ts_res_folder_csv + '/' + csv_name + '.csv created')


# json_to_csv()  # change hg_group and date
