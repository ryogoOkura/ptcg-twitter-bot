from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json

# options=Options()
driver=webdriver.PhantomJS()
driver.set_window_size(1124, 850)
driver.implicitly_wait(20)
url='https://www.pokemon-card.com/rules/faq/'
driver.get(url)
WAIT_SECOND=30
WebDriverWait(driver,WAIT_SECOND).until(EC.presence_of_element_located((By.CLASS_NAME, "ProductList_item_inner")))
html=driver.page_source.encode('utf-8')
driver.close()
driver.quit()

soup=BeautifulSoup(html, 'html.parser')
# attributes=soup.find_all('a',attrs={'class':'ProductList_item_inner'})
a=soup.find('a',attrs={'class':'ProductList_item_inner'})
print(a.href)

# import twitter
# CONSUMER_KEY="0PWItx3y8rT56fHmoksjCD3p8"
# CONSUMER_SECRET="Oc7v7lETeQdhOb2mnCXd3hiSBlgJ4DlYSADt7uZlBFSo9IRpbB"
# TOKEN="1103483478723584000-WCkBL5Hjf5bB6rZlsbgrSy2LrPLj8I"
# TOKEN_SECRET="FiRIR90V4wBv8TvVlclJn5WPWQIvENCMickfD32T96V2B"
#
# auth=twitter.OAuth(consumer_key=CONSUMER_KEY,
#     consumer_secret=CONSUMER_SECRET,
#     token=TOKEN,
#     token_secret=TOKEN_SECRET)
# t=twitter.Twitter(auth=auth)
# status="Hello World"
# t.statuses.update(status=status)
