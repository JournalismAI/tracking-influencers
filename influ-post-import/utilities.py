# pip3 freeze > requirements.txt
from datetime import datetime
import requests
import slug as slug


from requirements.config import *
import csv
import json
import re
import os
import pandas as pd
import string
import random
# import slug
import wordsegment as ws
import fasttext as ft
ft.FastText.eprint = lambda x: None
ws.load()


def get_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(4))


###############################################
############### DATA FILES ####################
###############################################

DATA_PATH = './data/'
DATA_IMPORT_PATH = DATA_PATH + 'import/'
DATA_INFLU_PATH = DATA_PATH + 'influencers/'
DATA_STRAPI_PATH = DATA_PATH + 'strapi_import_results/'
DATA_ANALYSIS_PATH = DATA_PATH + 'analysis/'
DATA_MODEL_PATH = DATA_PATH + 'pretrained_model/'
DATA_FOLDER = ''
LOG_PATH = './logs/'
strapi_import_log = LOG_PATH + 'strapi_import.txt'
strapi_failed_import_log = LOG_PATH + 'strapi_failed_import.txt'
ft_model = ft.load_model(DATA_MODEL_PATH + 'lid.176.bin')

character_dict = {
    "#": "hashtags",
    "@": "mentions"
}

nltk_stopwords = {
    "kids-sole": ['ad', 'al', 'allo', 'ai', 'agli', 'all', 'agl', 'alla', 'alle', 'con', 'col', 'coi', 'da', 'dal', 'dallo', 'dai', 'dagli', 'dall', 'dagl', 'dalla', 'dalle', 'di', 'del', 'dello', 'dei', 'degli', 'dell', 'degl', 'della', 'delle', 'in', 'nel', 'nello', 'nei', 'negli', 'nell', 'negl', 'nella', 'nelle', 'su', 'sul', 'sullo', 'sui', 'sugli', 'sull', 'sugl', 'sulla', 'sulle', 'per', 'tra', 'contro', 'io', 'tu', 'lui', 'lei', 'noi', 'voi', 'loro', 'mio', 'mia', 'miei', 'mie', 'tuo', 'tua', 'tuoi', 'tue', 'suo', 'sua', 'suoi', 'sue', 'nostro', 'nostra', 'nostri', 'nostre', 'vostro', 'vostra', 'vostri', 'vostre', 'mi', 'ti', 'ci', 'vi', 'lo', 'la', 'li', 'le', 'gli', 'ne', 'il', 'un', 'uno', 'una', 'ma', 'ed', 'se', 'perché', 'anche', 'come', 'dov', 'dove', 'che', 'chi', 'cui', 'non', 'più', 'quale', 'quanto', 'quanti', 'quanta', 'quante', 'quello', 'quelli', 'quella', 'quelle', 'questo', 'questi', 'questa', 'queste', 'si', 'tutto', 'tutti', 'a', 'c', 'e', 'i', 'l', 'o', 'ho', 'hai', 'ha', 'abbiamo', 'avete', 'hanno', 'abbia', 'abbiate', 'abbiano', 'avrò', 'avrai', 'avrà', 'avremo', 'avrete', 'avranno', 'avrei', 'avresti', 'avrebbe', 'avremmo', 'avreste', 'avrebbero', 'avevo', 'avevi', 'aveva', 'avevamo', 'avevate', 'avevano', 'ebbi', 'avesti', 'ebbe', 'avemmo', 'aveste', 'ebbero', 'avessi', 'avesse', 'avessimo', 'avessero', 'avendo', 'avuto', 'avuta', 'avuti', 'avute', 'sono', 'sei', 'è', 'siamo', 'siete', 'sia', 'siate', 'siano', 'sarò', 'sarai', 'sarà', 'saremo', 'sarete', 'saranno', 'sarei', 'saresti', 'sarebbe', 'saremmo', 'sareste', 'sarebbero', 'ero', 'eri', 'era', 'eravamo', 'eravate', 'erano', 'fui', 'fosti', 'fu', 'fummo', 'foste', 'furono', 'fossi', 'fosse', 'fossimo', 'fossero', 'essendo', 'faccio', 'fai', 'facciamo', 'fanno', 'faccia', 'facciate', 'facciano', 'farò', 'farai', 'farà', 'faremo', 'farete', 'faranno', 'farei', 'faresti', 'farebbe', 'faremmo', 'fareste', 'farebbero', 'facevo', 'facevi', 'faceva', 'facevamo', 'facevate', 'facevano', 'feci', 'facesti', 'fece', 'facemmo', 'faceste', 'fecero', 'facessi', 'facesse', 'facessimo', 'facessero', 'facendo', 'sto', 'stai', 'sta', 'stiamo', 'stanno', 'stia', 'stiate', 'stiano', 'starò', 'starai', 'starà', 'staremo', 'starete', 'staranno', 'starei', 'staresti', 'starebbe', 'staremmo', 'stareste', 'starebbero', 'stavo', 'stavi', 'stava', 'stavamo', 'stavate', 'stavano', 'stetti', 'stesti', 'stette', 'stemmo', 'steste', 'stettero', 'stessi', 'stesse', 'stessimo', 'stessero', 'stando'],
    "kids-sky-news": ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"],
    "kids-infobae": ['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos', 'estéis', 'estén', 'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán', 'estaría', 'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba', 'estabas', 'estábamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras', 'estuviéramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses', 'estuviésemos', 'estuvieseis', 'estuviesen', 'estando', 'estado', 'estada', 'estados', 'estadas', 'estad', 'he', 'has', 'ha', 'hemos', 'habéis', 'han', 'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá', 'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais', 'habrían', 'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube', 'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras', 'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos', 'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas', 'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seáis', 'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería', 'serías', 'seríamos', 'seríais', 'serían', 'era', 'eras', 'éramos', 'erais', 'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera', 'fueras', 'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos', 'fueseis', 'fuesen', 'sintiendo', 'sentido', 'sentida', 'sentidos', 'sentidas', 'siente', 'sentid', 'tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen', 'tenga', 'tengas', 'tengamos', 'tengáis', 'tengan', 'tendré', 'tendrás', 'tendrá', 'tendremos', 'tendréis', 'tendrán', 'tendría', 'tendrías', 'tendríamos', 'tendríais', 'tendrían', 'tenía', 'tenías', 'teníamos', 'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis', 'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos', 'tuvierais', 'tuvieran', 'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis', 'tuviesen', 'teniendo', 'tenido', 'tenida', 'tenidos', 'tenidas', 'tened'],
    "test": ['ad', 'al', 'allo', 'ai', 'agli', 'all', 'agl', 'alla', 'alle', 'con', 'col', 'coi', 'da', 'dal', 'dallo', 'dai', 'dagli', 'dall', 'dagl', 'dalla', 'dalle', 'di', 'del', 'dello', 'dei', 'degli', 'dell', 'degl', 'della', 'delle', 'in', 'nel', 'nello', 'nei', 'negli', 'nell', 'negl', 'nella', 'nelle', 'su', 'sul', 'sullo', 'sui', 'sugli', 'sull', 'sugl', 'sulla', 'sulle', 'per', 'tra', 'contro', 'io', 'tu', 'lui', 'lei', 'noi', 'voi', 'loro', 'mio', 'mia', 'miei', 'mie', 'tuo', 'tua', 'tuoi', 'tue', 'suo', 'sua', 'suoi', 'sue', 'nostro', 'nostra', 'nostri', 'nostre', 'vostro', 'vostra', 'vostri', 'vostre', 'mi', 'ti', 'ci', 'vi', 'lo', 'la', 'li', 'le', 'gli', 'ne', 'il', 'un', 'uno', 'una', 'ma', 'ed', 'se', 'perché', 'anche', 'come', 'dov', 'dove', 'che', 'chi', 'cui', 'non', 'più', 'quale', 'quanto', 'quanti', 'quanta', 'quante', 'quello', 'quelli', 'quella', 'quelle', 'questo', 'questi', 'questa', 'queste', 'si', 'tutto', 'tutti', 'a', 'c', 'e', 'i', 'l', 'o', 'ho', 'hai', 'ha', 'abbiamo', 'avete', 'hanno', 'abbia', 'abbiate', 'abbiano', 'avrò', 'avrai', 'avrà', 'avremo', 'avrete', 'avranno', 'avrei', 'avresti', 'avrebbe', 'avremmo', 'avreste', 'avrebbero', 'avevo', 'avevi', 'aveva', 'avevamo', 'avevate', 'avevano', 'ebbi', 'avesti', 'ebbe', 'avemmo', 'aveste', 'ebbero', 'avessi', 'avesse', 'avessimo', 'avessero', 'avendo', 'avuto', 'avuta', 'avuti', 'avute', 'sono', 'sei', 'è', 'siamo', 'siete', 'sia', 'siate', 'siano', 'sarò', 'sarai', 'sarà', 'saremo', 'sarete', 'saranno', 'sarei', 'saresti', 'sarebbe', 'saremmo', 'sareste', 'sarebbero', 'ero', 'eri', 'era', 'eravamo', 'eravate', 'erano', 'fui', 'fosti', 'fu', 'fummo', 'foste', 'furono', 'fossi', 'fosse', 'fossimo', 'fossero', 'essendo', 'faccio', 'fai', 'facciamo', 'fanno', 'faccia', 'facciate', 'facciano', 'farò', 'farai', 'farà', 'faremo', 'farete', 'faranno', 'farei', 'faresti', 'farebbe', 'faremmo', 'fareste', 'farebbero', 'facevo', 'facevi', 'faceva', 'facevamo', 'facevate', 'facevano', 'feci', 'facesti', 'fece', 'facemmo', 'faceste', 'fecero', 'facessi', 'facesse', 'facessimo', 'facessero', 'facendo', 'sto', 'stai', 'sta', 'stiamo', 'stanno', 'stia', 'stiate', 'stiano', 'starò', 'starai', 'starà', 'staremo', 'starete', 'staranno', 'starei', 'staresti', 'starebbe', 'staremmo', 'stareste', 'starebbero', 'stavo', 'stavi', 'stava', 'stavamo', 'stavate', 'stavano', 'stetti', 'stesti', 'stette', 'stemmo', 'steste', 'stettero', 'stessi', 'stesse', 'stessimo', 'stessero', 'stando'],
}


