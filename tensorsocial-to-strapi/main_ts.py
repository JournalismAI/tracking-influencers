from modules.strapi import *
from modules.tensorsocial import *
import json
from time import sleep

###############################################
############# EMPTY LOG FILES #################
###############################################

# empty_file(sp_failed_import_log)
# empty_ts_query_log()
# exit()

###############################################
########## TENSOR SOCIAL API REQUEST ##########
###############################################

print(f'\n\n\n*************************************\n\n')
write_log(f'Start Tensor Social import procedure for {get_dict_key(sp_hashtag_group_dict, sp_hashtag_group_id)}')

ts_query = get_ts_query()
ts_new_query = {
    'timestamp': get_now(),
    'hashtag_group_key': get_dict_key(sp_hashtag_group_dict, sp_hashtag_group_id),
    'hashtag_group_id': sp_hashtag_group_id,
    'body': ts_query
}

with open(ts_query_log, 'r+') as f:
    file_data = json.load(f)
    file_data["queries"].insert(0, ts_new_query)
    f.seek(0)
    json.dump(file_data, f, indent=4)

with open(ts_res_folder_json + 'ts_query_' + get_date() + '.json', 'w') as f:
    json.dump(ts_new_query, f, indent=4)

ts_query_limit = 100  # fixed
ts_query_skip = 0  # 0 -> 100 -> 200 -> ...
ts_api_q_limit = 99  # API query limit 10000 (ts_api_q_limit 99 if ts_query_limit = 100)
ts_api_req = update_ts_query(ts_query, ts_query_limit, ts_query_skip)
total_results = get_total_results(ts_api_req) - ts_query_skip
q, mod = divmod(total_results, ts_query_limit)
write_log(f'total results: {total_results}, q: {q}, mod: {mod}')

# action_input = input("Continue: y/n")
action_input = "y"

if action_input == 'n':
    exit('\nCancelled procedure')
elif action_input != 'n' and action_input != 'y':
    exit('\nAction not allowed')

i = 0
while i <= q:
    json_file_name = 'hg_' + str(sp_hashtag_group_id) + '__'
    # json_file_name = 'hg_MALE_' + str(sp_hashtag_group_id) + '__'  #  population-sole
    if i == ts_api_q_limit + 1:
        ts_query_skip = 0
        ts_query_limit = 100
        # print("limit", i, ts_api_q_limit)
        sleep(10)
    try:
        if i > ts_api_q_limit:
            ts_api_req = update_ts_query(ts_query, ts_query_limit, ts_query_skip, 'asc')
            # print('i asc', i)
        else:
            ts_api_req = update_ts_query(ts_query, ts_query_limit, ts_query_skip, 'desc')
            # print('i desc', i)
        ts_api_res = payload_influ(ts_api_req)
        ts_query_skip_in_file_name = str(ts_query_skip)
        ts_query_limit_in_file_name = str(ts_query_skip + ts_query_limit)
        if i == q:
            ts_query_limit_in_file_name = str(ts_query_skip + mod)
        if i > ts_api_q_limit:
            ts_query_skip_in_file_name = str(10000 + ts_query_skip)
            ts_query_limit_in_file_name = str(10000 + ts_query_skip + ts_query_limit)
            if i == q:
                ts_query_limit_in_file_name = str(10000 + ts_query_skip + mod)
        json_file_name = json_file_name + ts_query_skip_in_file_name + '_' + ts_query_limit_in_file_name
        if i > ts_api_q_limit:
            json_file_name = json_file_name + '__ASC'
        json_file_name = json_file_name + '.json'
        with open(ts_res_folder_json + json_file_name, 'w') as f:
            json.dump(ts_api_res, f, indent=4)
            write_log(f'{json_file_name} created')
        i += 1
        ts_query_skip += ts_query_limit
    except Exception as e:
        failed_import_log('Query ' + str(get_dict_key(sp_hashtag_group_dict,
                                                      sp_hashtag_group_id)) + ' - File ' + json_file_name + ' download failed: ' + repr(
            e))
        write_log('Query ' + str(get_dict_key(sp_hashtag_group_dict,
                                              sp_hashtag_group_id)) + ' - File ' + json_file_name + ' download failed: ' + repr(
            e))


open(account_custom_csv, 'a').close()
write_log(f'File {account_custom_csv} created')
