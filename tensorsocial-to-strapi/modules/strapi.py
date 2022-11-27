from utilities import *
from slugify import slugify


def sp_read_conn(endpoint, params='', token=STRAPI_API_TOKEN_READ):
    query_conn = STRAPI_API_CONN + endpoint + params
    print(query_conn)
    query_request = requests.get(query_conn, headers={"Authorization": f"Bearer {token}"})
    if query_request.status_code == requests.codes.ok:
        query_result = query_request.json()  # dict
        return query_result
    else:
        return query_request.status_code


def sp_write_conn(data, endpoint, params='', token=STRAPI_API_TOKEN_WRITE):
    query_conn = STRAPI_API_ENDPOINT + endpoint + params
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


'''def get_sp_api_endpoint(endpoint, params='?', page_size='100', field_key='name'):
    file = STRAPI_API_RESULTS_PATH + endpoint + '.csv'
    items_list = []
    page_count = sp_page_count(endpoint, params, page_size)
    if isinstance(page_count, int):
        for count in range(page_count):
            tm_params = params + 'sort=' + field_key + '&pagination[page]=' + str(
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
        write_log(page_count)'''


def get_ts_query(hashtag_group_id=sp_hashtag_group_id):
    hashtag_group_key = get_dict_key(sp_hashtag_group_dict, hashtag_group_id)
    ts_query = sp_read_conn('hashtag-groups/', hashtag_group_id + '?populate[0]=hashtags&populate[1]=searches&populate[2]=mentions')
    if type(ts_query) is dict and len(ts_query) != 0: # TODO check if it is len(sp_query['data])
        ts_query_body = ts_query['data']['attributes']['query']
        if len(ts_query['data']['attributes']['hashtags']['data']) > 20:
            failed_import_log(
                'Script terminated: number of hashtags in query ' + hashtag_group_key + ' (' + hashtag_group_id + ') exceed the limit of 20')
            write_log(
                'Script terminated: number of hashtags in query ' + hashtag_group_key + ' (' + hashtag_group_id + ') exceed the limit of 20')
            exit()
        if len(ts_query['data']['attributes']['hashtags']['data']):
            ts_query_body['search']['text_tags'] = []
            for hashtag in ts_query['data']['attributes']['hashtags']['data']:
                h_dict = {
                    'type': 'hashtag',
                    'value': hashtag['attributes']['text'],
                    'action': 'should'
                }
                ts_query_body['search']['text_tags'].append(h_dict)
        else:
            write_log('No hashtag in query ' + hashtag_group_key + ' (' + hashtag_group_id + ')')
        if len(ts_query['data']['attributes']['mentions']['data']):
            if not ts_query_body['search']['text_tags']:
                ts_query_body['search']['text_tags'] = []
            if len(ts_query['data']['attributes']['mentions']['data']) > 20:
                failed_import_log(
                    'Script terminated: number of mentions in query ' + hashtag_group_key + ' (' + hashtag_group_id + ') exceed the limit of 20')
                write_log(
                    'Script terminated: number of mentions in query ' + hashtag_group_key + ' (' + hashtag_group_id + ') exceed the limit of 20')
                exit()
            for mention in ts_query['data']['attributes']['mentions']['data']:
                m_dict = {
                    'type': 'mention',
                    'value': mention['attributes']['text'],
                    'action': 'should'
                }
                ts_query_body['search']['text_tags'].append(m_dict)
        else:
            '''if len(ts_query['data']['attributes']['searches']['data']):
                search_str = ''
                for search in ts_query['data']['attributes']['searches']['data']:
                    search_str = search_str + ' ' + search['attributes']['text']
                ts_query_body['search']['relevance']['value'] = search_str
                ts_query_body['search']['relevance']['weight'] = 0.5
                ts_query_body['search'].update({"modules": [{"filter": "relevance", "action": "should"}]})
            else:
                write_log('No searches in query ' + hashtag_group_key + ' (' + hashtag_group_id + ')')'''
        return ts_query_body
    else:
        failed_import_log(
            'Script terminated: Strapi query ' + hashtag_group_key + ' (' + hashtag_group_id + ') failed with request code ' + str(
                ts_query))
        write_log(
            'Script terminated: Strapi query ' + hashtag_group_key + ' (' + hashtag_group_id + ') failed with request code ' + str(
                ts_query))
        exit()


def get_import_file_list(folder):
    file_list = os.listdir(folder)
    new_list = [item for item in file_list if item.startswith('hg_')]
    new_list.sort()
    return new_list
