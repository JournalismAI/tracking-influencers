from typing import List, Any

from modules.strapi_accounts import *
import json
import csv
import os

###############################################
############# EMPTY LOG FILES #################
###############################################

# empty_csv(sp_influ_import_list, 0)  # keep headers
# empty_csv(sp_influ_import_log, 0)  # keep headers
# empty_file(sp_failed_import_log)
# exit()

###############################################
############## STRAPI IMPORT ##################
###############################################

print(f'\n\n\n*************************************\n\n')
write_log(f'Start Strapi strapi_import procedure for {get_dict_key(sp_hashtag_group_dict, sp_hashtag_group_id)}')

with open(ts_res_folder_json + 'ts_query_' + get_date() + '.json', 'r') as f:
    d = json.load(f)
    platform = d['body']['platform']
    if 'text_tags' in d['body']['search']:
        for tag in d['body']['search']['text_tags']:
            hashtag_list.append(tag['value'])
            hashtag_id_list.append(sp_hashtag_dict[tag['value']])
    else:
        write_log('hashtag_list and hashtag_id_list empty')
    write_log(f'Data platform: {platform}')
    write_log(f'Folder to be imported: {ts_res_folder_json}')


# action_input = input("Continue: y/n")
action_input = "y"

if action_input == 'n':
    exit('\nCancelled procedure')
elif action_input != 'n' and action_input != 'y':
    exit('\nAction not allowed')


get_sp_accounts_api_endpoint('accounts', params='?', page_size='100', field_key='username')
sp_new_item_counter = 0
sp_updated_item_counter = 0
failed_import_counter = 0
failed_import_dict = []
failed_import_usernames = []
failed_import_slugs = []
discarted_account_list = []
import_usernames = []
already_import_usernames = []
account_custom_list = read_csv(account_custom_csv)  # hand-made TS account filter
hg_file = ''
platform_id = sp_platform_dict[platform]

ts_res_file_list = get_import_file_list(ts_res_folder_json)
if len(ts_res_file_list) == 0:
    exit('Attention! Files to be import not found')

sp_ts_id_list = read_csv(STRAPI_API_RESULTS_PATH + 'accounts_ts_id.csv')  # TS accounts already in Strapi

try:
    for ts_res_file in ts_res_file_list:
        hg_file = ts_res_folder_json + ts_res_file
        with open(ts_res_folder_json + ts_res_file, 'r') as f:
            ts_res_dict = json.load(f)
            for account in ts_res_dict['users']:
                if (len(account_custom_list) > 0 and account['user_id'] in account_custom_list) or len(account_custom_list) == 0:
                    if len(sp_ts_id_list) > 0 and account['user_id'] not in sp_ts_id_list or len(sp_ts_id_list) == 0:
                        sp_item = add_account(account, platform_id)
                        if type(sp_item) is dict and len(sp_item) != 0:
                            sp_new_item_counter += 1
                            write_log('Success -- account ' + sp_item['data']['username'] + ' imported to Strapi')
                            import_usernames.append(account['username'])
                        else:
                            failed_import_dict.append(sp_item[0])
                            failed_import_slugs.append(sp_item[0]['data']['slug'])
                            failed_import_usernames.append(sp_item[0]['data']['username'])
                            failed_import_counter += 1
                            msg = 'Failed -- account ' + sp_item[0]['data']['username'] + ' import to Strapi failed: ' + sp_item[1]
                            failed_import_log(msg)
                            write_log(msg)
                    elif len(sp_ts_id_list) > 0 and account['user_id'] in sp_ts_id_list:
                        sp_account_id, sp_account_hg_group_id_list = get_account_hg_group(account['user_id'])
                        if sp_hashtag_group_id not in sp_account_hg_group_id_list:
                            sp_account_hg_group_id_list.append(sp_hashtag_group_id)
                            sp_update_res = sp_hashtag_group_update(sp_account_hg_group_id_list, 'accounts', '/' + sp_account_id + '?populate=*')
                            if sp_update_res == 200:
                                write_log(f'Account {account["username"]} already in Strapi - hashtag_group {str(sp_hashtag_group_id)} added to account')
                                sp_updated_item_counter += 1
                                if len(hashtag_id_list) > 0:
                                    sp_account_hashtag_id_list = get_account_hgs(sp_account_id)
                                    sp_account_hashtag_id_list += hashtag_id_list
                                    sp_update_res = sp_hashtags_update(sp_account_hashtag_id_list, 'accounts', '/' + sp_account_id + '?populate=*')
                                    hg_id_str = ', '.join(sp_account_hashtag_id_list)
                                    if sp_update_res == 200:
                                        write_log(f'Account {account["username"]} already in Strapi - new hashtags {hg_id_str} added to account')
                                    else:
                                        write_log(f'Failed -- Account {account["username"]} already in Strapi - new hashtags {hg_id_str} add failed')
                            else:
                                write_log(f'Failed -- Account {account["username"]} already in Strapi - hashtag_group {str(sp_hashtag_group_id)} add failed')
                        else:
                            write_log(f'Account {account["username"]} with hashtag_group {str(sp_hashtag_group_id)} both already in Strapi')
                            already_import_usernames.append(account['username'])
                    else:
                        write_log(f'Account {account["username"]} discarded as not in sp_ts_id_list (TS accounts already in Strapi)')
                else:
                    discarted_account_list.append(account['user_id'])
                    write_log(f'Account {account["username"]} discarded as not in account_custom_list (hand-made TS account filter)')
    import_usernames.sort()
    already_import_usernames.sort()
    failed_import_usernames.sort()
    list_to_csv(import_usernames, strapi_import_folder + 'import_usernames.csv')
    list_to_csv(already_import_usernames, strapi_import_folder + 'already_import_usernames.csv')
    list_to_csv(failed_import_usernames, strapi_import_folder + 'failed_import_account_names.csv')
    list_to_csv(discarted_account_list, strapi_import_folder + 'discarted_account_list.csv')
    data_to_json(failed_import_dict, strapi_import_folder + 'failed_import_account_dict.json')
    write_log(str(sp_new_item_counter) + ' new accounts imported to Strapi')
    write_log(str(sp_updated_item_counter) + ' accounts updated in Strapi')
    write_log(str(failed_import_counter) + ' failed imports to Strapi. Check failed_import_account_* files')
except Exception as e:
    failed_import_log('Local file ' + hg_file + ' import failed: ' + repr(e))
    write_log('Local file ' + hg_file + ' import failed: ' + repr(e))

