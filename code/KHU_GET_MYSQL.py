# 공통으로 사용하는 함수 모음
import datetime
import operator
import re
from elasticsearch import Elasticsearch
import mysql.connector
import pandas as pd

# 엘라스틱서치 접속정보
es_host = "61.78.63.51"
es_port = 9200
es_http_auth = ('fncsp', 'fncsp!!')
es_timeout = 36000
es_max_retries = 3
es_retry_on_timeout = True

# mysql 접속정보
my_host = "61.78.63.52"
my_user = "nia"
my_passwd = "nia123!!"
my_database = "nia"
my_connect_timeout = 36000

STDAD_DATE = datetime.datetime.today().strftime("%Y%m")

es = Elasticsearch(
    host=es_host,
    port=es_port,
    http_auth=es_http_auth,
    timeout=es_timeout,
    max_retries=es_max_retries,
    retry_on_timeout=es_retry_on_timeout
)

# CSV로 저장 + DataFrame으로 반환
def khu_get_data_all():
    df = None
    try:
        conn = mysql.connector.connect(
            host=my_host,
            user=my_user,
            passwd=my_passwd,
            database=my_database,
            connect_timeout=my_connect_timeout
        )
        cur = conn.cursor(prepared=True)
        sql = "SELECT DISTINCT(BIZ_NO) FROM KHU_CMP_SC ORDER BY BIZ_NO"
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        conn.close()
        for idx, biz in enumerate(res):
            print("{}/{}".format(idx+1, len(res)))
            biz_no = str(biz[0])
            tmp = khu_get_data(biz_no=biz_no)
            if tmp is not None:
                if df is None:
                    df = tmp
                else:
                    df = pd.concat([df, tmp], ignore_index=True)
            # print(df)
        # print(df)
        make_csv(file_dir="khu_get_data_all.csv", dataFrame=df)
    except Exception as e:
        print("khu_get_data_all - error log: {}".format(e))
    return df

# DataFrame으로 반환
def khu_get_data(biz_no):
    try:
        ColName = []
        Data = []
        cmp = get_khu_cmp_sc(biz_no=biz_no)
        if cmp is not None:

            ColName += ["사업자번호", "기업명", "기업규모", "산업명", "설립일", "설립연도", "대표자명", "종업원수기준일", "직원수"]
            tmp = [None] * 9
            info = get_nicednb_enterprise(biz_no)
            if info is not None:
                data = info["_source"]["Data"]
                try:
                    estbDate = data["estbDate"]
                    estbYear = None
                    if estbDate is not None:
                        estbYear = estbDate[:4]
                    tmp = [biz_no, data["cmpNm"], data["cmpSclNm"], data["indNm"], estbDate, estbYear, data["ceoNm"],
                           data["empAccYm"], data["empCnt"]]
                    tmp = [str(i) if i is not None else None for i in tmp]
                except Exception as e:
                    print(e)
            Data += tmp

            ColName += [
                "기업산업분류코드", "동종업계분류코드",
                "신용지수역량점수", "IP지수", "BM지수", "평판정보지수", "마케팅역량지수", "인적자원지수", "R&D역량지수", "미래성장지수",
                "기술인력비중평가점수", "전년대비R&D투자증액수준평가점수", "국가R&D실적평가점수", "4차산업혁명대응수준평가점수",
                "경영지원/전략기획인력수준평가점수", "종사자1인당매출액수준평가점수", "기업종사자비율증가수준평가점수",
                "고용전망평가점수", "체감경기전망평가점수", "매출액증가추이평가점수", "사업화기반구축수준평가점수",
                "고객응대서비스고도화수준평가점수", "마케팅네트워크보유역량평가점수", "영업·마케팅인력비중평가점수", "선도기업대비마케팅비용비중평가점수",
                "매출액증가율", "순이익증가율", "신용점수", "R&D점수", "BM점수", "BM2기술성점수", "BM2사업성점수",
                "긍정백분율", "중립백분율", "부정백분율", "상위5개의긍정키워드", "상위5개의부정키워드"
            ]
            cmp = [str(i) if i is not None else None for i in list(cmp)[2:]]
            Data += cmp

            indust_code_2 = cmp[1]
            avg = get_khu_avg_sc(indust_code_2=indust_code_2)
            if avg is not None:
                tmpName = [
                    "신용지수역량점수", "IP지수", "BM지수", "평판정보지수", "마케팅역량지수", "인적자원지수", "R&D역량지수", "미래성장지수",
                    "기술인력비중평가점수", "전년대비R&D투자증액수준평가점수", "국가R&D실적평가점수", "4차산업혁명대응수준평가점수",
                    "경영지원/전략기획인력수준평가점수", "종사자1인당매출액수준평가점수", "기업종사자비율증가수준평가점수",
                    "고용전망평가점수", "체감경기전망평가점수", "매출액증가추이평가점수", "사업화기반구축수준평가점수",
                    "고객응대서비스고도화수준평가점수", "마케팅네트워크보유역량평가점수", "영업·마케팅인력비중평가점수", "선도기업대비마케팅비용비중평가점수",
                    "매출액증가율", "순이익증가율", "신용점수", "R&D점수", "BM점수", "BM2기술성점수", "BM2사업성점수",
                    "긍정백분율", "중립백분율", "부정백분율"
                ]
                tmpName = [i+"평균" for i in tmpName]
                ColName += tmpName
                Data += [str(i) if i is not None else None for i in list(avg)[2:]]

                # print(len(ColName), ColName)
                # print(len(Data), Data)
                df = pd.DataFrame([Data], columns=ColName)
                # print(df)
                # make_csv(file_dir="khu_get_data.csv", dataFrame=df)
                return df
    except Exception as e:
        print(e)
    return None


