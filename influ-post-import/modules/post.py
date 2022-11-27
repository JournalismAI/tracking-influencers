from utilities import *
from time import sleep
from modules.hashtag_mention import *
from anyascii import anyascii
import re


def get_sp_account(account_username):
    try:
        sp_dict = sp_read_conn('accounts', '?populate=*&filters[username]=' + account_username)
        return sp_dict
    except Exception as e:
        return repr(e)


def get_sp_post(post_id):
    try:
        sp_dict = sp_read_conn('posts', '?populate=*&filters[post_id]=' + post_id)
        return sp_dict
    except Exception as e:
        return repr(e)


def remove_hashtag_and_mention(text):
    text_list = text.split()
    new_text_list = [w for w in text_list if not w.startswith('#') and not w.startswith('@')]
    return " ".join(new_text_list)


def clean_text_4_lang(text):
    text = re.sub(r'http\S+', '', text) # remove url
    text = remove_symbols(text)
    text = text.replace(":", " ").replace(".", " ").replace("~", " ").replace("*", " ").replace("  ", " ")
    return text


def get_hashtag_mention_from_caption(caption, character, data_folder):
    item_dict = {"valid": "", "disc": ""}
    text = caption.replace("\n", " ")
    text_list = clean_text(text)
    items_list = [w.lstrip(character) for w in text_list if
                  w.startswith(character) and len(w.lstrip(character)) > 1 and w.lstrip(character) not in
                  nltk_stopwords[data_folder]]
    discarted_items_list = [w.lstrip(character) for w in text_list if
                            w.startswith(character) and len(w.lstrip(character)) == 1 or w.lstrip(character) in
                            nltk_stopwords[data_folder]]
    if items_list:
        item_dict['valid'] = ", ".join(items_list)
    if discarted_items_list:
        item_dict['disc'] = ", ".join(discarted_items_list)
    return item_dict


def add_hashtags_to_post(hashtag_list, endpoint, params='', token=STRAPI_API_TOKEN_WRITE):
    query_conn = STRAPI_API_ENDPOINT + endpoint + params
    sp_dict = {
        "data": dict(
            hashtags=hashtag_list
        )
    }
    '''try:
        sp_query = requests.put(query_conn, data=json.dumps(sp_dict).encode('utf-8'),
                                headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}",
                                         'charset': 'utf-8'})
        return sp_dict
    except Exception as e:
        return repr(e)'''


def sp_add_post(post, account_id_list):
    sp_dict = { # TODO add owner_username and owner_IG_id
        "data": dict(
            post_id=post['id'],
            caption=post['caption'],
            url=post['url'],
            image_url=post['imageUrl'],
            image_filename=post['file'],
            is_video=post['isVideo'],
            comments_count=post['commentsCount'],
            likes_count=post['likesCount'],
            date=post['date'],
            should_request_ads=post['should_request_ads'],
            commerciality_status=post['commerciality_status'],
            is_paid_partnership=post['is_paid_partnership'],
            product_type=post['product_type'],
            account=account_id_list
        )
    }
    if post['locationName'] != 'null':
        sp_dict['data']['location_name'] = post['locationName']
    if post['location'] != 'null':
        sp_dict['data']['location_url'] = post['location']
    if post['lat'] != 'null':
        sp_dict['data']['lat'] = post['lat']
    if post['lng'] != 'null':
        sp_dict['data']['lng'] = post['lng']
    return sp_dict
    '''try:
        sp_query = sp_write_conn(json.dumps(sp_dict), 'posts', '')
        return sp_dict
    except Exception as e:
        return repr(e)'''


