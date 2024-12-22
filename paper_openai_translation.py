# -- coding: utf-8 --

import os
import json
import datetime
import pytz
from tqdm import tqdm
from openai import OpenAI
import re
import time
from tenacity import retry, stop_after_attempt, wait_exponential



# OpenAI API 키를 환경 변수에서 가져오기
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수를 설정해주세요")


# OpenAI API 호출 함수 (재시도 메커니즘 포함)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_gpt_api(prompt):
    
    # OpenAI 클라이언트를 초기화
    client = OpenAI(api_key=api_key)
    
    """
    OpenAI GPT API를 호출하여 번역 요청을 처리하는 함수
    재시도 로직이 포함되어 API 호출이 실패하면 최대 3번 재시도함
    """
    try:
        result = client.chat.completions.create(
            model="gpt-4o-mini",  # 사용 모델 지정
            messages=[
                {
                    "role": "user",  # 사용자 입력 메시지
                    "content": prompt
                }
            ],
            stream=False  # 스트리밍 비활성화
        )
        return result
    except Exception as e:
        print(f"API 호출 중 오류 발생: {str(e)}")
        raise


def process_papers():
    """
    논문 메타데이터 파일을 읽고 번역 후 결과를 저장하고 포스터를 생성하는 함수
    """
    # 어제 날짜 문자열 생성
    yesterday = datetime.datetime.now(pytz.timezone("Asia/Seoul")) - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    metadata_file = os.path.join('paper_metadata_download', f"{yesterday_str}.json")
    if not os.path.exists(metadata_file):
        print(f"메타데이터 파일을 찾을 수 없습니다: {metadata_file}")
        return

    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            papers_data = json.load(f)  # 논문 데이터 읽기

        papers_data = papers_data[0:2] # 2개의 논문에 대해서만 처리

        results = []
        # tqdm을 사용해 진행률 표시
        for paper_str in tqdm(papers_data, desc="논문 처리 중"):
            try:
                paper_data = eval(paper_str)  # 논문 데이터 파싱
                paper_info = paper_data.get("paper", {})

                if not paper_info:
                    continue

                title = paper_info.get("title", "")
                summary = paper_info.get("summary", "")

                # OpenAI GPT API에 번역 요청
                prompt = """
                이 논문의 영문 제목과 요약을 자연스러운 한국어로 요약해. 
                문장은 최대한 쉬운 표현으로 간결하게 번역하고, 기술 용어나 AI와 관련 있는 용어는 영어 단어를 그대로 작성해.
                키워드는 "Computer Vision, Image Generation, Image Understanding,
                Video Generation, Video Understanding, Natural Language Processing,
                Large Language Models, Multimodal Learning, Vision-Language Models,
                Image Classification, Pose Estimiation, 3D Vision, Document Parsing,
                Image Segmentation, Robotics" 중 3개를 선택해. 3개를 고를 수 없는 경우 적절한 키워드를 작성해.:
                
                출력 형식 : 
                {"translation_title":논문의 제목을 번역하여 작성",
                "purpose":논문에서 개선하거나 달성하려는 목표를 한국어로 작성,
                "method":논문에서 목적을 이루기 위해 실행한 방법을 작성하되, 요약에서 근거를 찾아 괄호로 작성,
                "conclusion":논문의 방법을 통해 최종적으로 달성한 성과나 결론을 작성,
                "keywods":논문과 관련이 있는 키워드 3가지를 작성}

                입력 제목 예시 : Pick-a-Pic: An Open Dataset of User Preferences for Text-to-Image Generation
                입력 요약 예시 : The ability to collect a large dataset of human preferences from text-to-image users is usually limited to companies, making such datasets inaccessible to the public. To address this issue, we create a web app that enables text-to-image users to generate images and specify their preferences. Using this web app we build Pick-a-Pic, a large, open dataset of text-to-image prompts and real users' preferences over generated images. We leverage this dataset to train a CLIP-based scoring function, PickScore, which exhibits superhuman performance on the task of predicting human preferences. Then, we test PickScore's ability to perform model evaluation and observe that it correlates better with human rankings than other automatic evaluation metrics. Therefore, we recommend using PickScore for evaluating future text-to-image generation models, and using Pick-a-Pic prompts as a more relevant dataset than MS-COCO. Finally, we demonstrate how PickScore can enhance existing text-to-image models via ranking.
                출력 예시:
                {"translation_title": "Pick-a-Pic: Text-to-Image 생성을 위한 사용자 선호도 공개 데이터 세트",
                "purpose": "Text-to-Image 성능 평가 시 인간 선호와 유사한 수치로 계산하기 위한 공개 데이터 및 Scoring 함수 연구",
                "method":["웹 애플리케이션을 만들어 text-to-image 사용자들이 이미지를 생성하고 선호도를 기록하도록 함(To address this issue, we create a web app that enables text-to-image users to generate images and specify their preferences.)", "사용자 데이터를 기반으로 Pick-a-Pic 이라는 대규모 공개 데이터세트를 생성함(Using this web app we build Pick-a-Pic, a large, open dataset of text-to-image prompts and real users' preferences over generated images.)", "Pick-a-Pic 데이터를 활용해 CLIP 기반 평가 함수인 PickScore를 학습시키고, 인간 선호 예측에서 뛰어난 성능을 확인함.(We leverage this dataset to train a CLIP-based scoring function, PickScore, which exhibits superhuman performance on the task of predicting human preferences.)","PickScore를 사용해 모델 평가를 수행하고, 기존 자동 평가 지표보다 인간 랭킹과 더 잘 일치하는 결과를 관찰함.(Then, we test PickScore's ability to perform model evaluation and observe that it correlates better with human rankings than other automatic evaluation metrics.)",
                "conclusion":"PickScore는 text-to-image 모델 평가와 향상에 효과적이며, MS-COCO보다 Pick-a-Pic 데이터셋을 사용하는 것이 더 적합함."
                "keywords":["Computer Vision","Image Generation","Text-to-Image"]}
                
                제목: %s
                요약: %s
                출력:
                """ %(title, summary)
                
                
                response = call_gpt_api(prompt)
                print(response)

                # GPT 응답 데이터 안전하게 JSON 파싱
                translation_content = response.choices[0].message.content
                translation_data = json.loads(translation_content)
                print(translation_data)
                
                parsed_result = {
                    "paper": paper_info,
                    "translation_title": translation_data.get("translation_title", ""),
                    "purpose": translation_data.get("purpose", ""),
                    "method": translation_data.get("method", []),
                    "conclusion": translation_data.get("conclusion",""),
                    "keywords": translation_data.get("keywords", [])
                }
                
                # 번역 결과 저장
                results.append(parsed_result)
                
                # None 값 체크
                if any(value is None for value in parsed_result.values()):
                    raise ValueError("응답 데이터에 None 값이 포함되어 있습니다.")

                time.sleep(1)  # 요청 간 딜레이 추가

            except Exception as e:
                print(f"논문 처리 중 오류 발생: {str(e)}")
                continue

        # 결과 저장
        output_folder = 'hf-daily-paper-ko-gpt'
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{yesterday_str}_paper_ko.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"번역 결과가 저장되었습니다: {output_file}")


    except Exception as e:
        print(f"논문 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    process_papers()
