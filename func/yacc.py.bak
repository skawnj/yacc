# -*- coding: utf-8 -*-
# Last Modified: 2016-06-22 01:28
# Last Modified: 2016-06-03 18:48
#from lxml import html
from urllib.parse import urljoin
import os
import requests
import sqlite3
import re
import random
import datetime
import math
import pickle
import json
#from django.db import models
from .models import NicknameSrcAdj

# 숙제
'''
* 야식당 부점별
* 용도별로 class화하기
* 쿼리 작성 시 "'"를 어떻게 핸들링할 것인지?
* 사용자의 식당 상세 뷰 시 기록
* 사용자 기반 목록 갯수가 뒤쳐질 경우 나머지는 랜덤으로? 아니면 비사용자 기반 추출 값으로?
* 다이닝코드 실시간 데이터 입수
* 데이터 분석: 가중치 랜덤(intelligent random) 구현(기준치: 날씨, 성향 분석 등)
* 현재 식당상세 조회 시 히트 수와 유저 열람 기록을 남기는데, 랜덤 연결인 경우에도 그러해야 하는지?
    - 랜덤 후 클릭해 들어가야 상세 뷰이도록 제약한다면 크게 문제 없을듯?
    - 필요하다면 흔적 안남기는 옵션을 두는 것도 방법임.
* 사용자 상세 열람 기록의 '체류 시간' 개념은 min(다른 열람 발생 때까지의 시간차, 3분)으로 함.
    - 갱신 시점: 상세 열람 기록 발생 시 바로 직전 것의 체류 시간 값을 계산해 반영시킴.
* 최종 접속 일시: session_id와 최종접속일시 데이터 둘만 관리
* json 처리, view 처리
* 세션 카운터? 스레드로 띄웠다가 일정 시간 지나면 체류 시간을 정리?
'''

# 전역 변수
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), 'yacc5.db')
TESTDATA_PATH = os.path.join(os.path.dirname(__file__), 'pkle')
HQ_COORD = (126.920762, 37.5283199) # 본점 좌표(네이버 API로 미리 추출)
IT_COORD = (126.9220432, 37.5278059) # 별관 좌표(네이버 API로 미리 추출)
"""
# 크롤링
def _crawl(query = '홍대', count = 100): # query를 검색어로 하여 총 count개를 긁어 옴.
    base_url = 'http://diningcode.com'
    target_url = urljoin(base_url, '/list.php?query={0}'.format(query))

    item_no = 0
    res_set = []
    while target_url != None:
        target_page = html.fromstring(requests.get(target_url).content)

        r = target_page.xpath("//dc-restaurant")
        for restr in r:
            restr_name = restr.xpath(".//div[@class='dc-restaurant-name']")[0].text_content().strip()
            restr_info = restr.xpath(".//div[@class='dc-restaurant-info-text']")
            restr_addr = restr_info[1].text_content().strip()
            try:
                restr_coord = _get_addr_coord(re.search(r'·\s*(.+)', restr_addr).group(1))
            except Exception as e:
                print(e)
                return(None)
            restr_phone = restr_info[2].text_content().strip()
            detail_url = urljoin(base_url, restr.xpath(".//div[@class='dc-restaurant-name']/a")[0].get('href'))
            thumbnail_url = restr.xpath(".//dc-rimage")[0].get('data-image').split(',')[0]
            #print(thumbnail_url)
            #thumbnail_url = restr.xpath("")
            res_set.append([item_no, restr_name, restr_addr, restr_phone, (restr_coord['x'], restr_coord['y']), detail_url, thumbnail_url])

            item_no += 1
            if item_no >= count:
                return(res_set)

        # 다이닝코드 다음 페이지 이동 처리(하단 페이징 바 분석)
        page_following = target_page.xpath("//div[@id='page_index']//td[@class='page-index-cell active']/following-sibling::td") # 현재 페이지 직후 sibling DOM 찾기
        if len(page_following) > 0: # 직후 sibling DOM이 존재할 경우
            if page_following[0].get('class') == 'page-index-cell': # 다음 페이지가 존재하는 경우
                target_url = urljoin(base_url, page_following[0].xpath("./a")[0].get('href'))
            else:
                target_url = None # 대상 URL 해제하여 로직 반복 중단(while 루프 탈출)
        else:
            target_url = None # 대상 URL 해제하여 로직 반복 중단(while 루프 탈출)

    return(res_set)
"""
# 크롤링
def _get_addr_coord(addr = '서울특별시 영등포구 여의동로 257 천주교여의도교회'): # 주소에 대한 GPS 좌표 획득(네이버 지도)
    params = { 'encoding': 'utf-8', 'coord': 'latlng', 'output': 'json',
                'query': addr }
    headers = { 'Host': 'openapi.naver.com', 'User-Agent': 'curl/7.43.0',
                'Accept': '*/*', 'Content-Type': 'application/json',
                'X-Naver-Client-Id': 'ifyR4NmJDhUPaXgNALTw',
                'X-Naver-Client-Secret': 'JuEtxELOyT' }
    r = requests.get('https://openapi.naver.com/v1/map/geocode', params=params, headers=headers)
    #print(r.json())
    return r.json()['result']['items'][0]['point']

