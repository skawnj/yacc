import sqlite3
#import random
from yacc import *

# DB
def create_tables():
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        # RESTR_BASE
        query = '''\
            CREATE TABLE RESTR_BASE
                (RID TEXT PRIMARY KEY, NAME TEXT, ADDR TEXT, PHONE TEXT, COORD_X REAL, COORD_Y REAL
                , DIST_HQ REAL, DIST_IT REAL, UPT_TIME TEXT, AVG_RATING REAL, HIT_SCORE INTEGER
                , DCODE_URL TEXT, THUMBNAIL_URL TEXT, BID TEXT, FLOOR INTEGER, TAG TEXT
                , FOREIGN KEY(BID) REFERENCES BLDG_BASE(BID))
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
        # USER_VIEW_HIST
        query = '''\
            CREATE TABLE USER_VIEW_HIST
                (SID TEXT, RID TEXT, VIEW_TIME TEXT, STAY_SECONDS INTEGER
                , PRIMARY KEY(SID, RID, VIEW_TIME)
                , FOREIGN KEY(SID) REFERENCES USER_BASE(SID)
                , FOREIGN KEY(RID) REFERENCES RESTR_BASE(RID))
            '''
        cur.execute(query)

        # BLDG_BASE
        query = '''\
            CREATE TABLE BLDG_BASE
                (BID TEXT PRIMARY KEY, NAME TEXT, ADDR TEXT, COORD_X REAL, COORD_Y REAL)
            '''
        cur.execute(query)
        # RESTR_CRAWL
        query = '''\
            CREATE TABLE RESTR_CRAWL
                (NAME TEXT, PHONE TEXT, ADDR TEXT, COORD_X REAL, COORD_Y REAL
                , DIST_HQ REAL, DIST_IT REAL, UPT_TIME TEXT
                , DCODE_URL TEXT, THUMBNAIL_URL TEXT
                , RID TEXT
                , PRIMARY KEY(NAME, ADDR)
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
        conn.commit()

def drop_tables():
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

def populate():
    # 테이블 비우기(테이블 제거는 아님)
    with sqlite3.connect(r'yacc5.db') as conn:
        cur = conn.cursor()
        tab_list = ('BLDG_BASE', 'RESTR_BASE', 'USER_BASE', 'USER_REVIEW', 'RESTR_CRAWL')
        for i in tab_list:
            query = 'DELETE FROM {0}'.format(i)
            cur.execute(query)
            conn.commit()

    # 빌딩 생성
    set_bldg('BLDG0001', '갑 빌딩', '영등포', 130, 123)
    set_bldg('BLDG0002', '을 빌딩', '구로', 131, 124)
    set_bldg('BLDG0003', '병 빌딩', '양천', 132, 125)
    set_bldg('BLDG0004', '정 빌딩', '동작', 133, 126)
    set_bldg('BLDG0005', '무 빌딩', '송파', 134, 127)

    # 식당 생성
    with sqlite3.connect(r'yacc5.db') as conn:
        cur = conn.cursor()
        query = '''\
            INSERT INTO RESTR_BASE (RID, NAME, ADDR, PHONE, COORD_X, COORD_Y, DIST_HQ, DIST_IT, UPT_TIME, AVG_RATING, HIT_SCORE, DCODE_URL, THUMBNAIL_URL, BID, FLOOR, TAG)
                SELECT RID, NAME, ADDR, PHONE, COORD_X, COORD_Y, DIST_HQ, DIST_IT, UPT_TIME, AVG_RATING, HIT_SCORE, DCODE_URL, THUMBNAIL_URL
                , 'BLDG000' || (ABS(RANDOM() % 5) + 1)
                , ABS(RANDOM() % 10), '' FROM RESTR_BASE_BAK
            '''
        cur.execute(query)
        conn.commit()
    #set_restr('zztest', 'sikdang', '9999123', 'X bldg', 21)

    # 식당 크롤링 자료 생성
    with sqlite3.connect(r'yacc5.db') as conn:
        cur = conn.cursor()
        query = '''\
            INSERT INTO RESTR_CRAWL (NAME, PHONE, ADDR, COORD_X, COORD_Y, DIST_HQ, DIST_IT, UPT_TIME, DCODE_URL, THUMBNAIL_URL, RID)
                SELECT NAME, PHONE, ADDR, COORD_X, COORD_Y, DIST_HQ, DIST_IT, UPT_TIME, DCODE_URL, THUMBNAIL_URL, '' FROM RESTR_BASE_BAK
            '''
        cur.execute(query)
        conn.commit()

    # 사용자 생성
    set_user_info('session_no_1357')
    set_user_info('session_no_2468')
    set_user_info('session_no_7777')

    # 사용자 리뷰 생성
    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        random_restr = cur.execute('SELECT * FROM RESTR_BASE ORDER BY RANDOM() LIMIT 1').fetchone()
        set_user_review('session_no_1357', random_restr[0], 3.7, 'Not so bad.')
        random_restr = cur.execute('SELECT * FROM RESTR_BASE ORDER BY RANDOM() LIMIT 1').fetchone()
        set_user_review('session_no_1357', random_restr[0], 4.1, 'Fabulous! Recommended!')
        random_restr = cur.execute('SELECT * FROM RESTR_BASE ORDER BY RANDOM() LIMIT 1').fetchone()
        set_user_review('session_no_1357', random_restr[0], 2.0, 'I must got paid by them... Terrible.')
        set_user_review('session_no_2468', random_restr[0], 2.5, 'So so... :d')
        set_user_review('session_no_7777', random_restr[0], 3.9, "I do not know why people dislike here. It is of my fav place.")

def test():
    pass

if __name__ == '__main__':
    populate()
    #test()