# pip3 freeze > requirements.txt

from requirements.config import *
from datetime import datetime
import json
import requests
import pandas as pd
import os
import csv
import string
import random


def get_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(4))


###############################################
###############   PATHS    ####################
###############################################


DATA_PATH = './data/'
DATA_SAMPLES_PATH = DATA_PATH + 'samples/'
TS_QUERY_RES_PATH = DATA_PATH + 'ts_query_results/'
TS_QUERY_RES_PATH_JSON = TS_QUERY_RES_PATH + 'json/'
TS_QUERY_RES_PATH_CSV = TS_QUERY_RES_PATH + 'csv/'
LOG_PATH = './logs/'
STRAPI_API_RESULTS_PATH = LOG_PATH + 'strapi_api_results/'

###############################################
############ STRAPI HASHTAG GROUPS ############
###############################################

slug_list = []
hashtag_list = []
hashtag_id_list = []


def get_dict_key(my_dict, val):
    for d_key, d_value in my_dict.items():
        if val == d_value:
            return d_key


def get_sp_content_type(content_type, field):
    query_conn = STRAPI_API_CONN + '' + content_type + '/?pagination[pageSize]=100'  # TODO add pagination if results are > 100
    print(query_conn)
    query_request = requests.get(query_conn, headers={"Authorization": f"Bearer {STRAPI_API_TOKEN_READ}"})
    content_dict = {}
    if query_request.status_code == requests.codes.ok:
        tmp_dict = {}
        query_result = query_request.json()  # dict
        if type(query_result) is dict and len(query_result) != 0:
            for res in query_result['data']:
                tmp_dict.update({res['attributes'][field]: str(res['id'])})
            sorted_keys = sorted(tmp_dict, key=tmp_dict.get)
            for k in sorted_keys:
                content_dict[k] = tmp_dict[k]
        else:
            print('Script terminated: unable to create ' + content_type + ' dictionary, Strapi query result is empty')
            exit()
        return content_dict
    else:
        print('Script terminated: unable to create ' + content_type + ' dictionary, Strapi query failed with request code ' + str(
                query_request.status_code))
        exit()


sp_hashtag_group_dict = get_sp_content_type('hashtag-groups', 'slug')
sp_hashtag_dict = get_sp_content_type('hashtags', 'text')
sp_platform_dict = get_sp_content_type('platforms', 'slug')

with open(DATA_PATH + 'sp_hashtag_group.json', 'w') as f:
    json.dump(sp_hashtag_group_dict, f, indent=4)

with open(DATA_PATH + 'sp_hashtags.json', 'w') as f:
    json.dump(sp_hashtag_dict, f, indent=4)

with open(DATA_PATH + 'sp_platform.json', 'w') as f:
    json.dump(sp_platform_dict, f, indent=4)


print("Hashtag groups:")
for key, value in sp_hashtag_group_dict.items():
    print(f"    {value}. {key}")
# hs_input = input("Insert hashtag group number: ")
hs_input = "13"

if hs_input in sp_hashtag_group_dict.values():
    sp_hashtag_group_id = hs_input
    sp_hashtag_group_key = get_dict_key(sp_hashtag_group_dict, sp_hashtag_group_id)
else:
    exit("Hashtag group not allowed")


ts_res_today_folder_json = TS_QUERY_RES_PATH_JSON + '' + str(get_date())
is_ts_res_dir = os.path.exists(ts_res_today_folder_json)
if not is_ts_res_dir:
    os.makedirs(ts_res_today_folder_json)

ts_res_folder_json = ts_res_today_folder_json + '/' + str(get_dict_key(sp_hashtag_group_dict, sp_hashtag_group_id) + '/')
is_ts_res_dir = os.path.exists(ts_res_folder_json)
if not is_ts_res_dir:
    os.makedirs(ts_res_folder_json)


strapi_import_folder = ts_res_folder_json + 'strapi_import/'
is_strapi_import_folder = os.path.exists(strapi_import_folder)
if not is_strapi_import_folder:
    os.makedirs(strapi_import_folder)


###############################################
############### DATA FILES ####################
###############################################

sp_influ_import_list = LOG_PATH + 'sp_influencer_import_list.csv'
sp_influ_import_log = LOG_PATH + 'sp_influencer_import_log.csv'
sp_import_log = LOG_PATH + 'sp_import.txt'
sp_failed_import_log = LOG_PATH + 'sp_failed_import.txt'
ts_query_log = LOG_PATH + 'ts_query_log.json'
account_custom_csv = ts_res_folder_json + 'ts_account_custom_selection.csv'


def empty_csv(csv_file, row_num):
    df = pd.read_csv(csv_file)
    df = df.head(row_num)
    df.to_csv(csv_file, index=False, header=True)


def empty_file(file):
    with open(file, 'w') as f:
        f.write('')


def list_to_csv(rows, csv_file):
    with open(csv_file, 'w') as f:
        write = csv.writer(f, delimiter='\n')
        write.writerow(rows)


def data_to_json(data, json_file):
    json_obj = json.dumps(data, indent=2)
    with open(json_file, 'w') as f:
        f.write(json_obj)


def unique_elem_list(el, unique_list):
    if el not in unique_list:
        unique_list.append(el)


def list_diff(li1, li2):
    li_diff = [i for i in li1 + li2 if i not in li1 or i not in li2 and len(i) > 0]
    return li_diff


def read_csv(file, param='list'):
    with open(file, 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        if param == 'row':
            for row in csv_reader:
                return row
        else:
            tmp_list = []
            for row in csv_reader:
                if len(row) > 0:
                    tmp_list.append(row[0])
            return tmp_list


##########################################
############  LOG FILES    ###############
##########################################


def update_csv_influ_log(hashtag_group_key, influ_id, status):
    with open(sp_influ_import_log, 'a') as file:
        file.write(get_now() + ',' + hashtag_group_key + ',' + influ_id + ',' + status + '\n')


def failed_import_log(msg, file=sp_failed_import_log):
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.write('##################\n' + get_now() + '\n' + msg + '\n##################\n\n\n' + content)


def write_log(msg: object, file: object = sp_import_log) -> object:
    with open(file, 'a') as file:
        file.write('' + get_now() + ' - ' + msg + '\n')
    print(msg)


def empty_ts_query_log():
    with open(ts_query_log, 'w') as f:
        f.write('{"queries" : []}')
