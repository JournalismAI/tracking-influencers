from modules.tag import *
from modules.brand import *
from modules.organization import *
import os


print("Actions:\n"
      "    0. Create brand json file from profile_brands folder\n"
      "    1. Create brand tags csv from local brand folder\n"
      "    2. Create organization names csv from local brand folder\n"
      "    3. Create brands csv from local brand folder\n"
      "    4. Update Strapi seungbae brand tag (tags)\n"
      "    5. Update Strapi jaifp brand tag (tags)\n"
      "    6. Update Strapi brand social accounts\n"
      "    7. Update Strapi organizations\n"
      "   99. Clean failed import log file\n"
      "   ##. Clean import log file\n"
      "    *. Test\n")
action_input = input("Insert action number: ")
# action_input = "6"


if action_input == '0':
    create_brand_json_from_files()
    create_brand_org_slug_json()
elif action_input == '1':
    create_tag_csv(brand_file_list)
elif action_input == '2':
    create_org_csv(brand_file_list)
elif action_input == '3':
    create_brand_csv(brand_file_list)
elif action_input == '4':
    get_sp_api_endpoint('tags', '?sort=name&filters[type][$eq]=seungbae')
    update_sp_tags('seungbae')
    update_sp_item_id_json('tags', 'tags_id.json')
elif action_input == '5':
    print("TO DO")
elif action_input == '6':
    get_sp_api_endpoint('brands')
    update_sp_brands()
    update_sp_item_id_json('brands', 'brands_id.json')
elif action_input == '7':
    update_sp_item_id_json('tags', 'tags_id.json')
    update_sp_item_id_json('brands', 'brands_id.json')
    get_sp_api_endpoint('organizations', '?', '100', 'slug')
    update_sp_organizations()
    update_sp_item_id_json('organizations', 'orgs_id.json', '?', '100', 'slug')
elif action_input == '99':
    empty_file(strapi_failed_import_log)
elif action_input == '##':
    empty_file(strapi_import_log)
elif action_input == '*':
    pass
else:
    print("Action not allowed")
