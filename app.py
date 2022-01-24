from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
import re
import requests
import json
import os
import time
from requests_oauthlib import OAuth1Session

URL_PTCG='https://www.pokemon-card.com'
URL_PTCG_RULE='/rules/faq/'
URL_TEXT='https://api.twitter.com/1.1/statuses/update.json'
URL_TL='https://api.twitter.com/1.1/statuses/home_timeline.json'
URL_MEDIA='https://upload.twitter.com/1.1/media/upload.json'

def main():
    ## ウェブドライバ起動
    driver_path='/app/.chromedriver/bin/chromedriver'
    options=Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')                # sandboxモードを解除
    options.add_argument('--disable-dev-shm-usage')     # /dev/shmパーティションの使用を禁止
    options.add_argument('--window-size=500,500')       # 小さくしたほうがメモリ消費を抑えられる（クラッシュしづらい）
    # options.add_argument('--start-maxmized')            # windowサイズ最大化
    options.add_argument('--disable-extentions')        # 拡張機能無効化
    options.add_argument('--proxy-server="direct://"')  # Proxy経由ではなく直接接続する
    options.add_argument('--proxy-bypass-list=*')       # すべてのホスト名
    driver=webdriver.Chrome(executable_path=driver_path, chrome_options=options)
    driver.implicitly_wait(10) # 暗黙的な待機時間
    WAIT_SECOND=30 # 明示的な待機時間

    # ## 直近の SERIES_RANGE 個の商品からランダムに選択し、そのURLを取得
    # SERIES_RANGE=0
    # productID=commodities[random.randint(0,SERIES_RANGE)].get('href')

    ## 一番直近のパックの商品を選択し、そのURLを取得
    try:
        driver.get(URL_PTCG+URL_PTCG_RULE)
        WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located( (By.CLASS_NAME, "ProductList_item_inner") ))
    except:
        print('err1')
        driver.quit()
        return
    html=driver.page_source.encode('utf-8')
    soup=BeautifulSoup(html, 'html.parser')
    commodities=soup.find_all('a',attrs={'class':'ProductList_item_inner'})
    productID=''
    for comi in commodities:
        if 'パック' in comi.get_text():
            productID=comi.get('href')
            break
    ## Q&Aの件数を取得し、ランダムに選択
    try:
        driver.get(URL_PTCG+productID)
        WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "HitNum")))
    except:
        print('err2')
        driver.quit()
        return
    html=driver.page_source.encode('utf-8')
    soup=BeautifulSoup(html, 'html.parser')
    # hitCount=soup.find_all('div',attr={'class':'HitNum'})
    # searchResult=soup.find('section',attr={'class':'SearchResult'})
    searchResult=soup.find(text=re.compile(u'件'))
    hitNum=int(searchResult.parent.span.text)
    num=random.randint(0,hitNum-1)
    pageNum=num//10+1
    print(f'hitNum={hitNum} num={num} pageNum={pageNum}')

    ## Q&Aをランダムに取得
    ## "Uncaught TypeError: PTC.setCardDetailPopupWindow is not a function" が出る
    try:
        driver.get(URL_PTCG+productID+'&page='+str(pageNum))
        WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "FAQResultList_item")))
    except:
        print('err3')
        driver.quit()
        return
    html=driver.page_source.encode('utf-8')
    soup=BeautifulSoup(html, 'html.parser')
    listItems=soup.find_all('li',attrs={'class':'FAQResultList_item'})
    bodys=listItems[num%10].find_all('div',attrs={'class':'BodyArea'})
    keyCards=listItems[num%10].find_all('a',attrs={'class':'popup-card-detail'})

    ## 関連カード画像を取得
    imagePaths=['' for _ in keyCards]
    imgCnt=0
    for card in keyCards:
        try:
            driver.get(URL_PTCG+card.get('href'))
            WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "fit")))
        except:
            print('err4')
            driver.quit()
            return
        html=driver.page_source.encode('utf-8')
        soup=BeautifulSoup(html, 'html.parser')
        img=soup.find('img',attrs={'class':'fit'})

        try:
            response=requests.get(URL_PTCG+img.get('src'), stream=True)
        except:
            print('err5')
            driver.quit()
            return
        imagePaths[imgCnt]='./'+str(imgCnt)+'.jpg'
        with open(imagePaths[imgCnt],mode="wb") as f:
            f.write(response.content)
        imgCnt+=1

    driver.quit()

    ## リプツリーの形でツイートしていく
    ## セッション開始
    mySession=OAuth1Session(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'], os.environ['TOKEN'], os.environ['TOKEN_SECRET'])

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
    isTweeting=True
    tweetCnt=0
    tweet_max=140
    while isTweeting:
        params={'status':status[:tweet_max]}
        if isReply:
            req_tl=mySession.get(URL_TL)
            # if req_tl.status_code!=200:
            #     print('time line error'+req_tl.text)
            id=json.loads(req_tl.text)[0]['id']
            params['in_reply_to_status_id']=id

        ## 質問文に４つずつ画像を添付する
        ## tweetCnt=0に対してimgCnt=1~4
        if (imgCnt-1)//4>=tweetCnt: # imgCnt>=5 なら２つ目のツイートにも画像添付
            params['media_ids']=mediaIDs[tweetCnt]
        ## ツイートの分割
        if len(status)<=tweet_max:
            if (imgCnt-1)//4>=tweetCnt+1: # 未表示画像があれば分ける（statusが未tweet文章）
                status='カードの表示'
            else:
                isTweeting=False
        else: # 字数がtweet_maxを超えるなら分ける（statusが未tweet文章）
            params['status']=params['status'][:(tweet_max-4)]+'（続く）'
            status=status[(tweet_max-4):]
        req_text=mySession.post(URL_TEXT,params=params)
        time.sleep(2)
        # if req_text.status_code!=200:
        #     print('tweet error:'+req_text.text)

        tweetCnt+=1
        isReply=True

    ## Answerのツイート
    status='A '+bodys[1].text
    isTweeting=True
    while isTweeting:
        params={'status':status[:tweet_max]}
        req_tl=mySession.get(URL_TL)
        # if req_tl.status_code!=200:
        #     print('timeline error'+req_tl.text)
        id=json.loads(req_tl.text)[0]['id']
        params['in_reply_to_status_id']=id
        ## ツイートの分割
        if len(status)<=tweet_max:
            isTweeting=False
        else: # 字数がtweet_maxを超えるなら分ける（statusが未tweet文章）
            params['status']=params['status'][:(tweet_max-4)]+'（続く）'
            status=status[(tweet_max-4):]
        req_text=mySession.post(URL_TEXT,params=params)
        time.sleep(2)
        # if req_text.status_code!=200:
        #     print('tweet error:'+req_text.text)

if __name__=='__main__':
    main()
