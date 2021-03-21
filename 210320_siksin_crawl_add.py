#%%
from selenium import webdriver
from bs4 import BeautifulSoup

import time
import json

import re
import pandas as pd

store_lst = pd.read_csv('sik_weird_num.csv')

store_name = store_lst['시도명'] + ' ' + store_lst['시군구명'] + ' ' + store_lst['사업장명']
idxs = list(store_lst['index'])
queries = [name.replace('\n', '').replace('/', '') for name in store_name]
# %% 식신 홈페이지
driver = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver2 = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver.implicitly_wait(3)
driver2.implicitly_wait(3)

HOMEPG = 'sik'
url = 'https://www.siksinhot.com'
num = 0
result = {}

driver.get(url)
time.sleep(0.5)

for idx, query in zip(idxs, queries):
    element = driver.find_element_by_name('q')
    element.send_keys(query)
    driver.find_element_by_xpath('//*[@id="header"]/div[2]/div[1]/div/a/div/div').click()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    if not soup.find('div', class_='listTy1'):
        result[idx] = {}
        result[idx]['name'] = query
        result[idx]['tel'] = None
        result[idx]['menus'] = None    
    else:
        data = soup.select('#schMove1 > div.listTy1 > ul > li')[0]  # 첫번째 검색 목록 데이터
        gugun = query.split()[1][:2]  # 구군 정보 추출
        rest_name = query.split()[2]
        search_name = re.sub('\s+', '', data.select_one('strong.store').text)

        ## 조건: 찾고자 하는 식당이 검색에 뜬다
        # 제주시 -> 제주시내 로 적혀 있기도 해서 앞 두개만 뽑아서 비교
        # 검색어와 검색 결과도 앞 두개만 뽑아서 비교
        if (gugun in data.find('li').text) and (rest_name[:3] in search_name):  # 첫 번째 데이터 주소와 구군이 일치하면 새로운 주소로 넘어감
            # 새로운 주소 고
            detail_url = data.select_one('a').get('href')
            driver2.get(url + detail_url)
            time.sleep(0.5)

            # 검색 결과 html 저장
            QUERY = '_'.join(query.split()[1:])
            with open(f'./sik_html/{idx}_{HOMEPG}_{QUERY}.html', mode='w', encoding='utf-8') as f:
                f.write(driver2.page_source)

            soup = BeautifulSoup(driver2.page_source, 'html.parser')
            tel = soup.find('div', class_='p_tel').text.replace('전화번호', '')

            details = soup.find('ul', class_='menu_ul')
            tel = soup.find('div', class_='p_tel')

            ## 조건: 메뉴 + 전화번호 존재
            if details and tel:
                phone = soup.find('div', class_='p_tel').text.replace('전화번호', '')
                menus = soup.find('ul', class_='menu_ul').find_all('span', class_='tit') # 메뉴목록
                menu_lst = [m.text.strip('\n') for m in menus]
            ## 조건: 메뉴 있음, 전화번호 없음
            elif details and not tel:
                phone = None
                menus = soup.find('ul', class_='menu_ul').find_all('span', class_='tit') # 메뉴목록
                menu_lst = [m.text.strip('\n') for m in menus]
            ## 조건: 메뉴 없음, 전화번호 있음
            elif not details and tel:
                phone = soup.find('div', class_='p_tel').text.replace('전화번호', '')
                menu_lst = None
            ## 조건: 메뉴 + 전화번호 모두 부재
            else:
                phone = None
                menu_lst = None
            
            result[idx] = {}
            result[idx]['name'] = query
            result[idx]['tel'] = phone
            result[idx]['menus'] = menu_lst

        else:
            result[idx] = {}
            result[idx]['name'] = query
            result[idx]['tel'] = None
            result[idx]['menus'] = None

    if num%10==5:
        print(f'---Crawled {num}/{len(idxs)} restaurants')
    if num!=0 and num%10==0:
        print(f'---Crawled {num}/{len(idxs)} restaurants')
        with open(f'./sik_json/{num}sik_data.json', 'w') as fp:
            json.dump(result, fp)
    num+=1


print('---DONE---')
driver.close()
driver2.close()

# 딕셔너리 저장
print('\nSave dictionary as data form..')
with open('sik_fulldata2.json', 'w') as fp:
    json.dump(result, fp)