# DB
def _gen_db_schema():
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        # RESTR_BASE
        query = '''\
            CREATE TABLE RESTR_BASE
                (RID TEXT PRIMARY KEY, NAME TEXT, ADDR TEXT, PHONE TEXT, COORD_X REAL, COORD_Y REAL
                , DIST_HQ REAL, DIST_IT REAL, UPT_TIME TEXT, AVG_RATING REAL, HIT_SCORE INTEGER
                , DCODE_URL TEXT, THUMBNAIL_URL TEXT)
            '''
        cur.execute(query)
        # USER_BASE
        query = '''\
            CREATE TABLE USER_BASE
                (SID TEXT PRIMARY KEY, NICKNAME TEXT, REG_TIME TEXT, LAST_CONN_TIME TEXT)
            '''
        cur.execute(query)
        # USER_REVIEW
        query = '''\
            CREATE TABLE USER_REVIEW
                (SID TEXT, RID TEXT, REVIEW_TIME TEXT, RATING REAL, REVIEW_TXT TEXT
                , PRIMARY KEY(SID, RID, REVIEW_TIME)
                , FOREIGN KEY(SID) REFERENCES USER_BASE(SID)
                , FOREIGN KEY(RID) REFERENCES RESTR_BASE(RID))
            '''
        cur.execute(query)
        # NICKNAME_SRC_ADJ
        query = '''\
            CREATE TABLE NICKNAME_SRC_ADJ
                (ADJECTIVE TEXT PRIMARY KEY, CNT_USED INTEGER, LAST_USED_TIME TEXT)
            '''
        cur.execute(query)
        # NICKNAME_SRC_NOUN
        query = '''\
            CREATE TABLE NICKNAME_SRC_NOUN
                (NOUN TEXT PRIMARY KEY, CNT_USED INTEGER, LAST_USED_TIME TEXT)
            '''
        cur.execute(query)
        # USER_VIEW_HIST
        query = '''\
            CREATE TABLE USER_VIEW_HIST
                (SID TEXT, RID TEXT, VIEW_TIME TEXT, STAY_SECONDS INTEGER
                , PRIMARY KEY(SID, RID, VIEW_TIME)
                , FOREIGN KEY(SID) REFERENCES USER_BASE(SID)
                , FOREIGN KEY(RID) REFERENCES RESTR_BASE(RID))
            '''
        cur.execute(query)
        conn.commit()

# DB
def _calibrate_data():
    #settings.configure()
    nnsadj = NicknameSrcAdj.objects.create(adjective = 'abc', cnt_used = 0, last_used_time = datetime.datetime())
    nnsadj.save()
    return
    """with open(TESTDATA_PATH, 'rb') as fp:
        nickname_src = pickle.load(fp)
        ts = _get_timestamp()
        query = '''\
            INSERT INTO NICKNAME_SRC_ADJ VALUES
                {0}
        '''.format(', '.join(["('{0}', 0, '{1}')".format(i.replace("'", "`"), ts) for i in nickname_src[0]]))
        cur.execute(query)
        conn.commit()


        ts = _get_timestamp()
        query = '''\
            INSERT INTO NICKNAME_SRC_NOUN VALUES
                {0}
        '''.format(', '.join(["('{0}', 0, '{1}')".format(i.replace("'", "`"), ts) for i in nickname_src[1]]))
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()

    """
    # 강제로 세션 ID 전처리기를 실행해 세 명의 유저 세션을 생성함.
    _preproc_session_id('session_no_1357')
    _preproc_session_id('session_no_2468')
    _preproc_session_id('session_no_7777')

    #_insert_restr_list(_crawl('서여의도', 100))
    #'''
    with open(TESTDATA_PATH, 'rb') as fp:
        _insert_restr_list(pickle.load(fp)[2]) # 크롤링 수행을 않고 pickle된 것을 활용
    #'''

    #'''
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        tot_cnt = cur.execute('SELECT COUNT(*) FROM RESTR_BASE').fetchone()[0]
        random_restr = cur.execute('SELECT * FROM RESTR_BASE LIMIT 1 OFFSET {0}'.format(random.randint(0, tot_cnt - 1))).fetchone()
        set_user_review('session_no_1357', random_restr[0], 3.7, 'Not so bad.')
        random_restr = cur.execute('SELECT * FROM RESTR_BASE LIMIT 1 OFFSET {0}'.format(random.randint(0, tot_cnt - 1))).fetchone()
        set_user_review('session_no_1357', random_restr[0], 4.1, 'Fabulous! Recommended!')
        random_restr = cur.execute('SELECT * FROM RESTR_BASE LIMIT 1 OFFSET {0}'.format(random.randint(0, tot_cnt - 1))).fetchone()
        set_user_review('session_no_1357', random_restr[0], 2.0, 'I must got paid by them... Terrible.')
        set_user_review('session_no_2468', random_restr[0], 2.5, 'So so... :d')
        set_user_review('session_no_7777', random_restr[0], 3.9, "I do not know why people dislike here. It is of my fav place.")
    #'''

def _drop_tables():
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = "SELECT NAME FROM SQLITE_MASTER WHERE TYPE = 'table'" # 전체 테이블 목록
        cur.execute(query)
        res = cur.fetchall()
        if len(res) > 0:
            tab_list = list(zip(*res))[0]
            for tab in tab_list: # 전체 테이블 목록 인식해 모두 drop함.
                query = '''\
                    DROP TABLE IF EXISTS {0}
                    '''.format(tab)
                cur.execute(query)
                conn.commit()

