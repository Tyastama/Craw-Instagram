from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import time
import re
from urllib.request import urlopen
import json
from pandas.io.json import json_normalize
import pandas as pd, numpy as np

username='jktinfo'
browser = webdriver.Chrome('/home/tyas-yanotama/chromedriver')
browser.get('https://www.instagram.com/'+username+'/?hl=en')
Pagelength = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#mengekstrak bagian profile instragram
links=[]
source = browser.page_source
data=bs(source, 'html.parser')
body = data.find('body')
script = body.find('script', text=lambda t: t.startswith('window._sharedData'))
page_json = script.string.split(' = ', 1)[1].rstrip(';')
data = json.loads(page_json)
#try 'script.string' instead of script.text if you get error on index out of range
for link in data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']:
    links.append('https://www.instagram.com'+'/p/'+link['node']['shortcode']+'/')
#try with ['display_url'] instead of ['shortcode'] if you don't get links 

print(data)
df= pd.DataFrame(data)
so =df.to_json("data.json")
result=pd.DataFrame()
for i in range(len(links)):
 try:
    page = urlopen(links[i]).read()
    data=bs(page, 'html.parser')
    body = data.find('body')
    script = body.find('script')
    raw = script.text.strip().replace('window._sharedData =', '').replace(';', '')
    json_data=json.loads(raw)
    posts =json_data['entry_data']['PostPage'][0]['graphql']
    posts= json.dumps(posts)
    posts = json.loads(posts)
    print(posts)
    x = pd.DataFrame.from_dict(json_normalize(posts), orient='columns') 
    x.columns = x.columns.str.replace("shortcode_media.", "")
    result=result.append(x)
 except:
    np.nan
    result = result.drop_duplicates(subset = 'shortcode')
    result.index = range(len(result.index))

import os
import requests
result.index = range(len(result.index))
directory="/home/tyas-yanotama/Documents"
for i in range(len(result)):
    r = requests.get(result['display_url'][i])
    with open(directory+result['shortcode'][i]+".jpg", 'wb') as f:
                    f.write(r.content)
