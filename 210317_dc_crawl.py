#%%
from selenium import webdriver
from bs4 import BeautifulSoup

import time
import json

import re
import pandas as pd
store_lst = pd.read_csv('안심식당_20210316.csv')

store_name = store_lst['시군구명'] + ' ' + store_lst['사업장명']
queries = [name.replace('\n', '') for name in store_name]
# %% 다이닝코드 홈페이지
driver = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver2 = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver.implicitly_wait(3)

HOMEPG = 'dc'
url = 'https://www.diningcode.com'
idx = 0
result = {}

for query in queries:
    if idx%10==5:
        print(f'---Crawled {idx} restaurants\nRest for 15 seconds...')
        time.sleep(15)
    if idx%10==9:
        print(f'---Crawled {idx} restaurants\nRest for 15 seconds...')
        time.sleep(15)

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
        idx += 1

    else:
        data = soup.select('#div_rn > ul > li')[0]  # 첫번째 검색 목록 데이터
        gugun = query.split()[0][:2]  # 구군 정보 추출
        rest_name = query.split()[1][:3]
        search_name = re.sub('\s+', '', data.select_one('span.btxt').text).replace('1.', '')

        ## 조건: 찾고자 하는 식당이 검색에 뜬다
        if (gugun in data.select_one('span.ctxt').text.split()[1]) and (rest_name in search_name):  # 첫 번째 데이터 주소와 구군이 일치하면 새로운 주소로 넘어감
            # 새로운 주소 고
            detail_url = data.select_one('a').get('href')
            driver2.get(url + detail_url)
            time.sleep(0.5)

            # 검색 결과 html 저장
            QUERY = query.replace(' ', '_')
            with open(f'./pages/{idx}_{HOMEPG}_{QUERY}.html', 'w') as f:
                f.write(driver2.page_source)
            
            # 검색 결과 창 소스
            soup = BeautifulSoup(driver2.page_source, 'html.parser')

            ## 조건: 메뉴 유무
            details = soup.find('div', class_='menu-info short')
            
            if details:
                ## 조건: 메뉴 더보기 유무
                if soup.find('a', class_='more-btn'):
                    driver2.find_element_by_xpath("//span[text()='더보기']").click()
                soup2 = BeautifulSoup(driver2.page_source, 'html.parser')
                # 전화번호와 메뉴
                tel = soup2.find('li', attrs={'class': 'tel'}).text  # 전화번호
                menus = soup2.find_all('span', attrs={'class':'Restaurant_Menu'}) # 메뉴목록
                menu_lst = [m.text for m in menus]
            else:
                tel = soup.find('li', attrs={'class': 'tel'}).text  # 전화번호
                menu_lst = None

            result[idx] = {}
            result[idx]['name'] = query
            result[idx]['tel'] = tel
            result[idx]['menus'] = menu_lst

        # 찾고자 하는 식당이 아니면
        else:
            result[idx] = {}
            result[idx]['name'] = query
            result[idx]['tel'] = None
            result[idx]['menus'] = None
        
        idx += 1
print('---DONE---')

driver.close()
driver2.close()

# 딕셔너리 저장
print('\nSave dictionary as data form..')
with open('dc_data.json', 'w') as fp:
    json.dump(result, fp)

# tmp = pd.read_json('data.json', orient='index')
# tmp['시군구'] = tmp['name'].apply(lambda x: x.split()[0])
# tmp['name'] = tmp['name'].apply(lambda x: ' '.join(x.split()[1:]))