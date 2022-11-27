from utilities import *
from slug import slug
from anyascii import anyascii  

# unicode to ascii such as 𝘔𝘶𝘭𝘵𝘪𝘭𝘪𝘯𝘨𝘶𝘢𝘭 𝘮𝘰𝘮 𝘰𝘧 𝘵𝘸𝘰 𝘨𝘪𝘳𝘭𝘴 👩‍👧‍👧 𝐉𝐞𝐭𝐚 𝐞 𝐧𝐣𝐞 𝐍𝐞𝐧𝐞 | 𝐒𝐡𝐤𝐫𝐢𝐦𝐞 | 𝐊𝐞𝐬𝐡𝐢𝐥𝐥𝐚 🤱🏽🤰🏽 𝗞𝗼𝗻𝘀𝘂𝗹𝗲𝗻𝘁𝗲 𝗽𝗲𝗿 𝗚𝗿𝗮𝘁𝗲 𝗱𝗵𝗲 𝗡𝗲𝗻𝗮𝘁 𝗻𝗲 𝗗𝗶𝗮𝘀𝗽𝗼𝗿 👩‍💻 𝘗𝘳𝘦𝘯𝘰𝘵𝘰 𝘬𝘰𝘯𝘴𝘶𝘭𝘵𝘦𝘯 𝘵𝘦𝘯𝘥𝘦 ⤵️


def get_sp_account(account_username):
    try:
        sp_dict = sp_read_conn('accounts', '?populate=*&filters[username]=' + account_username)
        if type(sp_dict) is dict and len(sp_dict) != 0:
            return sp_dict
        else:
            return ''
    except Exception as e:
        return repr(e)


def get_accounts(data_path, data_folder):
    influ_folder_list = get_influ_folder_list(data_path)
    list_to_csv(influ_folder_list, DATA_IMPORT_PATH + data_folder + '_accounts_from_posts.csv')
    write_log(str(len(influ_folder_list)) + ' accounts found in folder ' + data_folder)


def sp_add_influencer(profile, account_id_list):
    sp_dict = {
        "data": dict(
            full_name=profile['fullName'],
            slug=slug(profile['fullName']) + '--' + profile['id'],
            short_description=profile['biography'],
            accounts=account_id_list
        )
    }
    print("CHECK influ.py before proceed")
    return sp_dict
    '''try:
        sp_query = sp_write_conn(json.dumps(sp_dict), 'influencers', '')
        return sp_dict
    except Exception as e:
        return repr(e)'''


def update_sp_influ(data_path):
    sp_new_item_counter = 0
    sp_failed_import_counter = 0
    sp_missing_account_counter = 0
    import_usernames = []
    failed_import_usernames = []
    missing_accounts = []
    influ_folder_list = get_influ_folder_list(data_path)  # TODO change with diff list between strapi list and local list of accounts
    for folder_name in influ_folder_list:
        profile_json_file = data_path + folder_name + '/profile.json'
        if os.path.isfile(profile_json_file) and (os.path.getsize(profile_json_file) != 0):
            sp_account_dict = get_sp_account(folder_name)
            if len(sp_account_dict) != 0:
                sp_account_list = [sp_account_dict['data'][0]['id']]
                with open(profile_json_file) as json_file:
                    profile_dict = json.load(json_file)
                    sp_res = sp_add_influencer(profile_dict, sp_account_list)
                    if type(sp_res) is dict and len(sp_res['data']) != 0:
                        sp_new_item_counter += 1
                        write_log('Success -- influencer ' + profile_dict['fullName'] + ' of account ' + folder_name + ' imported to Strapi')
                        import_usernames.append(folder_name)
                    else:
                        sp_failed_import_counter += 1
                        write_log('Failed -- account ' + folder_name + ' -- influencer not imported to Strapi ' + str(sp_res))
                        failed_import_log('Failed -- account ' + folder_name + ' -- influencer not imported to Strapi ' + str(sp_res))
                        failed_import_usernames.append(folder_name)
            else:
                write_log('Account ' + folder_name + ' not found in Strapi')
                failed_import_log('Account ' + folder_name + ' not found in Strapi')
                failed_import_usernames.append(folder_name)
                missing_accounts.append(folder_name)
        else:
            sp_missing_account_counter += 1
            sp_failed_import_counter += 1
            write_log('profile.json missing for account ' + folder_name)
            failed_import_log('profile.json missing for account ' + folder_name)
            failed_import_usernames.append(folder_name)
    import_usernames.sort()
    failed_import_usernames.sort()
    list_to_csv(import_usernames, DATA_STRAPI_PATH + 'import_influencers.csv')
    list_to_csv(failed_import_usernames, DATA_STRAPI_PATH + 'failed_import_influencers.csv')
    write_log(str(sp_new_item_counter) + ' new influencers imported to Strapi')
    write_log(str(sp_failed_import_counter) + ' failed imports to Strapi. Check failed_import_influencers file')
    write_log(str(sp_missing_account_counter) + ' accounts not found in Strapi. Check missing_accounts file')


