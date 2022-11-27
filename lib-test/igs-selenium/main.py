from my_credentials import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time

driver = webdriver.Firefox()
driver.get("http://www.instagram.com")

# target the "allow only essential cookies" button
cookies = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Only allow essential cookies")]'))).click()


# target the "username" and "password" input field
username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
username.clear()
username.send_keys(MY_USERNAME)
password.clear()
password.send_keys(MY_PASSWORD)

# target the "login" button
time.sleep(3)
button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

# target the "save your login info" button and the "turn on notification" button
time.sleep(5)
not_save_login = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()
turn_off_notification = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]'))).click()

time.sleep(5)
#target the "search" input field
searchbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
searchbox.clear()

keyword = "ilsole_24ore"
searchbox.send_keys(keyword)
my_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/" + keyword + "/')]")))
my_link.click()

'''
#scroll down 2 times
n_scrolls = 2
for j in range(0, n_scrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
'''

time.sleep(5)
#target all the link elements on the page
anchors = driver.find_elements(by=By.TAG_NAME, value='a')
anchors = [a.get_attribute('href') for a in anchors]
#narrow down all links to image links only
anchors = [a for a in anchors if str(a).startswith("https://www.instagram.com/p/")]

print('Found ' + str(len(anchors)) + ' links to images')
print(anchors)

images = []
#follow each image link and extract only image at index=1
for a in anchors:
    driver.get(a)
    time.sleep(5)
    img = driver.find_elements(by=By.TAG_NAME, value='img')
    img = [i.get_attribute('src') for i in img]
    images.append(img[1])


# create folder to store images
import os
import wget
path = os.getcwd()
path = os.path.join(path, keyword)
isExist = os.path.exists(path)
if not isExist:
    os.mkdir(path)

counter = 0
for image in images:
    save_as = os.path.join(path, keyword + str(counter) + '.jpg')
    wget.download(image, save_as)
    counter += 1