# DB
def _insert_restr_list(restr_list):
    for i in restr_list:
        query = '''INSERT INTO RESTR_BASE VALUES
                    ('{0}', '{1}', '{2}', '{3}', {4}, {5}, {6}, {7}, '{8}', {9}, '{10}', '{11}', '{12}')'''.format\
                    ('R' + _get_timestamp(), i[1], i[2], i[3], i[4][0], i[4][1]
                    , _calc_distance(HQ_COORD, i[4]), _calc_distance(IT_COORD, i[4]), _get_timestamp()
                    #, random.uniform(3.0, 5.0) # RATING: 평가 전혀 없을 때 -1 설정
                    , -1 # RATING: 평가 전혀 없을 때 -1 설정
                    , 0, i[5], i[6])
        #print(query)
        with sqlite3.connect(DB_FILE_PATH) as conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()

# 사용자
#def preprocess_session():

# Misc.
def _get_timestamp(length = None):
    if length == None:
        #return(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:16])
        return(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
    else:
        return(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:length])

def _gen_nickname(): # 발음 가능한 랜덤 단어 생성
    '''target_url = 'http://soybomb.com/tricks/words'
    target_page = html.fromstring(requests.get(target_url).content)
    r = target_page.xpath("//font[@size='4']//tr/td/b")
    return(random.choice(r).text_content())'''
    nickname_generated = None
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = 'SELECT CNT_USED, COUNT(*) FROM NICKNAME_SRC_ADJ GROUP BY CNT_USED'
        cur.execute(query)
        least_freq, how_many = min(cur.fetchall(), key = lambda x: x[0])
        query = '''\
            SELECT * FROM NICKNAME_SRC_ADJ WHERE CNT_USED = {0}
                LIMIT 1 OFFSET {1}
            '''.format(least_freq, random.randint(1, how_many - 1))
        cur.execute(query)
        nickname_adj = cur.fetchone()[0] # 형용사 부분 획득(랜덤 취득)

        query = 'SELECT CNT_USED, COUNT(*) FROM NICKNAME_SRC_NOUN GROUP BY CNT_USED'
        cur.execute(query)
        least_freq, how_many = min(cur.fetchall(), key = lambda x: x[0])
        query = '''\
            SELECT * FROM NICKNAME_SRC_NOUN WHERE CNT_USED = {0}
                LIMIT 1 OFFSET {1}
            '''.format(least_freq, random.randint(1, how_many - 1))
        cur.execute(query)
        nickname_noun = cur.fetchone()[0] # 명사 부분 획득(랜덤 취득)

        # 사용된 형용사와 명사의 카운트 증가
        ts = _get_timestamp()
        query = '''\
            UPDATE NICKNAME_SRC_ADJ SET
                CNT_USED = CNT_USED + 1
                , LAST_USED_TIME = '{0}'
                WHERE ADJECTIVE = '{1}'
            '''.format(ts, nickname_adj.replace("'", "''"))
        cur.execute(query)
        conn.commit()
        query = '''\
            UPDATE NICKNAME_SRC_NOUN SET
                CNT_USED = CNT_USED + 1
                , LAST_USED_TIME = '{0}'
                WHERE NOUN = '{1}'
            '''.format(ts, nickname_noun.replace("'", "''"))
        cur.execute(query)
        conn.commit()

        nickname_generated = (nickname_adj + ' ' + nickname_noun).title() # 단어 단위 대문자화

    return(nickname_generated)

def _calc_distance(x, y):
    return(math.hypot(x[0] - y[0], x[1] - y[1]))

def _preproc_session_id(session_id):
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = "SELECT * FROM USER_BASE WHERE SID = '{0}'".format(session_id)
        cur.execute(query)
        res = cur.fetchone()

        ts = _get_timestamp()
        if res == None:
            query = '''\
                INSERT INTO USER_BASE VALUES
                    ('{0}', '{1}', '{2}', '{3}')
                '''.format(session_id, _gen_nickname(), ts, ts)
            cur.execute(query)
            conn.commit()
        else:
            query = '''\
                UPDATE USER_BASE SET
                    LAST_CONN_TIME = '{1}'
                    WHERE SID = '{0}'
                '''.format(session_id, ts)
            cur.execute(query)
            conn.commit()

def _search_restr_single_word(keyword): # 단일 단어
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = '''\
            SELECT RID, 'NAME', NAME
                FROM RESTR_BASE
                WHERE NAME LIKE '%{0}%'
            UNION ALL
            SELECT RID, 'ADDR', ADDR
                FROM RESTR_BASE
                WHERE ADDR LIKE '%{0}%'
            UNION ALL
            SELECT RID, 'PHONE', PHONE
                FROM RESTR_BASE
                WHERE PHONE LIKE '%{0}%'
            '''.format(keyword)
        cur.execute(query)
        res = cur.fetchall()
        return(res)

def _make_json_from_selection(selection, header):
    if len(selection) <= 0: # When nothing has been selected, return an empty dict
        return dict()
    if isinstance(selection[0], tuple) or isinstance(selection[0], list): # 2차원 리스트
        res = [dict(zip(header, i)) for i in selection] # 행 각각마다 헤더 접합
        res = dict(zip(range(1, len(selection) + 1), res)) # 각 행별로 순번 붙이기
    else: # 1차원 리스트 가정
        res = dict(zip(header, selection))
    #return(json.dumps(res, sort_keys = True))
    #return(json.dumps(res))
    return(res) # 딕셔너리로 반환

