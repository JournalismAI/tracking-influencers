from utilities import *
import csv


def create_org_csv(file_list):
    no_org_brands = 0
    org_list = []
    no_name_brand_list = []
    csv_file = DATA_IMPORT_PATH + 'unique_organizations.csv'
    no_name_csv_file = DATA_IMPORT_PATH + 'brands_with_no_organization_name.csv'
    try:
        for file in file_list:
            row = read_csv(DATA_BRANDS_PATH + '' + file, 'row')
            if row[0] != 'NULL':
                unique_elem_list(slugify(row[0]), org_list)
            else:
                no_org_brands += 1
                no_name_brand_list.append(file)
        org_list.sort()
        no_name_brand_list.sort()
        list_to_csv(org_list, csv_file)
        list_to_csv(no_name_brand_list, no_name_csv_file)
        write_log('File ' + csv_file + ' updated')
        write_log(str(no_org_brands) + ' organizations without name')
    except Exception as e:
        msg = 'Script create_org_csv failed on file ' + csv_file + ': ' + repr(e)
        failed_import_log(msg)
        write_log(msg)


def update_sp_organizations():
    refused_slug_list = ['ad', 'beauty', 'bella', 'campari', 'deichmann', 'delsey', 'drybar', 'kylie', 'nocibe', 'anastasia', 'c-a-r-a', 'casper', 'dubai', 'frey', 'hush', 'i-am', 'imaginarium', 'jordan', 'jules', 'las-vegas', 'london', 'luisa', 'makeup-artist-dubai', 'mark-face-and-body', 'nick', 'photography', 'rosie', 'samantha', 'samsonite', 'the-big-bang-theory', 'the-walking-dead',
'tm', 'womens-clothing-boutique', 'zinburger-wine-burger-bar', 'scholastic', 'tezenis', 'woolworths']  # list of slug that generate an error. To be investigated
    with open(DATA_IMPORT_PATH + 'profile_brand_data.json') as json_file:
        brands_dict = json.load(json_file)
    with open(DATA_IMPORT_PATH + 'profile_org_slug_brand_name.json') as json_file:
        brand_org_slug_dict = json.load(json_file)
    with open(DATA_STRAPI_PATH + 'brands_id.json') as json_file:
        brands_id_dict = json.load(json_file)
    with open(DATA_STRAPI_PATH + 'tags_id.json') as json_file:
        tags_id_dict = json.load(json_file)
    sp_list = read_csv(DATA_STRAPI_PATH + '' + 'organizations.csv')
    import_list = read_csv(DATA_IMPORT_PATH + 'unique_organizations.csv')
    items_diff = list_diff(import_list, sp_list)
    new_items = [it for it in items_diff if it != []]
    new_import_items = []
    if new_items and len(new_items) > 0:
        failed_import_org_dict = []
        failed_import_org_slugs = []
        failed_import_org_names = []
        new_sp_item_counter = 0
        new_import_item_counter = 0
        failed_import_counter = 0
        for item in new_items:
            sp_item = str(item[0])
            if item not in sp_list and sp_item not in refused_slug_list:
                sp_dict = {
                    'data': {
                        'name': brands_dict[brand_org_slug_dict[sp_item]]['org_name'],
                        'slug': brands_dict[brand_org_slug_dict[sp_item]]['org_slug'],
                    }
                }
                if brands_dict[brand_org_slug_dict[sp_item]]['org_website'] and brands_dict[brand_org_slug_dict[sp_item]]['org_website'] != 'NULL':
                    sp_dict['data']['website'] = brands_dict[brand_org_slug_dict[sp_item]]['org_website']
                if brands_dict[brand_org_slug_dict[sp_item]]['org_email']  and brands_dict[brand_org_slug_dict[sp_item]]['org_email'] != 'NULL':
                    sp_dict['data']['email'] = brands_dict[brand_org_slug_dict[sp_item]]['org_email']
                if brands_dict[brand_org_slug_dict[sp_item]]['org_phone'] and brands_dict[brand_org_slug_dict[sp_item]]['org_phone'] != 'NULL':
                    sp_dict['data']['phone'] = brands_dict[brand_org_slug_dict[sp_item]]['org_phone']
                if brands_dict[brand_org_slug_dict[sp_item]]['brand_name'] and brands_dict[brand_org_slug_dict[sp_item]]['brand_name'] != 'NULL':
                    sp_dict['data']['brands'] = [brands_id_dict[brands_dict[brand_org_slug_dict[sp_item]]['brand_name']]]
                if brands_dict[brand_org_slug_dict[sp_item]]['org_tag'] and brands_dict[brand_org_slug_dict[sp_item]]['org_tag'] != 'NULL':
                    sp_dict['data']['tag'] = tags_id_dict[brands_dict[brand_org_slug_dict[sp_item]]['org_tag']]
                try:
                    sp_query = sp_write_conn(json.dumps(sp_dict), 'organizations')
                    if type(sp_query) is dict and len(sp_query) != 0:
                        new_sp_item_counter += 1
                        write_log('Success -- org ' + sp_item + ' imported to Strapi')
                    else:
                        failed_import_org_dict.append(sp_dict)
                        failed_import_org_slugs.append(brands_dict[brand_org_slug_dict[sp_item]]['org_slug'])
                        failed_import_org_names.append(brands_dict[brand_org_slug_dict[sp_item]]['org_name'])
                        failed_import_counter += 1
                        msg = 'Failed -- organization with slug ' + sp_item + ' import to Strapi failed: ' + str(sp_query)
                        failed_import_log(msg)
                        write_log(msg)
                except Exception as e:
                    msg = 'Script update_sp_organizations failed. Org import to Strapi failed: ' + repr(e)
                    failed_import_log(msg)
                    write_log(msg)
            elif item not in import_list:
                new_import_items.append(item[0])
                new_import_item_counter += 1
        new_import_items.sort()
        failed_import_org_slugs.sort()
        failed_import_org_names.sort()
        list_to_csv(new_import_items, DATA_IMPORT_PATH + 'missing_import_orgs.csv')
        list_to_csv(failed_import_org_slugs, DATA_IMPORT_PATH + 'failed_import_org_slugs.csv')
        list_to_csv(failed_import_org_names, DATA_IMPORT_PATH + 'failed_import_org_names.csv')
        data_to_json(failed_import_org_dict, DATA_IMPORT_PATH + 'failed_import_org_dict.json')
        print(str(failed_import_org_dict))
        write_log(str(new_sp_item_counter) + ' new orgs imported to Strapi')
        write_log(str(new_import_item_counter) + ' orgs in Strapi but missing in import file')
        write_log(str(failed_import_counter) + ' Strapi imports failed. Check failed_import_org_* files')
    else:
        write_log('No new organization to add to Strapi')
