#%%
import pandas as pd
# 수집된 데이터 불러오기
first = pd.read_json('3030dc_data.json', orient='index')
second = pd.read_json('23430dc_data.json', orient='index')
last = pd.read_json('23430tofinal_data.json', orient='index')
# 합치기
diningcode = pd.concat([pd.concat([first, second]), last])

#%%
# 세종시 정보 불러오기
sejong = pd.read_json('dc_sejong_data.json', orient='index')
sejong_idx = list(sejong.index)  # 세종시 인덱스 리스트
sejong = sejong.reset_index()
# 세종시 인덱스 떨구고
diningcode = diningcode.drop(sejong_idx, axis=0).reset_index()
# 세종시 업데이트 정보 합치기
diningcode2 = pd.concat([diningcode, sejong]).sort_values(by='index', ascending=True).reset_index().drop(['level_0', 'index'], axis=1)
# %%
diningcode2['시군구명'] = diningcode2['name'].apply(lambda x: x.split()[0])
diningcode2['사업장명'] = diningcode2['name'].apply(lambda x: ' '.join(x.split()[1:]))
diningcode2 = diningcode2[['시군구명', '사업장명', 'tel', 'menus']]
diningcode2 = diningcode2.rename(columns={'tel': 'dc_tel', 'menus': 'dc_menus'})
diningcode2.head()
# %%
# 원래 데이터
orig = pd.read_csv('./raw_data/안심식당_20210316.csv')

# 원래 데이터에서 필요한 컬럼만 뽑기
orig2 = orig[['시도명', '시군구명', '사업장명', '주소1', '주소2', '업종', '전화번호']]
orig2 = orig2.reset_index()
orig2.head()
# %%
# 국번이 다르게 뽑힌 애들 찾기 위해서 원래 데이터랑 합쳐본다
# 식신 크롤링 데이터 합치기
dc_merge = orig2.copy()
dc_merge['dc_tel'] = diningcode2['dc_tel']
dc_merge['dc_menus'] = diningcode2['dc_menus']
# 크롤링된 row만 뽑아봄
dc_tmp = dc_merge[~dc_merge.isnull().any(axis=1)]
# %%
city_num = {
    '서울특별시': '02',
    '경기도': '031',
    '인천광역시': '032',
    '강원도': '033',
    '충청남도': '041',
    '대전광역시': '042',
    '충청북도': '043',
    '세종특별자치시': '044',
    '부산광역시': '051',
    '울산광역시': '052',
    '대구광역시': '053',
    '경상북도': '054',
    '경상남도': '055',
    '전라남도': '061',
    '광주광역시': '062',
    '전라북도': '063',
    '제주특별자치도': '064'
}
# %%
# 전화번호 앞자리가 다른 애들
weird_num = dc_tmp.loc[~(dc_tmp['전화번호'].apply(lambda x: x[:3]) == dc_tmp['dc_tel'].apply(lambda x: x[:3]))]
weird_idx = []
# 크롤링된 데이터 중 국번이 주소지랑 다른 경우 인덱스를 따로 저장
for _ in list(weird_num.index):
    front_num = city_num[weird_num.loc[_, '시도명']]
    dc_front_num = weird_num['dc_tel'].apply(lambda x: x[:3])[_]
    if front_num != dc_front_num:
        weird_idx.append(_)

# 지역과 수집된 전화번호 지역번호가 다른 애들..
weird_num = weird_num.loc[weird_idx]
# 이 데이터로 다시 크롤링 돌리기
weird_num.to_csv('dc_weird_num.csv', index=False)
# %%