# 외부 제공 모듈들
def get_restr_list(count = 10, option = None, session_id = None):
    '''
    * 모듈명: 식당 목록 조회
    * 입력: 개수, 옵션, 세션 ID
    * 출력(JSON): 식당 ID, 식당명, 주소, 전화번호, X 좌표, Y 좌표, 본점 거리, 별관 거리, 갱신 시간, 평균 평점, 히트 점수, 다이닝코드 페이지 URL, 썸네일 이미지 URL, ...(목록)
        - [('R20160604010629153804', '보나베띠 여의도점', '여의도 · 서울시 영등포구 여의도동 16-2 1F (중소기업중앙회신관 건물 1층)', '02-780-3886', 126.9227388, 37.5281813, 0.001981652895951576, 0.0007904331217772451, '20160604010629153804', -1.0, 0, 'http://diningcode.com/profile.php?rid=fCBYskxnOCky&rank=27', 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/53247/58022/53247_58022_86_5_5326_201572673841549_300x200.jpg'), ('R20160604010629558074', '달맞이 꽃게탕', '여의도 · 서울특별시 영등포구 여의도동 16-2', '02-3775-0118', 126.9227388, 37.5281813, 0.001981652895951576, 0.0007904331217772451, '20160604010629558074', -1.0, 0, 'http://diningcode.com/profile.php?rid=F8IzY8XHgHtO&rank=58', 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/57189/50096/57189_50096_77_0_3036_201631802252364_300x200.jpg'), ...]
    * 예외: 조회된 내용이 없으면(0건) None 반환
    * 설명
        - 옵션
            - 'recent': 최근 갱신된 순서로 정렬
            - 'random': 임의 선택
            - 'rating': 평균 평점 높은 순서로 정렬
            - 'hit': 히트 점수 높은 순서로 정렬
            - 'closest_hq': 본점 거리 가까운 순서로 정렬
            - 'closest_it': 별관 거리 가까운 순서로 정렬
            - 'recommend': 데이터 기반 추천(미완성)
        - 리뷰가 전무한 식당은 평균 평점이 -1임.
        - '뭐 먹지?' 기능 구현은 n개짜리 임의 선택 목록을 조회한 후 순차적으로 상세 조회하는 식으로 해야 할 것임.
    * 미완성: 데이터 기반 추천 기능 구현 예정. 세션 ID 주어진 경우 사용자별 처리가 현재는 완전 미구현 상태
    '''
    if session_id != None:
        _preproc_session_id(session_id)

    restr_list = None
    if option == None:
        if session_id == None:
            with sqlite3.connect(DB_FILE_PATH) as conn:
                cur = conn.cursor()
                q = 'SELECT * FROM RESTR_BASE'
                cur.execute(q)
                restr_list = cur.fetchmany(count)
                header = list(zip(*cur.description))[0]
                restr_list = _make_json_from_selection(restr_list, header)
        else:
            print('Not defined option.')
    elif option == 'recent': ############### session_id 주어진 경우 사용자별 최근 방문
        if session_id == None:
            with sqlite3.connect(DB_FILE_PATH) as conn:
                cur = conn.cursor()
                q = 'SELECT * FROM RESTR_BASE ORDER BY UPT_TIME DESC'
                cur.execute(q)
                restr_list = cur.fetchmany(count)
                header = list(zip(*cur.description))[0]
                restr_list = _make_json_from_selection(restr_list, header)
        else:
            print('Not defined option.')
    elif option == 'random':
        if session_id == None:
            with sqlite3.connect(DB_FILE_PATH) as conn:
                cur = conn.cursor()
                query = 'SELECT * FROM RESTR_BASE ORDER BY RANDOM() LIMIT {0}'.format(count)
                cur.execute(query)
                restr_list = cur.fetchall()
                header = list(zip(*cur.description))[0]
                restr_list = _make_json_from_selection(restr_list, header)
        else:
            print('Not defined option.')
    elif option in ('rating', 'hit', 'closest_hq', 'closest_it'):
        if session_id == None:
            with sqlite3.connect(DB_FILE_PATH) as conn:
                if option == 'rating':
                    order_by_col = 'AVG_RATING DESC'
                elif option == 'hit':
                    order_by_col = 'HIT_SCORE DESC'
                elif option == 'closest_hq':
                    order_by_col = 'DIST_HQ'
                elif option == 'closest_it':
                    order_by_col = 'DIST_IT'
                else:
                    order_by_col = None
                cur = conn.cursor()
                q = 'SELECT * FROM RESTR_BASE ORDER BY {0}'.format(order_by_col)
                cur.execute(q)
                restr_list = cur.fetchmany(count)
                header = list(zip(*cur.description))[0]
                restr_list = _make_json_from_selection(restr_list, header)
        else:
            print('Not defined option.')
    return(restr_list)

