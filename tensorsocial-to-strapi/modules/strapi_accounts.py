from utilities import *
from modules.strapi import *


def get_sp_accounts_api_endpoint(endpoint, params='?', page_size='100', field_key='name'):
    account_username_file = STRAPI_API_RESULTS_PATH + endpoint + '_usernames.csv'
    account_ts_id_file = STRAPI_API_RESULTS_PATH + endpoint + '_ts_id.csv'
    slug_username_file = STRAPI_API_RESULTS_PATH + endpoint + '_slug_username.json'
    username_slug_file = STRAPI_API_RESULTS_PATH + endpoint + '_username_slug.json'
    username_items_list = []
    ts_id_item_list = []
    slug_username_dict = {}
    username_slug_dict = {}
    page_count = sp_page_count(endpoint, params, page_size)
    if isinstance(page_count, int):
        for count in range(page_count):
            tm_params = params + 'sort=' + field_key + '&pagination[page]=' + str(
                count + 1) + '&pagination[pageSize]=' + page_size
            sp_query = sp_read_conn(endpoint, tm_params)
            if type(sp_query) is dict and len(sp_query) != 0: # TODO check if it is len(sp_query['data])
                for el in sp_query['data']:
                    username_items_list.append(el['attributes'][field_key])
                    ts_id_item_list.append(el['attributes']['ts_user_id'])
                    slug_username_dict[el['attributes']['slug']] = el['attributes'][field_key]
                    username_slug_dict[el['attributes'][field_key]] = el['attributes']['slug']
            else:
                write_log(
                    'Script get_sp_accounts_api_endpoint terminated: Strapi query failed with request code ' + str(sp_query))
                exit()
        list_to_csv(username_items_list, account_username_file)
        list_to_csv(ts_id_item_list, account_ts_id_file)
        data_to_json(slug_username_dict, slug_username_file)
        data_to_json(username_slug_dict, username_slug_file)
        write_log('File ' + account_username_file + ' updated')
        write_log('File ' + account_ts_id_file + ' updated')
        write_log('File ' + slug_username_file + ' updated')
        write_log('File ' + username_slug_file + ' updated')
    else:
        write_log(page_count)


def create_slug(username):
    slug = username
    if slug == '' or slug == 'null':
        slug = random_string()
    if slug in slug_list:
        slug += '----' + random_string()
    slug_list.append(slug)
    return slug


def add_account(account, platform_id):
    sp_dict = {
        "data": dict(
            username=account['username'],
            slug=create_slug(account['username']),
            ts_user_id=account['user_id'],
            platform=platform_id,
            url=account['url'],
            hashtag_groups=sp_hashtag_group_id,
        )
    }
    if account['followers'] and account['followers'] != '':
        sp_dict['data']['followers'] = str(account['followers'])
    if account['engagements'] and account['engagements'] != '':
        sp_dict['data']['engagements'] = str(account['engagements'])
    if account['engagement_rate'] and account['engagement_rate'] != '':
        sp_dict['data']['engagement_rate'] = str(account['engagement_rate'])
    if account['picture'] and account['picture'] != '':
        sp_dict['data']['picture'] = account['picture']
    if len(hashtag_id_list) > 0:
        sp_dict['data']['hashtags'] = hashtag_id_list
    try:
        sp_query = sp_write_conn(json.dumps(sp_dict), 'accounts', '')
        return sp_dict
    except Exception as e:
        return sp_dict, repr(e)


def get_account_hg_group(account_ts_id):
    try:
        sp_dict = sp_read_conn('accounts', '?populate=*&filters[ts_user_id]=' + account_ts_id)
        if type(sp_dict) is dict and len(sp_dict) != 0: # TODO check if it is len(sp_query['data])
            sp_hg_group_id_list = []
            for hg in sp_dict['data'][0]['attributes']['hashtag_groups']['data']:
                sp_hg_group_id_list.append(str(hg['id']))
            return str(sp_dict['data'][0]['id']), sp_hg_group_id_list
        else:
            return '', []
    except Exception as e:
        return repr(e)


def get_account_hgs(account_sp_id):
    try:
        sp_dict = sp_read_conn('accounts', '/' + account_sp_id + '?populate=*')
        if type(sp_dict) is dict and len(sp_dict) != 0: # TODO check if it is len(sp_query['data])
            sp_hg_ids_list = []
            for hg in sp_dict['data']['attributes']['hashtags']['data']:
                sp_hg_ids_list.append(str(hg['id']))
            return sp_hg_ids_list
        else:
            return []
    except Exception as e:
        return repr(e)


def sp_hashtag_group_update(hashtag_group_list, endpoint, params='', token=STRAPI_API_TOKEN_WRITE):
    query_conn = STRAPI_API_ENDPOINT + endpoint + params
    sp_dict = {
        "data": dict(
            hashtag_groups=hashtag_group_list,
        )
    }
    query_request = requests.put(query_conn, data=json.dumps(sp_dict).encode('utf-8'),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}",
                                          'charset': 'utf-8'})
    return query_request.status_code


def sp_hashtags_update(hashtags_list, endpoint, params='', token=STRAPI_API_TOKEN_WRITE):
    query_conn = STRAPI_API_ENDPOINT + endpoint + params
    sp_dict = {
        "data": dict(
            hashtags=hashtags_list,
        )
    }
    query_request = requests.put(query_conn, data=json.dumps(sp_dict).encode('utf-8'),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}",
                                          'charset': 'utf-8'})
    return query_request.status_code
