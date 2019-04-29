from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
WAIT_SECOND=30
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
import re
SERIES_RANGE=4
URL_PTCG='https://www.pokemon-card.com/'
URL_PTCG_RULE='rules/faq/'
import urllib.request
import json
import os
from requests_oauthlib import OAuth1Session
URL_TEXT='https://api.twitter.com/1.1/statuses/update.json'
URL_TL='https://api.twitter.com/1.1/statuses/home_timeline.json'
URL_MEDIA='https://upload.twitter.com/1.1/media/upload.json'
options=Options()
options.binary_location = '/app/.apt/usr/bin/google-chrome'
# options.add_argument('--headless')
driver=webdriver.Chrome(chrome_options=options)
# driver=webdriver.PhantomJS()
driver.set_window_size(1124, 850)
driver.implicitly_wait(30)

## 直近の SERIES_RANGE 個の商品からランダムに選択し、そのURLを取得
driver.get(URL_PTCG+URL_PTCG_RULE)
WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "ProductList_item_inner")))
html=driver.page_source.encode('utf-8')
soup=BeautifulSoup(html, 'html.parser')
commodities=soup.find_all('a',attrs={'class':'ProductList_item_inner'})
# print(commodities)
productID=commodities[random.randint(0,SERIES_RANGE)].get('href')

## Q&Aの件数を取得
driver.get(URL_PTCG+URL_PTCG_RULE+productID)
WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "HitNum")))
html=driver.page_source.encode('utf-8')
soup=BeautifulSoup(html, 'html.parser')
# print(soup)
# hitCount=soup.find_all('div',attr={'class':'HitNum'})
# searchResult=soup.find('section',attr={'class':'SearchResult'})
searchResult=soup.find(text=re.compile(u'件'))
# print(searchResult.parent.span.text)
# print(re.match(r'\d+',searchResult.parent.text))
hitNum=int(searchResult.parent.span.text)
num=random.randint(0,hitNum-1)
pageNum=num//10+1
# print(hitNum,num)
# print(url+productID+'&page='+str(pageNum))

## Q&Aをランダムに取得
driver.get(URL_PTCG+URL_PTCG_RULE+productID+'&page='+str(pageNum))
WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "FAQResultList_item")))
html=driver.page_source.encode('utf-8')
soup=BeautifulSoup(html, 'html.parser')
listItems=soup.find_all('li',attrs={'class':'FAQResultList_item'})
bodys=listItems[num%10].find_all('div',attrs={'class':'BodyArea'})
# for body in bodys:
#     print(body.text)
keyCards=listItems[num%10].find_all('a',attrs={'class':'popup-card-detail'})
# for card in keyCards:
#     print(card.string,card.get('href'))

## 関連カード画像を取得
imagePaths=['' for _ in keyCards]
imgCnt=0
for card in keyCards:
    driver.get(URL_PTCG+card.get('href'))
    WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "fit")))
    html=driver.page_source.encode('utf-8')
    soup=BeautifulSoup(html, 'html.parser')
    img=soup.find('img',attrs={'class':'fit'})

    data=urllib.request.urlopen(URL_PTCG+img.get('src')).read()
    imagePaths[imgCnt]='./'+str(imgCnt)+'.jpg'
    with open(imagePaths[imgCnt],mode="wb") as f:
        f.write(data)
    imgCnt+=1

driver.close()
driver.quit()

## リプツリーの形でツイートしていく
mySession=OAuth1Session(os.environ['CONSUMER_KEY'],os.environ['CONSUMER_SECRET'],os.environ['TOKEN'],os.environ['TOKEN_SECRET'])

## 画像のアップロード
mediaIDs=['' for _ in range(imgCnt//4+1)]
for i in range(imgCnt):
    files={'media':open(imagePaths[i],'rb')}
    req_media=mySession.post(URL_MEDIA,files=files)
    # if req_media.status_code!=200:
    #     print('update error:'+req_media.text)
    # mediaID=json.loads(req_media.text)['media_id']
    mediaIDString=json.loads(req_media.text)['media_id_string']
    if mediaIDs[i//4]=='':
        mediaIDs[i//4]=mediaIDString
    else:
        mediaIDs[i//4]=mediaIDs[i//4]+','+mediaIDString

## Questionのツイート
status='Q '+bodys[0].text
isReply=False
tweetCnt=0
while True:
    params={'status':status[:140]}
    if isReply:
        req_tl=mySession.get(URL_TL)
        # if req_tl.status_code!=200:
        #     print('time line error'+req_tl.text)
        id=json.loads(req_tl.text)[0]['id']
        params['in_reply_to_status_id']=id
    if imgCnt//4>=tweetCnt:
        params['media_ids']=mediaIDs[tweetCnt]
    req_text=mySession.post(URL_TEXT,params=params)
    # if req_text.status_code!=200:
    #     print('tweet error:'+req_text.text)

    tweetCnt+=1
    if len(status)<=140:
        if imgCnt//4>=tweetCnt:
            status='カードの表示'
        else:
            break
    else:
        status=status[140:]
    isReply=True

## Answerのツイート
status='A '+bodys[1].text
while True:
    params={'status':status[:140]}
    req_tl=mySession.get(URL_TL)
    # if req_tl.status_code!=200:
    #     print('timeline error'+req_tl.text)
    id=json.loads(req_tl.text)[0]['id']
    params['in_reply_to_status_id']=id
    req_text=mySession.post(URL_TEXT,params=params)
    # if req_text.status_code!=200:
    #     print('tweet error:'+req_text.text)
    if len(status)<=140:
        break
    status=status[140:]

## おまけ タイムラインの取得
# req_tl=mySession.get(URL_TL)
# if req_tl.status_code!=200:
#     print('time line error'+req_tl.text)
# timelines=json.loads(req_tl.text)
# for timeline in timelines:
#     print(timeline['id'],timeline['text'])


## tweepyを使う場合
# auth=tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
# auth.set_access_token(TOKEN,TOKEN_SECRET)
# t=tweepy.API(auth)
#
# t.update_with_media(filename=imagePaths[0],status='test')
#
# status='Q '+bodys[0].text
# isReply=False
# while True:
#     if isReply:
#         id=t.home_timeline()[0].id
#         t.update_status(status=status[:140],in_reply_to_status_id=id)
#     else:
#         t.update_status(status=status[:140])
#     if len(status)<=140:
#         break
#     status=status[140:]
#     isReply=True
#
# status='A '+bodys[1].text
# while True:
#     id=t.home_timeline()[0].id
#     t.update_status(status=status[:140],in_reply_to_status_id=id)
#     if len(status)<=140:
#         break
#     status=status[140:]
#
## おまけ　タイムラインの取得
# timelines=t.home_timeline()
# for timeline in timelines:
#     print('{id}:{text}'.format(id=timeline.id,text=timeline.text))
