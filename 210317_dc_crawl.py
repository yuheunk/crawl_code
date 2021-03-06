#%%
## Library
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json
import re
import pandas as pd

## Load Data
store_lst = pd.read_csv('안심식당_20210316.csv')
store_name = store_lst['시군구명'] + ' ' + store_lst['사업장명']
queries = [name.replace('\n', '').replace('/', '') for name in store_name]  # 검색어 지정
# %% 
## 다이닝코드 홈페이지
driver = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver2 = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver.implicitly_wait(3)

HOMEPG = 'dc'
url = 'https://www.diningcode.com'
idx = 0
result = {}

for query in queries:
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
    if not soup.find('div', id='div_rn'):  # 첫번째 검색에 없다
        result[idx] = {}
        result[idx]['name'] = query
        result[idx]['tel'] = None
        result[idx]['menus'] = None
    else:
        gugun = query.split()[0][:2]  # 구군 정보
        rest_name = query.split()[1][:3]  # 레스토랑 이름
        # 첫번째 검색 목록 데이터
        data = soup.select('#div_rn > ul > li')[0]  
        search_name = re.sub('\s+', '', data.select_one('span.btxt').text).replace('1.', '')  # 검색 결과 식당 이름 추출

        ## 조건: 찾고자 하는 식당이 검색에 뜬다
        # 첫 번째 데이터 주소와 구군이 일치하면 새로운 주소로 넘어감
        # (근데 세종시는 0번째 인덱스에 있는 예외라서 따로 다시 구함)
        if (gugun in data.select_one('span.ctxt').text.split()[1]) and (rest_name in search_name):
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
            result[idx]['tel'] = tel
            result[idx]['menus'] = menu_lst

        # 찾고자 하는 식당이 아니면
        else:
            result[idx] = {}
            result[idx]['name'] = query
            result[idx]['tel'] = None
            result[idx]['menus'] = None
    
    ## 쉬기 왜 15초나? 좀 더 생각하고 짤걸ㅠ
    if idx%10==5:
        print(f'---Crawled {idx} restaurants\nRest for 15 seconds...')
        time.sleep(15)
    if idx!=0 and idx%10==0:
        print(f'---Crawled {idx} restaurants\nRest for 15 seconds...')
        time.sleep(15)
    if idx!=0 and idx%30==0:
        with open(f'./dc_json/{idx}dc_data.json', mode='w', encoding='utf-8') as fp:
            json.dump(result, fp)
    idx += 1

print('---DONE---')

driver.close()
driver2.close()

# 딕셔너리 저장
print('\nSave dictionary as data form..')
with open('dc_fulldata.json', 'w') as fp:
    json.dump(result, fp)