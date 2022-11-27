from utilities import *
import re
import pywordsegment

# test_string_to_be_cleaned = = 'ad/gifted- 24⁣⁣ """inurbeautyuk""" bluebananas.bottles... el_arturo_moran⁠ test.test.test. arizonabypatrizia⁣, /testSlash #testSquare] #testRound) TEst #x#y#z artistic_unity_ aspirante?????? auguri!!!baby__lover___ babyginni,con babyginni. baitadibabbonatale…rimanete battesimosveva&gregorio beauty-case beautygirl, bebe_bebe11 bebè bebé bebénoel bebê f**kcovid'


def clean_text(text):
    text = text.lower()
    text = remove_symbols(text)
    text = text.replace('...', ' ').replace('#*', '#').replace('..', '.').replace('#/', '#').replace('/', ' ').replace('~', ' ')  # corrects special combination of characters
    text = f" #".join(text.split('#'))  # splits words with multiple hashtag
    text = " ".join(text.split())  # removes multiple space
    text_list = text.split()
    text_list = [re.sub(r'[!?)">•+:,…\[\]\(\)$]', '', w) for w in text_list]  # removes selected special characters inside the word
    text_list = [w[:-1] if w.endswith('.') else w for w in text_list]  # removes dot punctuation just if at the end of the word
    text_list = [w[:-1] if w.endswith('*') else w for w in text_list]
    return text_list


def get_items_from_caption(post_dict, character, accepted_list, discarted_list, data_folder):
    if post_dict['caption']:
        text = post_dict['caption'].replace("\n", " ")
        text_list = clean_text(text)
        items_list = [w.lstrip(character) for w in text_list if
                      w.startswith(character) and len(w.lstrip(character)) > 1 and w.lstrip(character) not in
                      nltk_stopwords[data_folder]]
        discarted_items_list = [w.lstrip(character) for w in text_list if
                                w.startswith(character) and len(w.lstrip(character)) == 1 or w.lstrip(character) in
                                nltk_stopwords[data_folder]]
        if items_list:
            accepted_list.extend(items_list)
            discarted_list.extend(discarted_items_list)
            file = DATA_IMPORT_PATH + data_folder + '_posts_with_' + character_dict[character] + '.csv'
            with open(file, 'a', encoding='utf8') as f:
                write = csv.writer(f, delimiter='\n')
                post_id = [post_dict['id']]
                write.writerow(post_id)
            write_log('Caption "' + text[:30] + '..." in post ' + post_dict['id'] + ' imported')
    else:
        file = DATA_IMPORT_PATH + data_folder + '_posts_without_' + character_dict[character] + '.csv'
        with open(file, 'a', encoding='utf8') as f:
            write = csv.writer(f, delimiter='\n')
            post_id = [post_dict['id']]
            write.writerow(post_id)
        write_log('No caption in post ' + post_dict['id'])


def get_items_from_posts(data_path, data_folder, character):
    items_from_posts = []
    discarted_items_from_posts = []
    missing_post_files = []
    influ_folder_list = get_influ_folder_list(data_path)
    for folder_name in influ_folder_list:
        post_json_file = data_path + folder_name + '/posts.json'
        if os.path.isfile(post_json_file) and (os.path.getsize(post_json_file) != 0):
            with open(post_json_file, encoding='utf8') as json_file:
                posts_list = json.load(json_file)
                for post_dict in posts_list:
                    get_items_from_caption(post_dict, character, items_from_posts, discarted_items_from_posts,
                                           data_folder)
        else:
            write_log('posts.json missing for account ' + folder_name)
            failed_import_log('posts.json missing for account ' + folder_name)
            missing_post_files.append(folder_name)
    items_from_posts = [i for i in items_from_posts if i]
    unique_items_from_posts_list = list(set(items_from_posts))
    if len(unique_items_from_posts_list) > 0:
        unique_items_from_posts_list.sort()
        list_to_csv(unique_items_from_posts_list,
                    DATA_IMPORT_PATH + data_folder + '_' + character_dict[character] + '_from_posts.csv')
        write_log(data_folder + " - " + str(len(unique_items_from_posts_list)) + ' new ' + character_dict[character] + ' found')
        discarted_unique_items_from_posts_list = list(set(discarted_items_from_posts))
        discarted_unique_items_from_posts_list.sort()
        list_to_csv(discarted_unique_items_from_posts_list,
                    DATA_IMPORT_PATH + data_folder + '_discarted_' + character_dict[character] + '_from_posts.csv')




