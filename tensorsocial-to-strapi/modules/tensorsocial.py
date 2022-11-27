from utilities import *
import http.client
import json


def ts_read_conn(request_body):
    conn = http.client.HTTPSConnection(TS_API_CONN, timeout=10)
    headers = {'Content-Type': "application/json"}
    conn.request("POST", "/identification?api_token=" + TS_API_TOKEN, request_body, headers)
    return conn.getresponse()


def update_ts_query(query, limit, skip, hashtag_group_id=sp_hashtag_group_id, sort_direction='desc'):
    query['paging']['limit'] = limit
    query['paging']['skip'] = skip
    query['sort']['direction'] = sort_direction
    # query['search']['gender']['code'] = 'MALE/FEMALE/UNKNOWN'  # if hashtag group is population-sole
    return json.dumps(query)


def get_total_results(request_body):
    res = ts_read_conn(request_body)
    if (res.status == 200) and (res.reason == "OK"):
        ts_str = res.read().decode("utf-8")
        ts_dict = json.loads(ts_str)
        return ts_dict['total']
    else:
        failed_import_log(
            'Script terminated: TensorSocial query ' + sp_hashtag_group_key + ' (' + sp_hashtag_group_id + ') failed with request code ' + str(
                res.status) + ' - error message: ' + res.reason)
        write_log(
            'Script terminated: TensorSocial query ' + sp_hashtag_group_key + ' (' + sp_hashtag_group_id + ') failed with request code ' + str(
                res.status) + ' - error message: ' + res.reason)
        exit()


def payload_influ(request_body):
    res = ts_read_conn(request_body)
    if (res.status == 200) and (res.reason == "OK"):
        ts_str = res.read().decode("utf-8")
        ts_dict = json.loads(ts_str)
        return ts_dict
    else:
        failed_import_log(
            'Script terminated: TensorSocial query ' + sp_hashtag_group_key + ' (' + sp_hashtag_group_id + ') failed with request code ' + str(
                res.status) + ' - error message: ' + res.reason)
        write_log(
            'Script terminated: TensorSocial query ' + sp_hashtag_group_key + ' (' + sp_hashtag_group_id + ') failed with request code ' + str(
                res.status) + ' - error message: ' + res.reason)
        exit()
