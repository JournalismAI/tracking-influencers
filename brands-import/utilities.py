# pip3 freeze > requirements.txt
from datetime import datetime
import requests
from requirements.config import *
import csv
import json
import re
import os
import pandas as pd
from slugify import slugify
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
############### DATA FILES ####################
###############################################

DATA_PATH = './data/'
DATA_BRANDS_PATH = DATA_PATH + 'profile_brands/'
# DATA_BRANDS_PATH = DATA_PATH + 'test/'
DATA_STRAPI_PATH = DATA_PATH + 'strapi_api_results/'
DATA_IMPORT_PATH = DATA_PATH + 'import/'
LOG_PATH = './logs/'
strapi_import_log = LOG_PATH + 'strapi_import.txt'
strapi_failed_import_log = LOG_PATH + 'strapi_failed_import.txt'

brand_file_list = os.listdir(DATA_BRANDS_PATH)
if '_' in brand_file_list:
    brand_file_list.remove('_')
brand_file_list.sort()


def unique_elem_list(el, unique_list):
    if el not in unique_list:
        unique_list.append(el)


def list_diff(li1, li2):
    li_diff = [i for i in li1 + li2 if i not in li1 or i not in li2 and len(i) > 0]
    return li_diff


def list_to_csv(rows, csv_file):
    with open(csv_file, 'w') as f:
        write = csv.writer(f, delimiter='\n')
        write.writerow(rows)


def data_to_json(data, json_file):
    json_obj = json.dumps(data, indent=2)
    with open(json_file, 'w') as f:
        f.write(json_obj)


def empty_csv(csv_file, row_num):
    df = pd.read_csv(csv_file)
    df = df.head(row_num)
    df.to_csv(csv_file, index=False, header=True)
    print('Csv emptied')


def empty_file(file):
    with open(file, 'w') as f:
        f.write('')
        print('File emptied')


def failed_import_log(msg: object) -> object:
    with open(strapi_failed_import_log, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.write('##################\n' + get_now() + '\n' + msg + '\n##################\n\n\n' + content)


def write_log(msg, file=strapi_import_log):
    with open(file, 'a') as f:
        f.write('' + get_now() + ' - ' + msg + '\n')
    print(msg)


def read_csv(file, param='list'):
    with open(file, 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        if param == 'row':
            for row in csv_reader:
                return row
        else:
            tmp_list = []
            for row in csv_reader:
                tmp_list.append(row)
            return tmp_list


def create_brand_json_from_files():
    data_dict = {}
    slug_list = []
    brand_counter = 0
    json_file = DATA_IMPORT_PATH + 'profile_brand_data.json'
    try:
        for file in brand_file_list:
            row = read_csv(DATA_BRANDS_PATH + file, 'row')
            slug = slugify(row[0])
            if slug == '' or slug == 'null':
                slug = file.replace("_", "")
            if slug in slug_list:
                slug += '----' + random_string()
            slug_list.append(slug)
            brand_dict = {
                file: {
                    'org_name': row[0],
                    'org_slug': slug,
                    'org_tag': row[6],
                    'org_website': row[4],
                    'org_email': row[8],
                    'org_phone': row[9],
                    'brand_name': file,
                    'brand_bio': row[7],
                    'brand_picture': row[10],
                }
            }
            data_dict.update(brand_dict)
            brand_counter += 1
        data_to_json(data_dict, json_file)
        write_log(str(brand_counter) + ' brands added to file ' + json_file)
    except Exception as e:
        msg = 'Script create_brand_json_from_files failed on file ' + json_file + ': ' + repr(e)
        failed_import_log(msg)
        write_log(msg)


def create_brand_org_slug_json():
    brands_dict = {}
    brand_counter = 0
    json_file = DATA_IMPORT_PATH + 'profile_org_slug_brand_name.json'
    try:
        with open(DATA_IMPORT_PATH + 'profile_brand_data.json') as f:
            data_dict = json.load(f)
        for file in brand_file_list:
            brand = {
                data_dict[file]['org_slug']: file
            }
            brands_dict.update(brand)
            brand_counter += 1
        data_to_json(brands_dict, json_file)
        write_log(str(brand_counter) + ' orgs added to file ' + json_file)
    except Exception as e:
        msg = 'Script create_brand_org_slug_json failed on file ' + json_file + ': ' + repr(e)
        failed_import_log(msg)
        write_log(msg)


###############################################
############ STRAPI API CONN ##################
###############################################

def sp_read_conn(relative_path, params='?sort=name', token=STRAPI_API_TOKEN_READ):
    query_conn = STRAPI_API_CONN + '/' + relative_path + '/' + params
    print(query_conn)
    query_request = requests.get(query_conn, headers={"Authorization": f"Bearer {token}"})
    if query_request.status_code == requests.codes.ok:
        query_result = query_request.json()  # dict
        return query_result
    else:
        return query_request.status_code


def sp_write_conn(data, relative_path, params='', token=STRAPI_API_TOKEN_WRITE):
    query_conn = STRAPI_API_ENDPOINT + '/' + relative_path + '/' + params
    query_request = requests.post(query_conn, data=data.encode('utf-8'),
                                  headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}",
                                           'charset': 'utf-8'})
    if query_request.status_code == requests.codes.ok:
        query_result = query_request.json()  # dict
        return query_result
    else:
        return query_request.status_code


def sp_page_count(endpoint, params, page_size):
    sp_query = sp_read_conn(endpoint, params + '&pagination[pageSize]=' + page_size)
    if type(sp_query) is dict and len(sp_query) != 0:
        return sp_query['meta']['pagination']['pageCount']
    else:
        return 'Strapi api page count error ' + str(sp_query)


def get_sp_api_endpoint(endpoint, params='?', page_size='100', field_key='name'):
    file = DATA_STRAPI_PATH + endpoint + '.csv'
    items_list = []
    page_count = sp_page_count(endpoint, params, page_size)
    if isinstance(page_count, int):
        for count in range(page_count):
            tm_params = params
            if endpoint != 'tags':
                tm_params += 'sort=' + field_key + '&pagination[page]=' + str(
                    count + 1) + '&pagination[pageSize]=' + page_size
            sp_query = sp_read_conn(endpoint, tm_params)
            if type(sp_query) is dict and len(sp_query) != 0:
                for el in sp_query['data']:
                    items_list.append(el['attributes'][field_key])
            else:
                write_log(
                    'Script get_sp_api_endpoint terminated: Strapi query failed with request code ' + str(sp_query))
                exit()
        list_to_csv(items_list, file)
        write_log('File ' + file + ' updated')
    else:
        write_log(page_count)


def update_sp_item_id_json(endpoint, file, params='?', page_size='100', field_key='name'):
    page_count = sp_page_count(endpoint, params, page_size)
    if isinstance(page_count, int):
        sp_dict = {}
        for count in range(page_count):
            tm_params = params + 'sort=' + field_key + '&pagination[page]=' + str(
                count + 1) + '&pagination[pageSize]=' + page_size
            sp_query = sp_read_conn(endpoint, tm_params)
            if type(sp_query) is dict and len(sp_query) != 0:
                for item in sp_query['data']:
                    item_dict = {
                        item['attributes'][field_key]: item['id']
                    }
                    sp_dict.update(item_dict)
            else:
                msg = 'Failed -- File ' + DATA_STRAPI_PATH + file + ' not updated: ' + str(sp_query)
                failed_import_log(msg)
                write_log(msg)
        data_to_json(sp_dict, DATA_STRAPI_PATH + file)
        write_log('File ' + DATA_STRAPI_PATH + file + ' updated')
    else:
        write_log(page_count)
