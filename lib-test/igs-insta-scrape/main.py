# https://pypi.org/project/insta-scrape/
# https://chris-greening.github.io/instascrape/
# pip3 freeze > requirements.txt

from my_credentials import *
from selenium import webdriver
from instascrape import *

driver = webdriver.Firefox()
# driver.get('https://www.instagram.com/')

headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57",
    "cookie": "sessionid=" + MY_SESSION_ID + ";"
}

account = "ilsole_24ore"

# create folder to store json and images
import os
path = os.getcwd()
path = os.path.join(path, account)
isExist = os.path.exists(path)
if not isExist:
    os.mkdir(path)


profile = Profile(f'https://www.instagram.com/{account}/')
profile.scrape(headers=headers)
profile.to_json(f"{path}/profile.json")

recents = profile.get_recent_posts()
photos = [post for post in recents if not post.is_video]

for post in photos:
    fname = post.upload_date.strftime("%Y-%m-%d %Hh%Mm")
    post.download(f"{path}/{fname}.jpg")
    post.to_json(f"{path}/{fname}.json")



