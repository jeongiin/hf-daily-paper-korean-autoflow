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
                    "role": "system",  # 시스템 메시지 (모델에 역할 정의)
                    "content": """
                    당신은 AI분야의 한국인 번역 전문가입니다. 
                    번역의 정확성과 전문성을 유지하고 적절한 학술 용어를 사용해주세요.
                    기술 용어는 영문을 그대로 작성하고 다른 문장은 자연스러운 한국어 문장으로 번역해주세요.
                    """
                },
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

    metadata_file = os.path.join('Paper_metadata_download', f"{yesterday_str}.json")
    if not os.path.exists(metadata_file):
        print(f"메타데이터 파일을 찾을 수 없습니다: {metadata_file}")
        return

    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            papers_data = json.load(f)  # 논문 데이터 읽기

        papers_data = papers_data[0:2]

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
                아래 논문 제목과 요약을 번역하고, 연구의 목적, 홍보 문구, 키워드를 작성해주세요.
                번역의 정도나 느낌은 예시를 참고해주세요.
                purpose는 논문에서 해결하려는 문제가 짧고 정확하게 작성되어야 합니다.
                키워드는 "Computer Vision, Image Generation, Image Understanding,
                Video Generation, Video Understanding, Natural Language Processing,
                Large Language Models, Multimodal Learning, Vision-Language Models,
                Image Classification, Pose Estimiation, 3D Vision, Document Parsing,
                Image Segmentation, Robotics" 중 3개를 선택해주세요. 3개를 고를 수 없는 경우 적절한 키워드를 작성해주세요.
                출력은 반드시 예시와 같이 dictionary 형태로 해주세요.:
                
                제목 입력 예시: Pick-a-Pic: An Open Dataset of User Preferences for Text-to-Image Generation
                요약 입력 예시: The ability to collect a large dataset of human preferences from text-to-image users is usually limited to companies, making such datasets inaccessible to the public. To address this issue, we create a web app that enables text-to-image users to generate images and specify their preferences. Using this web app we build Pick-a-Pic, a large, open dataset of text-to-image prompts and real users' preferences over generated images. We leverage this dataset to train a CLIP-based scoring function, PickScore, which exhibits superhuman performance on the task of predicting human preferences. Then, we test PickScore's ability to perform model evaluation and observe that it correlates better with human rankings than other automatic evaluation metrics. Therefore, we recommend using PickScore for evaluating future text-to-image generation models, and using Pick-a-Pic prompts as a more relevant dataset than MS-COCO. Finally, we demonstrate how PickScore can enhance existing text-to-image models via ranking.
                출력 예시:
                {
                    "translation_title": "Pick-a-Pic: Text-to-Image 생성을 위한 사용자 선호도 공개 데이터 세트",
                    "translation_summary": "Text-to-Image 기술에서, 실제 사용자들이 어떤 이미지를 선호하는 지는 기술을 소유하고 있는 회사만 접근 할 수 있습니다. 따라서 일반인들이 활용하기 어렵다는 문제가 발생합니다. \n이 문제를 해결하기 위해 Text-to-Image 사용자가 이미지를 생성하고 선호도를 지정할 수 있는 웹 앱을 먼저 만들었습니다. 이 웹 앱을 사용해서 Text-to-Image Prompt 와 생성된 이미지에 대한 사용자 선호도를 수집해 공개 데이터 세트 Pick-a-Pic 을 제작했습니다. \n이 데이터 세트를 활용하여 CLIP를 기반으로 점수를 계산하는 함수 PickScore를 학습했습니다. 이 함수는 인간 선호도 예측을 아주 잘합니다. PickScore 의 모델 평가 수행 능력을 테스트 하였을 때도 다른 지표들보다 인간이 직접 매긴 순위와 더 많은 상관관계가 있었습니다. 따라서 앞으로의 Text-to-Image 생성 모델을 평가할 때 PickScore가 할 것을 추천합니다. \n마지막으로, 우리는 PickScore 로 계산한 순위로 기존 Text-to-Image 모델을 어떻게 향상시킬 수 있는지 보여줍니다.",
                    "purpose": "Text-to-Image 성능 평가 시 인간 선호와 유사한 수치로 계산하기 위한 공개 데이터 및 Scoring 함수 연구",
                    "advertising_copy": "기존의 Text-to-Image 평가 방법을 더욱 사용자 선호도와 일치하게 개선하고 싶었던 분들에게 추천합니다!",
                    "keywords":["Computer Vision","Image Generation","Text-to-Image"]
                }
                
                
                제목: %s
                요약: %s
                출력:
                """ %(title, summary)
                
                
                response = call_gpt_api(prompt)
                print(response)

                # GPT 응답 데이터 안전하게 JSON 파싱
                translation_content = response.choices[0].message.content
                translation_data = json.loads(translation_content)
                
                parsed_result = {
                    "paper": paper_info,
                    "translation_title": translation_data.get("translation_title", ""),
                    "translation_summary": translation_data.get("translation_summary", ""),
                    "purpose": translation_data.get("purpose", ""),
                    "advertising_copy": translation_data.get("advertising_copy", ""),
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
