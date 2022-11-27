from modules.influ import *
from modules.post import *
from modules.hashtag_mention import *


print("Choose folder:\n"
      "    0. kids-sole\n"
      "    1. kids-sky-news\n"
      "    2. kids-infobae\n"
      "    t. test\n",
      "    s. Skip this step\n")
folder_input = input("Choose folder number: ")
# folder_input = "2"

if folder_input == '0':
    DATA_FOLDER = 'kids-sole'
elif folder_input == '1':
    DATA_FOLDER = 'kids-sky-news'
elif folder_input == '2':
    DATA_FOLDER = 'kids-infobae'
elif folder_input == 't':
    DATA_FOLDER = 'test'
elif folder_input == 's':
    DATA_FOLDER = "-"
else:
    print("Folder does not exist")

DATA_INFLU_PATH = DATA_INFLU_PATH + DATA_FOLDER + "/"


action_dict = {
    "0": "Get new influencers from posts",
    "1": "Add influencers to Strapi",
    "2": "Get new hashtags from posts",
    "3": "Get new mentions from posts",
    "4": "Merge all UNIQUE new hashtags",
    "5": "Merge all UNIQUE mentions",
    "6": "Add new hashtags in STRAPI",
    "7": "Add new mentions in STRAPI",
    "8": "Add posts to Strapi",
    "9": "Create accounts IG_id json",
    "10": "Create profiles and posts csv",
    "e": "Empty logs",
    "*": "Test"
}

print("Actions:")
for key, val in action_dict.items():
    print(f"    {key}. {val}")
print("\n")
action_input = input("Insert action number: ")
#action_input = "10"


def actions(action):
    if action == '0':
        get_sp_items('accounts',  'sp_accounts.csv', 'sp_accounts_id.json', params='?', page_size='100', field_key='username')
        get_accounts(DATA_INFLU_PATH, DATA_FOLDER)  # TODO: make diff between strapi list and local list of accounts
        pass
    elif action == '1':
        update_sp_influ(DATA_INFLU_PATH)
    elif action == '2':
        get_sp_items('hashtags', 'sp_hashtags.csv', 'sp_hashtags_id.json', params='?', page_size='100', field_key='text')
        get_items_from_posts(DATA_INFLU_PATH, DATA_FOLDER, '#')
    elif action == '3':
        get_sp_items('mentions', 'sp_mentions.csv', 'sp_mentions_id.json', params='?', page_size='100', field_key='text')
        get_items_from_posts(DATA_INFLU_PATH, DATA_FOLDER, '@')
    elif action == '4':
        file_list = ['kids-sole_hashtags_from_posts.csv', 'kids-sky-news_hashtags_from_posts.csv', 'kids-infobae_hashtags_from_posts.csv']
        merge_list_of_new_items(file_list, '#', 'new_hashtags_to_add_sp')
    elif action == '5':
        file_list = ['kids-sole_mentions_from_posts.csv', 'kids-sky-news_mentions_from_posts.csv', 'kids-infobae_mentions_from_posts.csv']
        merge_list_of_new_items(file_list, '@', 'new_mentions_to_add_sp')
    elif action == '6':
        update_sp_hashtags('new_hashtags_to_add_sp.csv')
    elif action == '7':
        update_sp_mentions('new_mentions_to_add_sp.csv')
    elif action == '8':
        update_sp_post(DATA_INFLU_PATH)
    elif action == '9':
        create_accounts_IG_id_json(DATA_INFLU_PATH, DATA_FOLDER)
    elif action == '10':
        create_profiles_csv(DATA_INFLU_PATH, DATA_FOLDER)
        create_posts_csv(DATA_INFLU_PATH, DATA_FOLDER)
    elif action == 'e':
        empty_file(strapi_import_log)
        empty_file(strapi_failed_import_log)
    elif action == '*':
        pass
    else:
        print("Action not allowed")


print(f"Selected folder: {DATA_FOLDER} - Action: {action_dict[action_input]}")
confirm_input = input("Proceed? (y/n): ")


if confirm_input == 'y':
    print("Script starts")
    actions(action_input)
elif confirm_input == 'n':
    print("Script stops")
    exit()
else:
    print("Action not allowed")