def get_restr_detail(restr_id, session_id = None, hit_or_not = True): # hit_or_not이 False이면 히트 기록 없이 조회만 함.
    '''
    * 모듈명: 식당 상세 조회
    * 입력: 식당 ID, 세션 ID, 히트 여부
    * 출력(JSON): 식당 ID, 식당명, 주소, 전화번호, X 좌표, Y 좌표, 본점 거리, 별관 거리, 갱신 시간, 평균 평점, 히트 점수, 다이닝코드 페이지 URL, 썸네일 이미지 URL, 등록 리뷰(평점) 목록
        - [('R20160604010629860275', '커피소녀', '여의도 · 서울특별시 영등포구 여의도동 17', '02-780-1199', 126.9187317, 37.5256864, 0.003325272972255698, 0.003931706054635711, '20160604010629861277', 2.8000000000000003, 3, 'http://diningcode.com/profile.php?rid=F4YpWDL04ai9&rank=80', 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/55803/54313/55803_54313_77_0_8901_2014415123814913_300x200.jpg'), [('session_no_7777', 'R20160604010629860275', '20160604010630279555', 3.9, 'I do not know why people dislike here. It is of my fav place.'), ('session_no_2468', 'R20160604010629860275', '20160604010630243531', 2.5, 'So so... :d'), ('session_no_1357', 'R20160604010629860275', '20160604010630212510', 2.0, 'I must got paid by them... Terrible.')]]
    * 예외: 식당 ID가 조회 불가하면(미등록 건) None 반환
    * 설명
        - 히트 여부가 False이면 히트 처리하지 않음.
        - 히트 여부가 True이면서 세션 ID가 None이면 본 모듈의 전체 로직 자체를 수행치 않음.
        - 리뷰가 전무한 식당은 평균 평점이 -1임.
    * 미완성: 다이닝코드 등에서 실시간으로 더 취해 올 실시간 정보 입수 로직 추가 예정
    '''
    if session_id != None:
        _preproc_session_id(session_id)

    if hit_or_not and session_id == None: # 세션 ID 없이 히트 불가능함.(사용자 식별 불가하므로)
        print('Cannot update the hit score without session id.')
        return None

    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = "SELECT * FROM RESTR_BASE WHERE RID = '{0}'".format(restr_id)
        cur.execute(query)
        detail = cur.fetchone()
        if detail == None:
            print('No restaurant called {0}.'.format(restr_id))
            return None
        header = list(zip(*cur.description))[0]
        detail = _make_json_from_selection(detail, header)
        query = "SELECT * FROM USER_REVIEW WHERE RID = '{0}' ORDER BY REVIEW_TIME DESC".format(restr_id)
        cur.execute(query)
        reviewed = cur.fetchall()
        header = list(zip(*cur.description))[0]
        reviewed = _make_json_from_selection(reviewed, header)
        res = {'RESTR_DETAIL': detail, 'REVIEW_LIST': reviewed}

    if hit_or_not: # 히트 생략 여부 확인
        hit_restr(restr_id, session_id)

    ############# get dcode realtime data!!!
    #return([detail, reviewed]) # 식당 상세 정보와 동 식당에 대한 리뷰 기록들을 함께 반환함.
    return(res) # 식당 상세 정보와 동 식당에 대한 리뷰 기록들을 함께 반환함.

    #hit_restr(restr_id, session_id) ###############

def hit_restr(restr_id, session_id): # hit은 보통 식당 상세 열람 시 발동되나, 경우에 따라 임의 발동되야 할 수 있으므로 외부 제공 모듈로 정의함.
    '''
    * 모듈명: 식당 히트 처리
    * 입력: 식당 ID, 세션 ID
    * 출력(JSON): N/A
    * 설명
        - 히트는 식당 상세 조회 시 통상 자동으로 이뤄짐.(예외 처리도 가능함.)
        - 식당 상세 조회 외 경우에서 히트 처리를 할 경우는 직접 이 모듈을 호출함.(보통은 직접 호출할 일이 없을 것임.)
        - 히트 시 처리 내용
            1. 식당별 히트 점수 1 증가
            2. 사용자별 해당 식당 열람 내역 추가
            3. 직전의 열람 내역의 체류 시간 갱신(0 ~ 180초)
    '''

    if session_id != None:
        _preproc_session_id(session_id)

    MAX_STAY_SECONDS = 180 # 체류 시간은 최대 3분까지만 측정(180초)
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        # 식당 히트 증가
        query = "UPDATE RESTR_BASE SET HIT_SCORE = HIT_SCORE + 1 WHERE RID = '{0}'".format(restr_id)
        cur.execute(query)
        conn.commit()
        ts = _get_timestamp()
        # 시간 계산을 위해 시간 형식 반영
        time_formatted = '{0}-{1}-{2} {3}:{4}:{5}'.format(ts[:4], ts[4:6], ts[6:8], ts[8:10], ts[10:12], ts[12:14])
        # 사용자의 직전 열람 건의 체류 시간 갱신(MAX_STAY_SECONDS 초과 시간은 무시)
        query = '''\
            UPDATE USER_VIEW_HIST SET
                STAY_SECONDS =
                    MIN(strftime('%s', '{1}')
                    - strftime('%s', substr(VIEW_TIME, 1, 4) || '-' || substr(VIEW_TIME, 5, 2) || '-' || substr(VIEW_TIME, 7, 2) || ' ' ||
                        substr(VIEW_TIME, 9, 2) || ':' || substr(VIEW_TIME, 11, 2) || ':' || substr(VIEW_TIME, 13, 2))
                    , {2})
                WHERE SID = '{0}'
                    AND STAY_SECONDS = -1
                    AND VIEW_TIME = (SELECT MAX(VIEW_TIME) FROM USER_VIEW_HIST WHERE SID = '{0}')
            '''.format(session_id, time_formatted, MAX_STAY_SECONDS)
        #print(query)
        cur.execute(query)
        conn.commit()
        # 사용자별 열람 기록
        query = '''\
            INSERT INTO USER_VIEW_HIST VALUES
                ('{0}', '{1}', '{2}', {3})
            '''.format(session_id, restr_id, _get_timestamp(), -1) # 체류 시간은 최초 -1로 설정
        #print(query)
        cur.execute(query)
        conn.commit()