def create_accounts_IG_id_json(data_path, data_folder):
    items_dict = {}
    failed_items_list = []
    influ_folder_list = get_influ_folder_list(data_path)
    for folder_name in influ_folder_list:
        profile_json_file = data_path + folder_name + '/profile.json'
        if os.path.isfile(profile_json_file) and (os.path.getsize(profile_json_file) != 0):
            with open(profile_json_file) as json_file:
                profile_dict = json.load(json_file)
                item_dict = {profile_dict['id']: folder_name}
                items_dict.update(item_dict)
                write_log('Account ' + folder_name + 'and id ' + profile_dict['id'] + ' found')
        else:
            failed_items_list.append(folder_name)
            write_log('Failed -- Account ' + folder_name + 'not found')
    data_to_json(items_dict, DATA_ANALYSIS_PATH + data_folder + '_accounts_IG_id.json')
    failed_items_list.sort()
    list_to_csv(failed_items_list, DATA_ANALYSIS_PATH + data_folder + '_failed_accounts_IG_id.csv')
    write_log(str(len(items_dict)) + ' accounts found')
    write_log(str(len(failed_items_list)) + ' accounts not found')
    write_log('File ' + DATA_ANALYSIS_PATH + data_folder + '_accounts_IG_id.json updated')
    write_log('File ' + DATA_ANALYSIS_PATH + data_folder + '_failed_accounts_IG_id.csv updated')


def create_profiles_csv(data_path, data_folder):
    data_analysis_path = DATA_ANALYSIS_PATH + data_folder
    items_list = []
    failed_items_list = []
    failed_accounts_list = []
    influ_folder_list = get_influ_folder_list(data_path)
    for folder_name in influ_folder_list:
        profile_json_file = data_path + folder_name + '/profile.json'
        if os.path.isfile(profile_json_file) and (os.path.getsize(profile_json_file) != 0):
            with open(profile_json_file) as json_file:
                profiles_dict = json.load(json_file)
                biography = ""
                norm_bio = ""
                language = ""
                if profiles_dict['biography']:
                    biography = profiles_dict['biography'].lower().replace("\n", " ").replace("  ", " ")
                    norm_bio = anyascii(biography)
                    detect_language = fasttext_language_predict(norm_bio)
                    language = detect_language[0][0][0].replace('__label__', '')
                    lan_probability = detect_language[1][0][0]
                item_dict = {
                    "id": profiles_dict['id'],
                    "username": profiles_dict['username'],
                    "full_name": profiles_dict['fullName'],
                    "biography": biography,
                    "norm_biography": norm_bio,
                    "language": language,
                    "entities": profiles_dict['entities'],
                    "is_recent_user": profiles_dict['isRecentUser'],
                    "subscribers_count": profiles_dict['subscribersCount'],
                    "subscribtions": profiles_dict['subscribtions'],
                    "is_business_account": profiles_dict['isBusinessAccount'],
                    "business_contact": profiles_dict['businessContact'],
                    "business_category_name": profiles_dict['businessCategoryName'],
                    "category_name": profiles_dict['categoryName'],
                    "is_verified": profiles_dict['isVerified'],
                    "transparency_label": profiles_dict['transparencyLabel'],
                    "transparency_product": profiles_dict['transparencyProduct'],
                    "posts_count": profiles_dict['postsCount'],
                }
                items_list.append(item_dict)
                write_log('Profile ' + profiles_dict['username'] + ' found')
        else:
            failed_items_list.append(folder_name)
            write_log('Failed -- profile of account ' + folder_name + ' not found')
    csv_post_header = list(items_list[0].keys())
    with open(data_analysis_path + '_profiles.csv', 'w+', encoding='utf8', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(csv_post_header)
        for item_dict in items_list:
            writer.writerow(item_dict.values())
    failed_profiles_num_list = failed_accounts_list
    failed_items_list = list(set(failed_items_list))
    failed_accounts_list = list(set(failed_accounts_list))
    failed_items_list.sort()
    failed_accounts_list.sort()
    list_to_csv(failed_items_list, data_analysis_path + '_failed_profiles.csv')
    list_to_csv(failed_accounts_list, data_analysis_path + '_failed_accounts_from_profiles.csv')
    write_log(str(len(items_list)) + ' profiles found')
    write_log(str(len(failed_items_list)) + ' profiles not found')
    write_log('File ' + data_analysis_path + '_profiles.csv updated')
    write_log('File ' + data_analysis_path + '_failed_profiles.csv updated')
    write_log('File ' + data_analysis_path + '_failed_accounts_from_profiles.csv updated')