def update_sp_post(data_path):
    sp_post_imported_counter = 0
    sp_post_failed_import_counter = 0
    sp_post_already_imported_counter = 0
    sp_account_not_found_counter = 0
    sp_missing_post_file_counter = 0
    import_posts = []
    failed_import_posts = []
    already_imported_posts = []
    not_found_accounts = []
    missing_post_files = []
    influ_folder_list = get_influ_folder_list(data_path)
    for folder_name in influ_folder_list:
        post_json_file = data_path + folder_name + '/posts.json'
        if os.path.isfile(post_json_file) and (os.path.getsize(post_json_file) != 0):
            sp_account_dict = get_sp_account(folder_name)
            if len(sp_account_dict['data']) != 0:  # TODO if strapi post content-type is empty
                sp_account_list = [sp_account_dict['data'][0]['id']]
                with open(post_json_file, encoding='utf8') as json_file:
                    posts_list = json.load(json_file)
                    for post_dict in posts_list:
                        sp_post_dict = get_sp_post(post_dict['id'])
                        if type(sp_post_dict) is dict and len(sp_post_dict['data']) == 0:
                            sp_res = sp_add_post(post_dict, sp_account_list)
                            if type(sp_res) is dict and len(sp_res['data']) != 0:
                                sp_post_imported_counter += 1
                                write_log('Success -- post ' + post_dict[
                                    'id'] + ' of account ' + folder_name + ' imported to Strapi')
                                import_posts.append([folder_name, post_dict['id']])
                                # add_hashtags_mentions(post_dict)
                            else:
                                sp_post_failed_import_counter += 1
                                write_log('Failed -- account ' + folder_name + ' -- post ' + post_dict[
                                    'id'] + ' not imported to Strapi ' + str(sp_res))
                                failed_import_log('Failed -- account ' + folder_name + ' -- post ' + post_dict[
                                    'id'] + ' not imported to Strapi ' + str(sp_res))
                                failed_import_posts.append([folder_name, post_dict['id']])
                        else:
                            write_log(
                                'Post ' + post_dict['id'] + ' in account ' + folder_name + ' already exist in Strapi')
                            failed_import_log(
                                'Post ' + post_dict['id'] + ' in account ' + folder_name + ' already exist in Strapi')
                            already_imported_posts.append([folder_name, post_dict['id']])
                        sleep(.5)
            else:
                write_log('Account ' + folder_name + ' not found in Strapi')
                failed_import_log('Account ' + folder_name + ' not found in Strapi')
                not_found_accounts.append(folder_name)
        else:
            sp_account_not_found_counter += 1
            sp_post_failed_import_counter += 1
            write_log('posts.json missing for account ' + folder_name)
            failed_import_log('posts.json missing for account ' + folder_name)
            missing_post_files.append(folder_name)
    import_posts.sort()
    failed_import_posts.sort()
    list_to_csv(import_posts, DATA_STRAPI_PATH + 'import_posts.csv')
    list_to_csv(failed_import_posts, DATA_STRAPI_PATH + 'failed_import_posts.csv')
    list_to_csv(already_imported_posts, DATA_STRAPI_PATH + 'already_imported_posts.csv')
    list_to_csv(not_found_accounts, DATA_STRAPI_PATH + 'not_found_accounts.csv')
    list_to_csv(missing_post_files, DATA_STRAPI_PATH + 'missing_post_files.csv')
    write_log(str(sp_post_imported_counter) + ' new posts imported to Strapi. Check import_posts.csv file')
    write_log(str(sp_post_failed_import_counter) + ' failed imports to Strapi. Check failed_import_posts.csv file')
    write_log(str(sp_account_not_found_counter) + ' accounts not found in Strapi. Check not_found_accounts.csv file')
    write_log(
        str(sp_post_already_imported_counter) + ' posts already imported to Strapi. Check already_imported_posts.csv file')
    write_log(
        str(sp_missing_post_file_counter) + ' accounts having no posts.json file. Check missing_post_files.csv file')


