import unittest
import requests
from datetime import datetime, timedelta, timezone
import json
import os

class TestDailyPapers(unittest.TestCase):
    """
    TestDailyPapers 클래스:
    - 전날의 연구 논문 데이터를 가져오는 API의 응답을 테스트하고, 
    - 결과를 JSON 파일로 저장하는 테스트 케이스를 구현합니다.
    """

    def setUp(self):
        """
        setUp 메서드:
        - 테스트 케이스 실행 전에 초기 설정을 수행합니다.
        - 현재 UTC 시간과 서울 시간(UTC+9)을 계산하고, 전날 날짜를 구합니다.
        - API URL을 생성합니다.
        """
        # 현재 UTC 시간 가져오기
        self.current_date = datetime.now(timezone.utc)
        print(f"현재 UTC 날짜와 시간: {self.current_date}")

        # UTC+9 시간대 설정 (서울 시간)
        seoul_timezone = timezone(timedelta(hours=9))
        self.current_date_seoul = self.current_date.astimezone(seoul_timezone)
        print(f"현재 서울 날짜와 시간: {self.current_date_seoul}")

        # 조회할 날짜 설정 (전날 날짜)
        self.query_date = (self.current_date_seoul - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"조회 날짜: {self.query_date}")

        # API URL 생성
        self.url = f"https://huggingface.co/api/daily_papers?date={self.query_date}"
        print(f"API URL: {self.url}")

    def test_get_daily_papers(self):
        """
        test_get_daily_papers 메서드:
        - API에 GET 요청을 보내고, 응답 데이터를 처리합니다.
        - 응답 상태에 따라 JSON 파일을 생성하고 저장합니다.
        """
        # API에 GET 요청을 보냄
        response = requests.get(self.url)

        # 결과를 저장할 폴더와 파일명 설정
        folder_name = 'paper_metadata_download'
        file_name = f"{self.query_date}.json"

        # 폴더 생성 (이미 존재하면 생략)
        os.makedirs(folder_name, exist_ok=True)

        # 저장할 파일 경로 설정
        file_path = os.path.join(folder_name, file_name)

        try:
            if response.status_code == 200:  # 응답 상태가 200인 경우 (요청 성공)
                # JSON 응답 데이터 가져오기
                data = response.json()
                if data:  # 데이터가 비어있지 않은 경우
                    print(f"{self.query_date}에 데이터를 찾았습니다:")
                    print(data)

                    # 데이터를 JSON 파일로 저장
                    with open(file_path, 'w', encoding='utf-8') as f:
                        papers_str = [str(paper) for paper in data]  # paper 객체를 문자열로 변환
                        json.dump(papers_str, f, ensure_ascii=False, indent=4)
                    print(f"데이터가 파일에 저장되었습니다: {file_path}")
                else:
                    print(f"{self.query_date}에 데이터를 찾지 못했습니다.")
                    # 데이터가 없는 경우 1을 JSON 파일에 저장
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(1, f)
                    print(f"1이 파일에 저장되었습니다: {file_path}")
            else:
                # 요청 실패 시 상태 코드와 오류 메시지 출력
                print(f"요청 실패, 상태 코드: {response.status_code}")
                print(response.json())  # 오류 세부 정보 출력
                # 실패한 경우에도 1을 JSON 파일에 저장
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(1, f)
                print(f"1이 파일에 저장되었습니다: {file_path}")
                
        except Exception as e:
            # 예외 발생 시 오류 메시지 출력 및 테스트 실패 처리
            print(f"파일 저장 중 오류 발생: {e}")
            self.fail(f"파일 저장 중 오류 발생: {e}")

if __name__ == '__main__':
    # 테스트 케이스 실행
    unittest.main(exit=False)