# 기업개요데이터 가져오기
def get_nicednb_enterprise(biz_no):
    result = None
    try:
        query = {
          "sort": [{"SearchDate": {"order": "desc"}}],
          "query": {"bool": {"must": [
              {"match": {"BusinessNum": biz_no}},
              {"match": {"DataType": "nicednb_enterprise"}}
          ]}}}
        res = es.search(index="source_data", body=query, size=1)
        if res["hits"]["total"]["value"] > 0:
            result = res["hits"]["hits"][0]
    except Exception as e:
        print(e)
    return result
# 기업 역량평가점수 가져오기
def get_khu_cmp_sc(biz_no):
    res = None
    try:
        conn = mysql.connector.connect(
            host=my_host,
            user=my_user,
            passwd=my_passwd,
            database=my_database,
            connect_timeout=my_connect_timeout
        )
        cur = conn.cursor(prepared=True)
        sql = "SELECT * FROM KHU_CMP_SC WHERE BIZ_NO=" + str(biz_no) + " ORDER BY STDAD_DATE DESC"
        cur.execute(sql)
        res = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print("get_khu_cmp_sc - error log: {}".format(e))
    return res
# 동종업계 역량평가점수 가져오기
def get_khu_avg_sc(indust_code_2):
    res = None
    try:
        conn = mysql.connector.connect(
            host=my_host,
            user=my_user,
            passwd=my_passwd,
            database=my_database,
            connect_timeout=my_connect_timeout
        )
        cur = conn.cursor(prepared=True)
        sql = "SELECT * FROM KHU_AVG_SC WHERE INDUST_CODE_2='" + indust_code_2 + "' ORDER BY STDAD_DATE DESC"
        cur.execute(sql)
        res = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        print("get_khu_avg_sc - error log: {}".format(e))
    return res
# csv 파일 만들기
def make_csv(file_dir, dataFrame):
    dataFrame.to_csv(file_dir, encoding='utf-8-sig')


if __name__ == "__main__":
    data = khu_get_data(biz_no=1011652006)
    
    data2 = khu_get_data_all()
    
    # 엘라스틱서치 커넥션 종료
    es.close()