def create_posts_csv(data_path, data_folder):
    data_analysis_path = DATA_ANALYSIS_PATH + data_folder
    items_list = []
    failed_items_list = []
    failed_accounts_list = []
    influ_folder_list = get_influ_folder_list(data_path)
    with open(data_analysis_path + '_accounts_IG_id.json') as json_file:
        account_ig_id_dict = json.load(json_file)
    for folder_name in influ_folder_list:
        post_json_file = data_path + folder_name + '/posts.json'
        if os.path.isfile(post_json_file) and (os.path.getsize(post_json_file) != 0):
            with open(post_json_file) as json_file:
                posts_dict = json.load(json_file)
                for post in posts_dict:
                    if post['ownerId'] in account_ig_id_dict.keys():
                        account_username = account_ig_id_dict[post['ownerId']]
                        owner_username = account_username
                    else:
                        account_username = get_dict_key(account_ig_id_dict, folder_name)
                        owner_username = post['ownerUsername']
                        failed_accounts_list.append(post['ownerId'])
                        write_log('Failed -- account ' + post['ownerId'] + ' not found')
                    caption = ""
                    norm_caption = ""
                    hashtags_dict = {"valid": "", "disc": ""}
                    mentions_dict = {"valid": "", "disc": ""}
                    language = ""
                    if post['caption']:
                        caption = post['caption'].replace("\n", " ").replace("  ", " ")
                        raw_caption = remove_hashtag_and_mention(caption)
                        norm_caption = anyascii(raw_caption)
                        lang_caption = clean_text_4_lang(norm_caption)
                        detect_language = fasttext_language_predict(lang_caption)
                        language = detect_language[0][0][0].replace('__label__', '')
                        lan_probability = detect_language[1][0][0]
                        hashtags_dict = get_hashtag_mention_from_caption(caption, '#', data_folder)
                        mentions_dict = get_hashtag_mention_from_caption(caption, '@', data_folder)
                    item_dict = {
                        "account": account_username,
                        "owner_id": post['ownerId'],
                        "owner_username": owner_username,
                        "post_id": post['id'],
                        "post_code": post['shortCode'],
                        "date": post['date'],
                        "caption": caption,
                        "norm_caption": norm_caption,
                        "lang_caption": lang_caption,
                        "language": language,
                        "hashtags": hashtags_dict['valid'],
                        "mentions": mentions_dict['valid'],
                        "discarted_hashtags": hashtags_dict['disc'],
                        "discarted_mentions": mentions_dict['disc'],
                        "commentsCount": post['commentsCount'],
                        "likesCount": post['likesCount'],
                        "is_video": post['isVideo'],
                        "location_name": post['locationName'],
                        "latitude": post['lat'],
                        "longitude": post['lng'],
                        "product_type": post['product_type'],
                        "is_paid_partnership": post['is_paid_partnership'],
                        "commerciality_status": post['commerciality_status'],
                        "should_request_ads": post['should_request_ads']
                    }
                    items_list.append(item_dict)
                    write_log('Post ' + post['id'] + ' found')
        else:
            failed_items_list.append(folder_name)
            write_log('Failed -- post of account ' + folder_name + ' not found')
    csv_post_header = list(items_list[0].keys())
    with open(data_analysis_path + '_posts.csv', 'w+', encoding='utf8', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(csv_post_header)
        for item_dict in items_list:
            writer.writerow(item_dict.values())
    failed_posts_num_list = failed_accounts_list
    failed_items_list = list(set(failed_items_list))
    failed_accounts_list = list(set(failed_accounts_list))
    failed_items_list.sort()
    failed_accounts_list.sort()
    list_to_csv(failed_items_list, data_analysis_path + '_failed_posts.csv')
    list_to_csv(failed_accounts_list, data_analysis_path + '_failed_accounts_from_posts.csv')
    write_log(str(len(items_list)) + ' posts found')
    write_log(str(len(failed_items_list)) + ' posts not found')
    write_log(str(len(failed_posts_num_list)) + ' posts with accounts id not found in account username list (' + data_folder + '_accounts_IG_id.json file)')
    write_log(str(len(failed_accounts_list)) + ' accounts id not found in account username list (' + data_folder + '_accounts_IG_id.json file)')
    write_log('File ' + data_analysis_path + '_posts.csv updated')
    write_log('File ' + data_analysis_path + '_failed_posts.csv updated')
    write_log('File ' + data_analysis_path + '_failed_accounts_from_posts.csv updated')
