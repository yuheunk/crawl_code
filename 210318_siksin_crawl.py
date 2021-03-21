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
queries = [name for name in store_name]  # 검색어 지정
# %% 
## 식신 홈페이지
driver = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver2 = webdriver.Chrome('/Users/yuheunkim/Downloads/chromedriver')
driver.implicitly_wait(3)
driver2.implicitly_wait(3)

HOMEPG = 'sik'
url = 'https://www.siksinhot.com'
idx = 0
result = {}

# 식신 오픈
driver.get(url)
time.sleep(0.5)

for query in queries:
    # 검색어 입력 및 검색
    element = driver.find_element_by_name('q')
    element.send_keys(query)
    driver.find_element_by_xpath('//*[@id="header"]/div[2]/div[1]/div/a/div/div').click()
    # 검색 목록 데이터
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    gugun = query.split()[0][:2]  # 구군 정보 추출
    rest_name = query.split()[1]  # 식당 이름

    data = soup.select('#schMove1 > div.listTy1 > ul > li')[0]  # 첫번째 검색 목록 데이터
    search_name = re.sub('\s+', '', data.select_one('strong.store').text)  # 검색 결과 식당 이름

    ## 조건: 찾고자 하는 식당이 검색에 뜬다
    # 제주시 -> 제주시내 로 적혀 있기도 해서 앞 두개만 뽑아서 비교
    # 검색어와 검색 결과도 앞 두개만 뽑아서 비교
    if (data.find('li').text[:2] in gugun) and (rest_name[:3] in search_name):  # 첫 번째 데이터 주소와 구군이 일치하면 새로운 주소로 넘어감
        # 새로운 주소 고
        detail_url = data.select_one('a').get('href')
        driver2.get(url + detail_url)
        time.sleep(0.5)

        # 검색 결과 html 저장
        QUERY = query.replace(' ', '_')
        with open(f'./sik_html/{idx}_{HOMEPG}_{QUERY}.html', mode='w', encoding='utf-8') as f:
            f.write(driver2.page_source)

        # 검색 결과 창 소스
        soup = BeautifulSoup(driver2.page_source, 'html.parser')
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

    # 상황 보고
    if idx%10==5:
        print(f'---Crawled {idx} restaurants')
    if idx!=0 and idx%10==0:
        print(f'---Crawled {idx} restaurants')
    if idx!=0 and idx%30==0:
        with open(f'./sik_json/{idx}sik_data.json', 'w') as fp:
            json.dump(result, fp)
    idx+=1

print('---DONE---')

driver.close()
driver2.close()

# 딕셔너리 저장
print('\nSave dictionary as data form..')
with open('sik_fulldata.json', 'w') as fp:
    json.dump(result, fp)