def get_user_info(session_id):
    '''
    * 모듈명: 사용자 정보 조회
    * 입력: 세션 ID
    * 출력(JSON): 세션 ID, 별명, 등록시간, 최종접속시간, 등록 리뷰(평점) 목록
        - [('session_no_1357', 'Known Jackal', '20160604010628722516', '20160604010630200502'), [('session_no_1357', 'R20160604010629860275', '20160604010630212510', 2.0, 'I must got paid by them... Terrible.'), ('session_no_1357', 'R20160604010629114778', '20160604010630180489', 4.1, 'Fabulous! Recommended!'), ('session_no_1357', 'R20160604010629474018', '20160604010630148467', 3.7, 'Not so bad.')]]
    * 예외: 세션 ID가 조회 불가하면(미등록 건) None 반환
    * 설명
        - 타 모듈은 주어진 세션 ID를 확인해 미등록 건이면 등록시킨 후 로직 처리를 함.
        - 본 모듈은 이미 등록된 사용자의 정보를 확인하기 위함임. 따라서 미등록 세션 ID라도 등록 처리하지 않음.
        - 사용자가 등록한 리뷰(평점)들을 최근 등록된 순으로 나열해 같이 반환함.
    '''

    #사용자 정보 획득 시 인자로 넘겨진 세션 ID에 대해서는 전처리를 하지 않음.
    # (있는지 조회하려 했는데 등록을 하는 경우가 발생하므로)
    '''
    if session_id != None:
        _preproc_session_id(session_id)
    '''

    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = "SELECT * FROM USER_BASE WHERE SID = '{0}'".format(session_id)
        cur.execute(query)
        user_info = cur.fetchone()
        if user_info == None:
            return None
        header = list(zip(*cur.description))[0]
        user_info = _make_json_from_selection(user_info, header)
        query = "SELECT * FROM USER_REVIEW WHERE SID = '{0}' ORDER BY REVIEW_TIME DESC".format(session_id)
        cur.execute(query)
        reviewed = cur.fetchall()
        header = list(zip(*cur.description))[0]
        reviewed = _make_json_from_selection(reviewed, header)
        res = {'USER_INFO': user_info, 'REVIEW_LIST': reviewed}
        return(res) # 사용자 정보와 동 사용자의 리뷰한 것들을 같이 반환함.

def set_user_review(session_id, restr_id, rating, review_txt):
    '''
    * 모듈명: 사용자 리뷰 등록
    * 입력: 세션 ID, 식당 ID, 평점, 리뷰 문구
    * 출력(JSON): N/A
    * 설명
        - 평점 등록과 리뷰 문구 등록은 함께 발생함.
        - 등록된 평점는 동 식당의 평균 평점을 바로 갱신시킴.
        - 따라서 리뷰 문구는 공백 입력되어도 무관하나 평점 입력 시에는 사용자 유의가 필요함.
    '''
    if session_id != None:
        _preproc_session_id(session_id)

    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = '''\
            INSERT INTO USER_REVIEW VALUES
                ('{0}', '{1}', '{2}', {3}, '{4}')
            '''.format(session_id, restr_id, _get_timestamp(), str(rating), review_txt)
        cur.execute(query)
        conn.commit()
        # 사용자 리뷰 발생 시 식당 평균 평점을 갱신함.
        query = '''\
            UPDATE RESTR_BASE SET
                AVG_RATING = (SELECT AVG(RATING) FROM USER_REVIEW WHERE RID = '{0}')
                WHERE RID = '{0}'
            '''.format(restr_id)
        cur.execute(query)
        conn.commit()

def get_session_id(nickname): # 사용자가 기억한 별명으로부터 세션 ID를 취하고 controller가 그것으로 사용자와 세션을 맺게 함.
    '''
    * 모듈명: 세션 ID 조회
    * 입력: 닉네임
    * 출력(JSON): 세션 ID
    * 예외: 닉네임으로 조회되지 않으면(미등록 건) None 반환
    * 설명
        - 사용자가 기억할 것으로 기대되는 닉네임을 바탕으로 세션 ID를 조회해 옴.
        - 사용자가 닉네임을 기반으로 여러 장치에서 서비스를 이용할 때, 기존 사용하던 동일 세션을 맺을 수 있게 해 줌.
        - 본 모듈은 닉네임 기반으로 세션 ID를 조회해 줄 뿐이며, 조회 결과를 바탕으로 세션 맺는 일은 모듈 호출자가 할 것임.
        - 닉네임은 영문 문자열이며 '형용사 동물' 임의 조합으로 생성됨.(최초 세션 ID 등록 시 정의)
            - 사례: Scary Insect, Easy-Going American Cocker Spaniel, Marvelous African Penguin
    '''
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        query = "SELECT SID FROM USER_BASE WHERE NICKNAME = '{0}'".format(nickname)
        cur.execute(query)
        sess = cur.fetchone()
        header = list(zip(*cur.description))[0]
        sess = _make_json_from_selection(sess, header)
        return(sess)

