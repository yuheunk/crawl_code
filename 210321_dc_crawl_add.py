#%%
from selenium import webdriver
from bs4 import BeautifulSoup

import time
import json

import re
import pandas as pd
store_lst = pd.read_csv('dc_weird_num.csv')

store_name = store_lst['시도명'] + ' ' + store_lst['시군구명'] + ' ' + store_lst['사업장명']
idxs = list(store_lst['index'])
queries = [name.replace('\n', '').replace('/', '') for name in store_name]
# %% 다이닝코드 홈페이지
driver = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver2 = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver.implicitly_wait(3)

HOMEPG = 'dc'
url = 'https://www.diningcode.com'
num = 0
result = {}

for idx, query in zip(idxs, queries):
    # 다이닝코드 오픈
    driver.get(url)
    time.sleep(0.5)
    # 검색어 입력 및 검색
    element = driver.find_element_by_name('query')
    element.send_keys(query)
    element.submit()
    # 검색 목록 데이터
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    ## 조건: 첫번째 검색 목록 유무
    if not soup.find('div', id='div_rn'):
        result[idx] = {}
        result[idx]['name'] = query
        result[idx]['tel'] = None
        result[idx]['menus'] = None
    else:
        data = soup.select('#div_rn > ul > li')[0]  # 첫번째 검색 목록 데이터
        gugun = query.split()[1][:2]  # 구군 정보 추출
        rest_name = query.split()[2][:3]
        search_name = re.sub('\s+', '', data.select_one('span.btxt').text).replace('1.', '')

        ## 조건: 찾고자 하는 식당이 검색에 뜬다
        if (gugun in data.select_one('span.ctxt').text.split()[1]) and (rest_name in search_name):  # 첫 번째 데이터 주소와 구군이 일치하면 새로운 주소로 넘어감
            # 새로운 주소 고
            detail_url = data.select_one('a').get('href')
            driver2.get(url + detail_url)
            time.sleep(0.5)

            # 검색 결과 html 저장
            QUERY = query.replace(' ', '_')
            with open(f'./dc_html/{idx}_{HOMEPG}_{QUERY}.html', mode='w', encoding='utf-8') as f:
                f.write(driver2.page_source)
            
            # 검색 결과 창 소스
            soup = BeautifulSoup(driver2.page_source, 'html.parser')
            details = soup.find('div', class_='menu-info short')
            tel = soup.find('li', attrs={'class': 'tel'})

            ## 조건: 메뉴 있는 경우
            if details:
                ## 조건: 메뉴 더보기 유무
                if soup.find('a', class_='more-btn'):
                    driver2.find_element_by_xpath("//span[text()='더보기']").click()
                soup2 = BeautifulSoup(driver2.page_source, 'html.parser')
                
                ## 조건: 전화번호 유무
                if tel:
                    phone = soup2.find('li', attrs={'class': 'tel'}).text  # 전화번호
                else:
                    phone = None
                
                menus = soup2.find_all('span', attrs={'class':'Restaurant_Menu'}) # 메뉴목록
                menu_lst = [m.text for m in menus]
            
            ## 조건: 메뉴 없는 경우
            else:
                ## 조건: 전화번호 유무
                if tel:
                    phone = soup.find('li', attrs={'class': 'tel'}).text  # 전화번호
                else:
                    phone = None
                menu_lst = None

            result[idx] = {}
            result[idx]['name'] = query
            result[idx]['tel'] = phone
            result[idx]['menus'] = menu_lst

        # 찾고자 하는 식당이 아니면
        else:
            result[idx] = {}
            result[idx]['name'] = query
            result[idx]['tel'] = None
            result[idx]['menus'] = None
        
    if num%10==5:
        print(f'---Crawled {num}/{len(idxs)} restaurants\nRest for 5 seconds...')
        time.sleep(5)
    if num!=0 and num%10==0:
        print(f'---Crawled {num}/{len({idxs})} restaurants\nRest for 5 seconds...')
        time.sleep(5)
    if num!=0 and num%30==0:
        with open(f'./dc_json/{idx}dc_data.json', mode='w', encoding='utf-8') as fp:
            json.dump(result, fp)
    num += 1
    time.sleep(3)

print('---DONE---')

driver.close()
driver2.close()

# 딕셔너리 저장
print('\nSave dictionary as data form..')
with open('dc_fulldata.json', 'w') as fp:
    json.dump(result, fp)