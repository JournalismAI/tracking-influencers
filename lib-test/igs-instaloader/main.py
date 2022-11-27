# https://instaloader.github.io/
# https://github.com/instaloader/instaloader
# pip3 freeze > requirements.txt

from my_credentials import *
from datetime import datetime
from itertools import dropwhile, takewhile

import instaloader

L = instaloader.Instaloader()
L.login(MY_USERNAME, MY_PASSWORD)


# PROFILE = input('Enter an account username: ')
PROFILE = 'ilsole_24ore'

L.download_profile(PROFILE, profile_pic_only=True)
profile_id = L.check_profile_id(PROFILE)
print(profile_id)

profile = instaloader.Profile.from_username(L.context, PROFILE)
posts = profile.get_posts()

SINCE = datetime(2022, 5, 29)
UNTIL = datetime(2022, 5, 27)

for post in takewhile(lambda p: p.date > UNTIL, dropwhile(lambda p: p.date > SINCE, posts)):
    print(post.date)
    L.download_post(post, PROFILE)

'''
posts_sorted_by_likes = sorted(profile.get_posts(), key=lambda post: post.likes, reverse=True)
for post in posts_sorted_by_likes:
    L.download_post(post, PROFILE)
'''