def search_restr(keyword): # class 형태로 재작성하여 overloading으로 표현할 예정
    '''
    * 모듈명: 식당 검색
    * 입력: 키워드(키워드 목록 또는 공백으로 분리된 키워드들로 이뤄진 문자열)
    * 출력(JSON): 식당 ID, 키워드 일치 빈도수, 키워드 일치 현황, ...(목록)
        - [['R20160604010628862610', 3, {('NAME', '제일제면소 여의도IFC점'), ('ADDR', 'ifc몰 · 서울시 영등포구 여의도동 23 IFC몰 L3층')}], ['R20160604010629433991', 2, {('ADDR', 'ifc몰 · 서울특별시 영등포구 여의도동 23'), ('NAME', '푸드엠파이어 IFC점')}], ['R20160604010628996699', 1, {('ADDR', 'ifc몰 · 서울특별시 영등포구 여의도동 23')}], ['R20160604010628908640', 1, {('NAME', '정인면옥')}], ['R20160604010628963677', 1, {('ADDR', 'ifc몰 · 서울시 영등포구 여의도동 23')}]]
    * 예외: 조회된 식당이 없을 때, 또는 인자로 주어진 키워드의 형식이 부적절하면, None 반환
    * 설명
        - 식당명, 주소, 전화번호를 대상으로 검색
        - 키워드가 다수일 때는 각각에 대해 검색을 수행
        - 조회 결과 목록은 일치된 검색어가 많은 것을 우선으로 정렬함.
    * 미완성
        - 식당 태그, 설명 텍스트 등에 대해서도 검색 수행
        - 사용자 리뷰 등에서도 검색할 수 있게 함.
    '''
    if type(keyword) is str:
        keyword = re.split('\s+', keyword)

    if type(keyword) is not list:
        print("Wrong keyword format. Use 'list' or blank-splittable 'str'.")
        return(None)

    res = []
    for i in keyword: # 각 키워드(단어)마다 검색을 수행
        res += _search_restr_single_word(i)
    if len(res) == 0:
        return(None)
    res_eval = set(list(zip(*res))[0]) # RID의 유니크 셋 구하기
    res_eval = dict(zip(res_eval, [[] for i in range(0, len(res_eval))])) # 딕셔너리 구성
    for i in res:
        res_eval[i[0]].append((i[1], i[2]))
    res_eval = ([[i[0], len(i[1]), set(i[1])] for i in res_eval.items()]) # RID, 검색 충족 건수(중복 제거), 실제 검색 충족부
    res_eval.sort(key = lambda x: x[1], reverse = True)
    # 출력을 위한 가공
    res_final = dict()
    for ix, i in enumerate(res_eval):
        match_info = i[2]
        match_info = _make_json_from_selection(list(match_info), ['MATCH_WHERE', 'MATCH_PART'])
        restr_info = _make_json_from_selection(i[:len(i) - 1], ['RID', 'MATCH_COUNT'])
        #res_final.append({'RESTR_INFO': restr_info, 'MATCH_INFO': match_info})
        res_final[ix + 1] = {'RESTR_INFO': restr_info, 'MATCH_INFO': match_info}
    return(res_final)

# pickle 작업용
def _deal_with_pickle():
    res = None
    with open(TESTDATA_PATH, 'rb') as fp:
        res = pickle.load(fp)
        print(res)
    '''
    with open(TESTDATA_PATH, 'wb') as fp:
        pickle.dump([res[0], res[1], _crawl('서여의도', 100)], fp)
    '''

# 디버깅용
def _exec_qurey():
    '''
    conn = sqlite3.connect(DB_FILE_PATH)
    c = conn.cursor()
    '''

    '''
    q = 'drop table restr_base'
    c.execute(q)
    conn.commit()
    '''

    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        #'''
        #query = 'SELECT * FROM NICKNAME_SRC_NOUN WHERE CNT_USED > 0'
        #query = 'SELECT * FROM NICKNAME_SRC_ADJ WHERE CNT_USED > 0'
        #query = 'SELECT * FROM RESTR_BASE'
        #query = 'SELECT * FROM RESTR_BASE LIMIT 1 OFFSET 0'
        #query = 'SELECT * FROM USER_REVIEW'
        #query = "SELECT NAME FROM SQLITE_MASTER WHERE TYPE = 'table'"
        query = "SELECT * FROM USER_BASE"
        #query = "SELECT * FROM USER_VIEW_HIST"
        cur.execute(query)
        #print(cur.fetchall())
        print('\n'.join([str(i) for i in cur.fetchall()]))
        #'''
        '''
        query = 'DELETE FROM RESTR_BASE'
        cur.execute(query)
        conn.commit()
        '''

def _print_db(result_list):
    print('\n'.join([str(i) for i in result_list]))

