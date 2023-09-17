from datetime import datetime
import pandas as pd
import numpy as np


# 기존 파일(khu_get_data_all_0704.csv)에는 6대지수 및 세부 역량지수 열에 결측치가 많았음
# 따라서, 각 컬럼별로 임의의 값을 가진 데이터프레임을 생성

# 함수 프로세스
# 1) 기존 데이터프레임에 난수값을 가질 '_2'컬럼 생성
#   ex) '기술인력비중평가점수' : 기존 컬럼(결측치 많음)
#       '기술인력비중평가점수_2' : 난수를 갖는 임의의 컬럼

# 2) 각 컬럼별 값 범위를 임의로 만들고, 범위 내 난수(int, float)를 부여
#   ex) '기술인력비중평가점수' 컬럼 --> 5~30 사이의 int 임의로 부여
#   ex2) '매출액증가율' 컬럼 --> -1~1 사이의 float 임의로 부여

# 3) 기존컬럼의 결측치가 있는 부분에 '_2'컬럼의 난수를 덮어씌움
#    (컬럼명은 기존 컬럼명으로 유지)

# 4) 요약문 출력의 일반화를 위해 각 컬럼 값 중 일부(5%)를 결측치로 재변환

# 5) 기업의 지수별 점수 계산
#    가중치는 1/세부역량지수개수 로 설정
#    ex) R&D역량지수의 세부역량지수는 4개 --> 각 가중치는 25%로 설정
#    세부역량지수 중 결측치가 하나라도 있으면 점수 계산X

# 6) 동종업계 평균값 업데이트
#    기업별로 지수별 점수가 변화됨 --> '동종업계분류' 컬럼의 값에 따라 동종업계별 평균값도 업데이트!





def make_test_csv(file_dir):
    df = pd.read_csv(file_dir)
    
    # 난수 부여할 컬럼들
    total_change_columns = ['기술인력비중평가점수', '전년대비R&D투자증액수준평가점수', '국가R&D실적평가점수',
                        '경영지원/전략기획인력수준평가점수', '기업종사자비율증가수준평가점수',
                        '종사자1인당매출액수준평가점수', '매출액증가추이평가점수', '고객응대서비스고도화수준평가점수',
                        '마케팅네트워크보유역량평가점수', '영업·마케팅인력비중평가점수', '선도기업대비마케팅비용비중평가점수',
                             '신용점수', 'R&D점수','BM점수', 'BM2기술성점수','BM2사업성점수',
                             '매출액증가율', '순이익증가율','긍정백분율', '중립백분율', '부정백분율']
    
    # 바꿀 값의 범위에 따라 컬럼 구분
    change_columns_5_30 = ['기술인력비중평가점수', '전년대비R&D투자증액수준평가점수', '국가R&D실적평가점수']
    change_columns_20_70 = ['경영지원/전략기획인력수준평가점수', '기업종사자비율증가수준평가점수']
    change_columns_10_50 = ['종사자1인당매출액수준평가점수', '매출액증가추이평가점수', '고객응대서비스고도화수준평가점수']
    change_columns_50_100 = ['마케팅네트워크보유역량평가점수', '영업·마케팅인력비중평가점수', '선도기업대비마케팅비용비중평가점수',
                             '신용점수', 'R&D점수', 'BM점수', 'BM2기술성점수','BM2사업성점수']
    change_columns_1 = ['매출액증가율', '순이익증가율']  # -1~1 사이 값으로 float 분배
    change_columns_0_1 = ['긍정백분율', '중립백분율', '부정백분율'] # 0~1사이 값으로 float 분배
    
    
    # 1) &  2)
    for column in change_columns_5_30:
        df[f'{column}_2'] = np.random.randint(5,31, size=(len(df),1))
        
    for column in change_columns_20_70:
        df[f'{column}_2'] = np.random.randint(20,71, size=(len(df),1))
            
    for column in change_columns_10_50:
        df[f'{column}_2'] = np.random.randint(10,51, size=(len(df),1))
            
    for column in change_columns_50_100:
        df[f'{column}_2'] = np.random.randint(50,101, size=(len(df),1))

    # 실수를 갖는 컬럼들은 소수점 첫째자리까지만 출력    
    for column in change_columns_1:
        df[f'{column}_2'] = np.round(np.random.uniform(-1,1, size=(len(df),1)), 1)
        
    for column in change_columns_0_1:
        df[f'{column}_2'] = np.round(np.random.random_sample(size=(len(df),1)), 1)
    
    # 3) 
    for column in total_change_columns:
        df[f'{column}'] = df[f'{column}'].fillna(df[f'{column}_2'])
        df = df.drop(columns= f'{column}_2')
    
    # 4) 
    for column in total_change_columns:
        df[f'{column}'] = df[f'{column}'].mask(np.random.random(len(df)) < 0.05)
    

    # 5)
    
    df['R&D역량지수'] = np.round(df['기술인력비중평가점수'] * 0.25 + df['전년대비R&D투자증액수준평가점수'] * 0.25 + df['국가R&D실적평가점수'] * 0.25 + df['4차산업혁명대응수준평가점수'] * 0.25)
    df['인적자원지수'] = np.round(df['경영지원/전략기획인력수준평가점수'] * 0.33 + df['종사자1인당매출액수준평가점수'] * 0.33 + df['기업종사자비율증가수준평가점수'] * 0.33)
    df['BM지수'] = np.round(df['고용전망평가점수'] * 0.25 + df['체감경기전망평가점수'] * 0.25 + df['매출액증가추이평가점수'] * 0.25 + df['사업화기반구축수준평가점수'] * 0.25)
    df['마케팅역량지수'] = np.round(df['고객응대서비스고도화수준평가점수'] * 0.25 + df['마케팅네트워크보유역량평가점수'] * 0.25 + df['영업·마케팅인력비중평가점수'] * 0.25 + df['선도기업대비마케팅비용비중평가점수'] * 0.25)
    df['미래성장지수'] = np.round(df['매출액증가율'] * 14.3 + df['순이익증가율'] * 14.3 + df['신용점수'] * 0.143 + df['BM점수'] * 0.143 + df['BM2기술성점수'] * 0.143 + df['BM2사업성점수'] * 0.143 + df['R&D점수'] * 0.143)
    df['평판정보지수'] = np.round(df['긍정백분율'] * 33 + df['중립백분율'] * 33 + df['부정백분율'] * 33)

    # 6) 
    column_list = ['BM지수', '마케팅역량지수', '인적자원지수', 'R&D역량지수',
                '미래성장지수', '평판정보지수', '기술인력비중평가점수', '전년대비R&D투자증액수준평가점수', '국가R&D실적평가점수',
                    '경영지원/전략기획인력수준평가점수', '기업종사자비율증가수준평가점수',
                    '종사자1인당매출액수준평가점수', '매출액증가추이평가점수', '고객응대서비스고도화수준평가점수',
                    '마케팅네트워크보유역량평가점수', '영업·마케팅인력비중평가점수', '선도기업대비마케팅비용비중평가점수',
                    '신용점수', 'R&D점수','BM점수', 'BM2기술성점수','BM2사업성점수',
                    '매출액증가율', '순이익증가율','긍정백분율', '중립백분율', '부정백분율']

    for column in column_list:
        df[f'{column}평균'] = df.groupby('동종업계분류코드')[column].transform('mean')
    
    return df


if __name__ == '__main__':
    # 작업에 사용한 기존 데이터프레임
    df = make_test_csv(file_dir='khu_get_data_all_0704.csv')
    
    # 새로 생성된, 난수를 가진 데이터프레임
    df.to_csv('test.csv',index=False, encoding='utf-8-sig')