def merge_list_of_new_items(file_list, character, save_file):
    # merge the lists and get the UNIQUE values to add to strapi.
    complete_list = []
    complete_dict = []
    sp_items_list = csv_to_list(DATA_STRAPI_PATH + 'sp_' + character_dict[character] + '.csv')
    for file in file_list:
        tmp_list = csv_to_list(DATA_IMPORT_PATH + file)
        complete_list.extend(tmp_list)
        if character == '#':
            for item in tmp_list:
                just_letters = re.sub(r'[^a-zA-Z]', '', item)
                word_segment_list = pywordsegment.WordSegmenter.segment(text=just_letters)
                word_segment = ' '.join(word_segment_list)
                detect_language = fasttext_language_predict(word_segment)
                language = detect_language[0][0][0].replace('__label__', '')
                lan_probability = detect_language[1][0][0]
                item_dict = {"item": item, "segment": word_segment, "language": language, "probability": str(lan_probability)}
                complete_dict.append(item_dict)
    unique_items_list = list(set(complete_list))
    unique_items_without_sp_items_list = list_diff(unique_items_list, sp_items_list)
    unique_items_without_sp_items_list.sort()
    list_to_csv(unique_items_without_sp_items_list, DATA_IMPORT_PATH + save_file + '.csv')
    '''if character == '#':
        data_to_json(complete_dict, DATA_ANALYSIS_PATH + save_file + '_language.json')'''
    write_log(str(len(complete_list)) + ' new ' + character_dict[character] + ' from merged files')
    write_log(str(len(unique_items_list)) + ' new unique ' + character_dict[character] + ' from merged files without strapi hashtags')
    write_log('File ' + DATA_IMPORT_PATH + save_file + '.csv updated')
    '''if character == '#':
        write_log('File ' + DATA_ANALYSIS_PATH + save_file + '_language.json updated')'''


def sp_add_hashtag(hashtag):
    sp_dict = {
        "data": dict(
            text=hashtag
        )
    }
    try:
        sp_query = sp_write_conn(json.dumps(sp_dict), 'hashtags', '')
        return sp_query
    except Exception as e:
        return repr(e)


def update_sp_hashtags(csv_file):
    sp_new_item_counter = 0
    sp_failed_import_counter = 0
    import_items = []
    failed_import_items = []
    hashtag_list = csv_to_list(DATA_IMPORT_PATH + csv_file)
    for hashtag in hashtag_list:
        sp_res = sp_add_hashtag(hashtag)
        if type(sp_res) is dict and len(sp_res['data']) != 0:
            sp_new_item_counter += 1
            write_log('Success -- hashtag ' + hashtag + ' imported to Strapi')
            import_items.append(hashtag)
        else:
            sp_failed_import_counter += 1
            write_log('Failed -- hashtag ' + hashtag + ' not imported to Strapi ' + str(sp_res))
            failed_import_log('Failed -- hashtag ' + hashtag + ' not imported to Strapi ' + str(sp_res))
            failed_import_items.append(hashtag)
    import_items.sort()
    failed_import_items.sort()
    list_to_csv(import_items, DATA_STRAPI_PATH + 'import_hashtags.csv')
    list_to_csv(failed_import_items, DATA_STRAPI_PATH + 'failed_import_hashtags.csv')
    write_log(str(sp_new_item_counter) + ' new hashtags imported to Strapi')
    write_log(str(sp_failed_import_counter) + ' failed imports to Strapi. Check failed_import_hashtags file')


def sp_add_mention(mention):
    sp_dict = {
        "data": dict(
            text=mention
        )
    }
    try:
        sp_query = sp_write_conn(json.dumps(sp_dict), 'mentions', '')
        return sp_query
    except Exception as e:
        return repr(e)


def update_sp_mentions(csv_file):
    sp_new_item_counter = 0
    sp_failed_import_counter = 0
    import_items = []
    failed_import_items = []
    mention_list = csv_to_list(DATA_IMPORT_PATH + csv_file)
    for mention in mention_list:
        sp_res = sp_add_mention(mention)
        if type(sp_res) is dict and len(sp_res['data']) != 0:
            sp_new_item_counter += 1
            write_log('Success -- mention ' + mention + ' imported to Strapi')
            import_items.append(mention)
        else:
            sp_failed_import_counter += 1
            write_log('Failed -- mention ' + mention + ' not imported to Strapi ' + str(sp_res))
            failed_import_log('Failed -- mention ' + mention + ' not imported to Strapi ' + str(sp_res))
            failed_import_items.append(mention)
    import_items.sort()
    failed_import_items.sort()
    list_to_csv(import_items, DATA_STRAPI_PATH + 'import_mentions.csv')
    list_to_csv(failed_import_items, DATA_STRAPI_PATH + 'failed_import_mentions.csv')
    write_log(str(sp_new_item_counter) + ' new mentions imported to Strapi')
    write_log(str(sp_failed_import_counter) + ' failed imports to Strapi. Check failed_import_mentions file')
