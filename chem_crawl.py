## Library
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re
import pandas as pd
from tqdm import tqdm

df = pd.read_csv('save_crawl.csv')
links = df.Links.tolist()

def save_table(h3_name, h3_title):
    i=0
    header = h3_name.find_next_sibling('h4')

    while i < 3:
        header_title = header.text

        if (header_title == 'Components') or (header_title=='Data Table'):
            header_table = header.find_next_sibling('table')
            table_rows = header_table.find_all('tr')

            cols_lst = table_rows[0].findAll('th')
            cols = [tr.text for tr in cols_lst]

            l = []
            for tr in table_rows:
                td = tr.find_all('td')
                row = [tr.text for tr in td]
                l.append(row)
            df = pd.DataFrame(l[1:], columns=cols)
            df.to_csv(f'{h3_title}_{header_title}.csv', index=False)
            
            header = header.find_next_sibling('h4')
            i += 1

        elif header_title == 'Constant Value':
            header_table = header.find_next_sibling('table')
            type = header_table.th.text  # 종류: Temperature or Pressure
            v = float(header_table.td.text)  # 수치

            result = [[type, v]]
            df = pd.DataFrame(result)
            df.to_csv(f'{h3_title}_{header_title}.csv', index=False, header=False)

            header = header.find_next_sibling('h4')
            i += 1

        else:
            i += 1
            continue

## 홈페이지
driver = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')   ## CHROMEDRIVER DIR
driver.implicitly_wait(3)

url = 'http://www.ddbst.com/en/EED/VLE/'

for l in tqdm(links):
    # 링크 열기
    driver.get(url + l)
    time.sleep(0.5)
    # 소스 보기
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    if len(soup.find_all('h3')) == 1:
        dataset = soup.h3
        dataset_title = dataset.text
        save_table(dataset, dataset_title)

    elif len(soup.find_all('h3')) > 1:
        dataset = soup.h3
        dataset_title = dataset.text
        
        i = 0
        while i < len(soup.find_all('h3')):
            dataset_title = dataset.text
            save_table(dataset, dataset_title)
            i+=1
            dataset = dataset.find_next_sibling('h3')

driver.close()
