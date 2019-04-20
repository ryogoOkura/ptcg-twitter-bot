from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
WAIT_SECOND=30
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
import re
URL='https://www.pokemon-card.com/rules/faq/'
SERIES_RANGE=4
import twitter
CONSUMER_KEY="0PWItx3y8rT56fHmoksjCD3p8"
CONSUMER_SECRET="Oc7v7lETeQdhOb2mnCXd3hiSBlgJ4DlYSADt7uZlBFSo9IRpbB"
TOKEN="1103483478723584000-WCkBL5Hjf5bB6rZlsbgrSy2LrPLj8I"
TOKEN_SECRET="FiRIR90V4wBv8TvVlclJn5WPWQIvENCMickfD32T96V2B"

# options=Options()
# options.binary_location = '/app/.apt/usr/bin/google-chrome'
# options.add_argument('--headless')
# driver=webdriver.Chrome(chrome_options=options)
driver=webdriver.PhantomJS()
driver.set_window_size(1124, 850)
driver.implicitly_wait(30)
driver.get(URL)
WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "ProductList_item_inner")))
html=driver.page_source.encode('utf-8')

soup=BeautifulSoup(html, 'html.parser')
commodities=soup.find_all('a',attrs={'class':'ProductList_item_inner'})
# print(commodities)
productID=commodities[random.randint(0,SERIES_RANGE)].get('href')

driver.get(URL+productID)
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
driver.get(URL+productID+'&page='+str(pageNum))
WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "FAQResultList_item")))
html=driver.page_source.encode('utf-8')
driver.close()
driver.quit()

soup=BeautifulSoup(html, 'html.parser')
listItems=soup.find_all('li',attrs={'class':'FAQResultList_item'})
keyCards=listItems[num%10].find_all('a',attrs={'class':'popup-card-detail'})
for card in keyCards:
    print(card.string)
bodys=listItems[num%10].find_all('div',attrs={'class':'BodyArea'})
for body in bodys:
    print(body.text)



# auth=twitter.OAuth(consumer_key=CONSUMER_KEY,
#     consumer_secret=CONSUMER_SECRET,
#     token=TOKEN,
#     token_secret=TOKEN_SECRET)
# t=twitter.Twitter(auth=auth)
# status="Hello World"
# t.statuses.update(status=status)
