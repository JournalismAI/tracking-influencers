from utilities import *
import csv


def create_brand_csv(file_list):
    csv_file = DATA_IMPORT_PATH + 'unique_brands.csv'
    try:
        list_to_csv(file_list, csv_file)
        write_log('File ' + csv_file + ' updated')
    except Exception as e:
        msg = 'Script create_brand_csv failed on file  ' + csv_file + ': ' + repr(e)
        failed_import_log(msg)
        write_log(msg)


def update_sp_brands():
    with open(DATA_IMPORT_PATH + 'profile_brand_data.json') as json_file:
        brands_dict = json.load(json_file)
    sp_list = read_csv(DATA_STRAPI_PATH + 'brands.csv')
    import_list = read_csv(DATA_IMPORT_PATH + 'unique_brands.csv')
    items_diff = list_diff(import_list, sp_list)
    new_items = [it for it in items_diff if it != []]
    new_import_items = []
    if new_items and len(new_items) > 0:
        failed_import_brand_dict = []
        failed_import_brand_slugs = []
        failed_import_brand_names = []
        new_sp_item_counter = 0
        new_import_item_counter = 0
        failed_import_counter = 0
        for item in new_items:
            sp_item = str(item[0])
            if item not in sp_list and brands_dict[sp_item]['org_name'] != 'NULL':
                sp_dict = {
                    'data': {
                        'name': brands_dict[sp_item]['brand_name'],
                        'slug': brands_dict[sp_item]['org_slug'],
                        "platforms": ["1"]  # instagram
                    }
                }
                if brands_dict[sp_item]['brand_bio']:
                    sp_dict['data']['bio'] = brands_dict[sp_item]['brand_bio']
                if brands_dict[sp_item]['brand_picture']:
                    sp_dict['data']['picture'] = brands_dict[sp_item]['brand_picture']
                try:
                    sp_query = sp_write_conn(json.dumps(sp_dict), 'brands')
                    # if (type(sp_query) is dict and len(sp_query) != 0) or sp_query != '500':
                    if type(sp_query) is dict and len(sp_query) != 0:
                        new_sp_item_counter += 1
                        write_log('Success -- brand ' + sp_item + ' imported to Strapi')
                    else:
                        failed_import_brand_dict.append(sp_dict)
                        failed_import_brand_slugs.append(brands_dict[sp_item]['org_slug'])
                        failed_import_brand_names.append(brands_dict[sp_item]['brand_name'])
                        failed_import_counter += 1
                        msg = 'Failed -- brand ' + sp_item + ' import to Strapi failed: ' + str(sp_query)
                        failed_import_log(msg)
                        write_log(msg)
                except Exception as e:
                    msg = 'Script update_sp_brands failed. Brand import to Strapi failed: ' + repr(e)
                    failed_import_log(msg)
                    write_log(msg)
            elif item not in import_list:
                new_import_items.append(item[0])
                new_import_item_counter += 1
        new_import_items.sort()
        failed_import_brand_slugs.sort()
        failed_import_brand_names.sort()
        list_to_csv(new_import_items, DATA_IMPORT_PATH + 'missing_import_brands.csv')
        list_to_csv(failed_import_brand_slugs, DATA_IMPORT_PATH + 'failed_import_brand_slugs.csv')
        list_to_csv(failed_import_brand_names, DATA_IMPORT_PATH + 'failed_import_brand_names.csv')
        data_to_json(failed_import_brand_dict, DATA_IMPORT_PATH + 'failed_import_brand_dict.json')
        write_log(str(new_sp_item_counter) + ' new brands imported to Strapi')
        write_log(str(new_import_item_counter) + ' brands in Strapi but missing in import file')
        write_log(str(failed_import_counter) + ' Strapi imports failed. Check failed_import_brand_* files')
    else:
        write_log('No new brand to add to Strapi')