def get_dict_key(my_dict, val):
    for d_key, d_value in my_dict.items():
        if val == d_value:
            return d_key


def unique_elem_list(el, unique_list):
    if el not in unique_list:
        unique_list.append(el)


def list_diff(li1, li2):
    li_diff = [i for i in li1 + li2 if i not in li1 or i not in li2 and len(i) > 0]
    return li_diff


def list_to_csv(rows, csv_file):
    with open(csv_file, 'w', encoding='utf8') as f:
        write = csv.writer(f, delimiter='\n')
        write.writerow(rows)


def data_to_json(data, json_file):
    json_obj = json.dumps(data, indent=2)
    with open(json_file, 'w+', encoding='utf8') as f:
        f.write(json_obj)


def empty_csv(csv_file, row_num):
    df = pd.read_csv(csv_file)
    df = df.head(row_num)
    df.to_csv(csv_file, index=False, header=True)
    print('Csv emptied')


def empty_file(file):
    with open(file, 'w', encoding='utf8') as f:
        f.write('')
        print('File emptied')


def failed_import_log(msg: object) -> object:
    with open(strapi_failed_import_log, 'r+', encoding='utf8') as f:
        content = f.read()
        f.seek(0)
        f.write('##################\n' + get_now() + '\n' + msg + '\n##################\n\n\n' + content)


