from lib2to3.pgen2 import driver
from turtle import title
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import load_workbook
import os,sys

driver_loc = os.environ.get("CHROME_DRIVER_LOC",r"C:\Users\saiam\OneDrive\Desktop\chrome_driver\chromedriver.exe")



class Scraper():

    def __init__(self,driver):
        self.driver = driver
        
        
    def get_driver(self):
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument('ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument("--headless")
        #options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(executable_path=self.driver, options=options)
        driver.maximize_window()
        return driver

    def launch_driver(self):
        self.driver = self.get_driver()
        return self.driver

    def open_website(self,website):
        self.driver.get(website)
    
    def get_page_source(self):
        return self.driver.page_source

    def close(self):
        self.driver.close()
        self.driver.quit()



   

scraper =  Scraper(driver = driver_loc)
d = scraper.launch_driver()
scraper.open_website(website='https://www.bbc.com/')
get_page_source = scraper.get_page_source()
soup = BeautifulSoup(get_page_source, "html.parser")
#media_links =  soup.find_all("a", {"class": "media__link"})['href']
links =  soup.find_all(href=True)
ref = set()
for h in links:
    ref.add(h.get('href'))

df = pd.DataFrame({'ref':list(ref)})
workbook = load_workbook('bbc_links_test_03.xlsx')
writer  =  pd.ExcelWriter('bbc_links_test_03.xlsx',engine = 'openpyxl')
writer.book = workbook 
df.to_excel(writer, sheet_name = 'links',index=False)

urls = []
title = {}
text_main = {}
url_main = {}
for index, row in df.iterrows():
    #if  (row['ref'].startswith('/news' ) or 'www.bbc.com/news/' in row['ref'] ) and any(i.isdigit() for i in  row['ref']) :
    if (row['ref'].startswith('/' )):
        url = 'https://www.bbc.com' + row['ref']
    else:
        url = row['ref']
    urls.append(url)
    
    try:
        scraper.open_website(website=url)
        time.sleep(1)
        get_page_source_article = scraper.get_page_source()
        soup = BeautifulSoup(get_page_source_article , "html.parser")
        
        x = soup.find("h1", {"id": "main-heading"}).text
        
        if x:
            url_main[index] = url
            text = soup.find_all("div", {"data-component": "text-block"})
            text_main[index] = []
            for t in text:
                text_main[index].append(t.text)

            if index in title:
                title[index].expend([x])
            else:
                title[index] = [x]     
        
    except:
        url_main[index] = url
        text_main[index] = 'Not Available'
        title[index] = 'Not Available'
        pass
        

df_text =  pd.DataFrame({'url':url_main,'title':title,'text':text_main})
df_text['title'] = df_text['title'].apply(lambda x : x if x else 'Not Available')
df_text['text'] = df_text['text'].apply(lambda x : x if x else 'Not Available')

df_text.to_excel(writer,sheet_name= 'links_text',index=False)
writer.save()
writer.close()
        
time.sleep(10)
scraper.close()