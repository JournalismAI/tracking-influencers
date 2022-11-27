from utilities import *
import os
import csv
from slugify import slugify


def create_tag_csv(file_list):
    no_tag_brands = 0
    tag_list = []
    no_tag_brand_list = []
    csv_file = DATA_IMPORT_PATH + 'unique_tags.csv'
    no_tag_csv_file = DATA_IMPORT_PATH + 'brands_with_no_tags.csv'
    try:
        for file in file_list:
            row = read_csv(DATA_BRANDS_PATH + '' + file, 'row')
            if row[6] != 'NULL':
                unique_elem_list(row[6], tag_list)
            else:
                no_tag_brands += 1
                no_tag_brand_list.append(file)
        tag_list.sort()
        no_tag_brand_list.sort()
        list_to_csv(tag_list, csv_file)
        list_to_csv(no_tag_brand_list, no_tag_csv_file)
        write_log('File ' + csv_file + ' updated')
        write_log(str(no_tag_brands) + ' brands without tag')
    except Exception as e:
        msg = 'Script create_tag_csv failed on file  ' + csv_file + ': ' + repr(e)
        failed_import_log(msg)
        write_log(msg)


def update_sp_tags(tag_family=''):
    sp_list = read_csv(DATA_STRAPI_PATH + '' + 'tags.csv')
    import_list = read_csv(DATA_IMPORT_PATH + 'unique_tags.csv')
    items_diff = list_diff(import_list, sp_list)
    new_items = [it for it in items_diff if it != []]
    new_import_items = []
    if new_items and len(new_items) > 0:
        new_sp_item_counter = 0
        new_import_item_counter = 0
        failed_import_counter = 0
        for item in new_items:
            if item not in sp_list:
                sp_item = str(item[0])
                sp_dict = {
                    'data': {
                        'name': sp_item,
                        'slug': slugify(sp_item),
                        'type': tag_family,
                        'organizations': [],
                    }
                }
                try:
                    sp_query = sp_write_conn(json.dumps(sp_dict), 'tags')
                    if type(sp_query) is dict and len(sp_query) != 0:
                        new_sp_item_counter += 1
                        msg = 'Success -- tag ' + sp_item + ' imported to Strapi'
                        write_log(msg)
                    else:
                        failed_import_counter += 1
                        msg = 'Failed -- tag ' + sp_item + ' import to Strapi failed: ' + str(sp_query)
                        failed_import_log(msg)
                        write_log(msg)
                except Exception as e:
                    msg = 'Script update_sp_tags failed. Tag import to Strapi failed: ' + repr(e)
                    failed_import_log(msg)
                    write_log(msg)
            elif item not in import_list:
                new_import_items.append(item[0])
                new_import_item_counter += 1
        with open(DATA_IMPORT_PATH + 'unique_tags.csv', 'a+') as f:
            write = csv.writer(f, delimiter='\n')
            write.writerow(new_import_items)
        write_log(str(new_sp_item_counter) + ' new tags imported to Strapi')
        write_log(str(new_import_item_counter) + ' new tags imported to import file')
        write_log(str(failed_import_counter) + ' Strapi imports failed')
    else:
        write_log('No new tag to add to Strapi')