def write_log(msg, file=strapi_import_log):
    with open(file, 'a', encoding='utf8') as f:
        f.write('' + get_now() + ' - ' + msg + '\n')
    print(msg)


def csv_to_list(file, param='list'):
    with open(file, 'r', encoding='utf8') as f:
        csv_reader = csv.reader(f, delimiter='\n')
        tmp_list = []
        for row in csv_reader:
            tmp_list.append(row[0])
        return tmp_list


def get_influ_folder_list(folder):
    influ_folder_list = os.listdir(folder)
    influ_folder_list.sort()
    return influ_folder_list


###############################################
############ TEXT MANIPULATION ################
###############################################


def remove_symbols(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642" 
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               u"\u2063"  # invisible comma
                               u"\u2060"  # word joiner
                               u"\u200b"  # zero width space
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def fasttext_language_predict(text, model=ft_model):
    text = text.replace('\n', " ")
    prediction = model.predict([text])
    return prediction


def wordsegment(word):
    return ws.segment(word)


'''def create_slug(text):
    slugg = slug.slug(text)
    if slugg == '' or slugg == 'null':
        slugg = random_string()
    else:
        slugg += '----' + random_string()
    return slug'''


###############################################
############ STRAPI API CONN ##################
###############################################

def sp_read_conn(relative_path, params='?sort=name', token=STRAPI_API_TOKEN_READ):
    query_conn = STRAPI_API_CONN + '/' + relative_path + '/' + params
    query_request = requests.get(query_conn, headers={"Authorization": f"Bearer {token}"})
    if query_request.status_code == requests.codes.ok:
        query_result = query_request.json()  # dict
        return query_result
    else:
        return query_request.status_code


def sp_write_conn(data, relative_path, params='', token=STRAPI_API_TOKEN_WRITE):
    query_conn = STRAPI_API_ENDPOINT + '/' + relative_path + '/' + params
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


def get_sp_api_endpoint(endpoint, params='?', page_size='100', field_key='name'):
    file = DATA_STRAPI_PATH + endpoint + '.csv'
    items_list = []
    page_count = sp_page_count(endpoint, params, page_size)
    if isinstance(page_count, int):
        for count in range(page_count):
            tm_params = params
            if endpoint != 'tags':
                tm_params += 'sort=' + field_key + '&pagination[page]=' + str(
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
        write_log(page_count)


def get_sp_items(endpoint, csvfile, jsonfile, params='?', page_size='100', field_key='name'):
    sp_item_list = []
    page_count = sp_page_count(endpoint, params, page_size)
    if isinstance(page_count, int):
        sp_dict = {}
        for count in range(page_count):
            tm_params = params + 'sort=' + field_key + '&pagination[page]=' + str(
                count + 1) + '&pagination[pageSize]=' + page_size
            sp_query = sp_read_conn(endpoint, tm_params)
            if type(sp_query) is dict and len(sp_query) != 0:
                for item in sp_query['data']:
                    sp_item_list.append(item['attributes'][field_key])
                    item_dict = {
                        item['attributes'][field_key]: item['id']
                    }
                    sp_dict.update(item_dict)
                    write_log('Item ' + item['attributes'][field_key] + ' found')
            else:
                msg_json = 'Failed -- File ' + DATA_STRAPI_PATH + jsonfile + ' not updated: ' + str(sp_query)
                msg_csv = 'Failed -- File ' + DATA_STRAPI_PATH + csvfile + ' not updated: ' + str(sp_query)
                failed_import_log(msg_json)
                write_log(msg_json)
                failed_import_log(msg_csv)
                write_log(msg_csv)
        data_to_json(sp_dict, DATA_STRAPI_PATH + jsonfile)
        list_to_csv(sp_item_list, DATA_STRAPI_PATH + csvfile)
        write_log(str(len(sp_item_list)) + ' items found in Strapi')
        write_log('File ' + DATA_STRAPI_PATH + jsonfile + ' updated')
        write_log('File ' + DATA_STRAPI_PATH + csvfile + ' updated')
    else:
        write_log(page_count)

