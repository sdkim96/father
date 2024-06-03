import time
import requests
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta

# Set the date to the previous day
PREVIOUS_DAY = (datetime.now() - timedelta(days=1)).date()

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
    
    filename = f"{PREVIOUS_DAY}.csv"

    # BytesIO 객체로 감싸서 read_excel에 전달
    df = pd.read_excel(BytesIO(response.content), engine='openpyxl')
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    return filename


def read_csv_file(file: str) -> pd.DataFrame:
    df = pd.read_csv(file)

    df['등록일자'] = pd.to_datetime(df['등록일자']).dt.date

    previous_day_data = df[df['등록일자'] == PREVIOUS_DAY]
    
    return previous_day_data


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
    preprocessed_previous_day_data = df[~df['소관부처'].isin(department_to_except)]

    print(preprocessed_previous_day_data.head(2))

    return preprocessed_previous_day_data


def save_to_md(df: pd.DataFrame) -> None:
    md = f"# {PREVIOUS_DAY} 일자 공고 정보\n\n"
    md += "| 소관부처 | 공고명 | 공고일자 | 마감일자 | 상세링크 |\n"
    md += "| --- | --- | --- | --- | --- |\n"
    
    # DataFrame 데이터를 md 문자열에 추가
    for index, row in df.iterrows():
        md += f"| {row['소관부처']} | {row['지원분야']} | {row['공고명']} | {row['등록일자']} | {row['공고상세URL']} |\n"

    # 마크다운 파일로 저장
    with open(f"{PREVIOUS_DAY}.md", "w", encoding="utf-8") as file:
        file.write(md)


if __name__ == '__main__':
    while True:

        file_name = f"{PREVIOUS_DAY}.csv"

        try:
            with open(file_name, "r") as file:
                file = file.read().strip()
        except FileNotFoundError:
            file = download_excel()

        if file_name:
            previous_day_data = read_csv_file(file_name)
            processed_previous_day_data = preprocessing(previous_day_data)
            save_to_md(processed_previous_day_data)
        
        time.sleep(3600 * 24)
