#%%
import pandas as pd

# 식신 전체 크롤링 데이터
siksin = pd.read_json('./siksin/sik_fulldata.json', orient='index')
siksin['시군구명'] = siksin['name'].apply(lambda x: x.split()[0])
siksin['사업장명'] = siksin['name'].apply(lambda x: ' '.join(x.split()[1:]))
siksin = siksin[['시군구명', '사업장명', 'tel', 'menus']]
siksin = siksin.rename(columns={'tel': 'sik_tel', 'menus': 'sik_menus'})
siksin.head()
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
sik_merge = orig2.copy()
sik_merge['sik_tel'] = siksin['sik_tel']
sik_merge['sik_menus'] = siksin['sik_menus']
# 크롤링된 row만 뽑아봄
sik_tmp = sik_merge[~sik_merge.isnull().any(axis=1)]
# %%
# 도시별 번호
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
#%%
# 전화번호 앞자리가 다른 애들
weird_num = sik_tmp.loc[~(sik_tmp['전화번호'].apply(lambda x: x[:3]) == sik_tmp['sik_tel'].apply(lambda x: x[:3]))]
weird_idx = []
# 크롤링된 데이터 중 국번이 주소지랑 다른 경우 인덱스를 따로 저장
for _ in list(weird_num.index):
    front_num = city_num[weird_num.loc[_, '시도명']]
    sik_front_num = weird_num['sik_tel'].apply(lambda x: x[:3])[_]
    if front_num != sik_front_num:
        weird_idx.append(_)

# 지역과 수집된 전화번호 지역번호가 다른 애들..
weird_num = weird_num.loc[weird_idx]
# 이 데이터로 다시 크롤링 돌리기
# weird_num.to_csv('sik_weird_num.csv', index=False)
# %%
# 번호 이상한 애들 새로 수집했다!
fix_num = pd.read_json('sik_fulldata2.json', orient='index')
fix_num['시도명'] = fix_num['name'].apply(lambda x: x.split()[0])
fix_num['시군구명'] = fix_num['name'].apply(lambda x: x.split()[1])
fix_num['사업장명'] = fix_num['name'].apply(lambda x: ' '.join(x.split()[2:]))
fix_num = fix_num[['시도명', '시군구명', '사업장명', 'tel', 'menus']]
fix_num = fix_num.rename(columns={'tel': 'sik_tel', 'menus': 'sik_menus'})
fix_num = fix_num.reset_index()
# %%
add_idx = list(fix_num['index'])  # 수정한 애들
# 원래 식신 데이터에서 오류 난 애들 삭제
siksin2 = siksin.drop(add_idx, axis=0).reset_index()
# 데이터 합치기 위해 fix_num에서 시도명 컬럼 제거
fix_num = fix_num.drop('시도명', axis=1)
# 최종 업데이트된 식신 크롤링 데이터
siksin_update = pd.concat([siksin2, fix_num]).sort_values(by='index', ascending=True)
siksin_update = siksin_update.reset_index().drop(['level_0', 'index'], axis=1)
#%%
# 원래 데이터랑 크롤링한 데이터 합치자
sik_merge2 = orig2.copy()
sik_merge2 = sik_merge2.drop('index', axis=1)
sik_merge2['sik_tel'] = siksin_update['sik_tel']
sik_merge2['sik_menus'] = siksin_update['sik_menus']
# %%
sik_final = sik_merge2.drop('전화번호', axis=1)
sik_final.to_csv('siksin_crawl.csv', index=False)
# %%