if __name__ == '__main__':
    _calibrate_data()
    '''
    _drop_tables()
    _gen_db_schema()
    _calibrate_data() # get_addr_coord() 호출을 내부적으로 포함
    '''
    '''
    print('▶ 사용자별 정보')
    print(get_user_info('session_no_1357'))
    print(get_user_info('session_no_2468'))
    print(get_user_info('session_no_7777'))
    '''
    '''
    temp_info = get_user_info('session_no_7777')
    restr_with_mult_reviews = temp_info[1][0][1]
    print('▶ 레스토랑 상세')
    print(get_restr_detail(restr_with_mult_reviews, 'session_no_7777'))
    '''
    '''
    print(get_restr_detail('R20160604010628835593', 'session_no_7777'))
    #get_restr_detail('R20160603221305955236', 'session_no_7777', False)
    '''
    '''
    print('▶ 레스토랑 목록')
    #get_restr_list(5, 'rating')
    #_print_db(get_restr_list(5, 'hit'))
    print(get_restr_list(5, 'closest_it'))
    '''
    '''
    print('▶ 별명으로부터 세션 ID 얻기')
    print(get_session_id('Annoyed Starfish'))
    '''
    '''
    print('▶ 검색')
    #_print_db(search_restr('웱'))
    print(search_restr('S'))
    '''
    #print(_crawl('서여의도', 5))
    #print(_gen_nickname())
    #print(_get_timestamp())
    #get_restr_list(2, 'random')
    #get_restr_detail('R20160602sablank')
    #print(_gen_nickname())
    #_deal_with_pickle()
    #_exec_qurey()
    #a = {1: {'ADDR': '여의도 · 서울시 영등포구 여의도동 16-2 1F (중소기업중앙회신관 건물 1층)', 'RID': 'R20160604010629153804', 'DIST_HQ': 0.001981652895951576, 'UPT_TIME': '20160604010629153804', 'COORD_Y': 37.5281813, 'THUMBNAIL_URL': 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/53247/58022/53247_58022_86_5_5326_201572673841549_300x200.jpg', 'HIT_SCORE': 0, 'AVG_RATING': -1.0, 'NAME': '보나베띠 여의도점', 'COORD_X': 126.9227388, 'DIST_IT': 0.0007904331217772451, 'DCODE_URL': 'http://diningcode.com/profile.php?rid=fCBYskxnOCky&rank=27', 'PHONE': '02-780-3886'}, 2: {'ADDR': '여의도 · 서울특별시 영등포구 여의도동 16-2', 'RID': 'R20160604010629558074', 'DIST_HQ': 0.001981652895951576, 'UPT_TIME': '20160604010629558074', 'COORD_Y': 37.5281813, 'THUMBNAIL_URL': 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/57189/50096/57189_50096_77_0_3036_201631802252364_300x200.jpg', 'HIT_SCORE': 0, 'AVG_RATING': -1.0, 'NAME': '달맞이 꽃게탕', 'COORD_X': 126.9227388, 'DIST_IT': 0.0007904331217772451, 'DCODE_URL': 'http://diningcode.com/profile.php?rid=F8IzY8XHgHtO&rank=58', 'PHONE': '02-3775-0118'}, 3: {'ADDR': '여의도 · 서울특별시 영등포구 여의도동 16-2', 'RID': 'R20160604010630063411', 'DIST_HQ': 0.001981652895951576, 'UPT_TIME': '20160604010630063411', 'COORD_Y': 37.5281813, 'THUMBNAIL_URL': 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/55601/58987/55601_58987_86_5_4060_201572825730907_300x200.jpg', 'HIT_SCORE': 0, 'AVG_RATING': -1.0, 'NAME': '명동할머니국수 서여의도점', 'COORD_X': 126.9227388, 'DIST_IT': 0.0007904331217772451, 'DCODE_URL': 'http://diningcode.com/profile.php?rid=2AWJjClsTJZJ&rank=96', 'PHONE': '02-3775-3779'}, 4: {'ADDR': '여의도 · 서울특별시 영등포구 여의도동 14-15', 'RID': 'R20160604010629165812', 'DIST_HQ': 0.0007042791775973079, 'UPT_TIME': '20160604010629165812', 'COORD_Y': 37.5286203, 'THUMBNAIL_URL': 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/51820/52947/51820_52947_80_0_8935_201473114438908_300x200.jpg', 'HIT_SCORE': 0, 'AVG_RATING': -1.0, 'NAME': '동해도 본점', 'COORD_X': 126.921399, 'DIST_IT': 0.0010383838404070924, 'DCODE_URL': 'http://diningcode.com/profile.php?rid=yQ699tA32IEh&rank=28', 'PHONE': '02-761-6350'}, 5: {'ADDR': '여의도 · 서울특별시 영등포구 여의도동 13-25', 'RID': 'R20160604010629369949', 'DIST_HQ': 0.0013472848882181824, 'UPT_TIME': '20160604010629369949', 'COORD_Y': 37.5290775, 'THUMBNAIL_URL': 'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/53344/51043/53344_51043_77_0_216_20158202552186_300x200.jpg', 'HIT_SCORE': 0, 'AVG_RATING': -1.0, 'NAME': '정우칼국수', 'COORD_X': 126.9218761, 'DIST_IT': 0.001282532249109619, 'DCODE_URL': 'http://diningcode.com/profile.php?rid=7rxrKLPFV3D6&rank=43', 'PHONE': '02-783-4007'}}
    #xx(a, 0)
