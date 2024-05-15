import time
import requests
import pandas as pd
from io import BytesIO

current_time = time.strftime("%y%m%d")
current_time_with_dash = str(time.strftime("%Y-%m-%d"))

def download_excel() -> str:
    target_url = "https://www.bizinfo.go.kr/bbs/AS/excelDowload.do?1=1&schEndAt=N&condition=searchPblancNm&condition1=AND&rescan=N"
    
    try:
        response = requests.get(target_url)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킴
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
    filename = f"{current_time}.csv"

    # BytesIO 객체로 감싸서 read_excel에 전달
    df = pd.read_excel(BytesIO(response.content), engine='openpyxl')
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    return filename


def read_csv_file(file: str) -> pd.DataFrame:
    df = pd.read_csv(file)

    today_data = df[df['등록일자'] == current_time_with_dash]

    return today_data

def preprocessing(df: pd.DataFrame) -> pd.DataFrame:

    department_to_except = [
                            # 광역시 및 특별자치시
                            '울산광역시', '부산광역시', '대구광역시', '대전광역시', 
                            '광주광역시', '세종특별자치시', '제주특별자치도',
                            # 도
                            '전라남도', '전라북도', '전북특별자치도', 
                            '경상남도', '경상북도', 
                            '충청남도', '충청북도',
                            '강원도', '강원특별자치도'
                            ]
    # 소관 부처 칼럼에서 서울 및 정부부처만 추출
    df = df[~df['소관부처'].isin(department_to_except)]
    
    return df


def save_to_md(df: pd.DataFrame) -> None:

    md = f"# {current_time_with_dash} 일자 공고 정보\n\n"
    md += "| 소관부처 | 공고명 | 공고일자 | 마감일자 | 상세링크 |\n"
    md += "| --- | --- | --- | --- | --- |\n"
    



if __name__ == '__main__':
    while True:
        file_path = download_excel()

        if file_path:
            df = read_csv_file(file_path)
            processed_df = preprocessing(df)
    
        time.sleep(3600*24)
