[![download_daily_papers](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/download_hf_daily_paper.yml/badge.svg)](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/download_hf_daily_paper.yml) [![translate_into_korean](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/translate_into_korean.yml/badge.svg)](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/translate_into_korean.yml) [![upload_to_notion](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/upload_to_notion.yml/badge.svg)](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/upload_to_notion.yml)


# Korean Daily Briefs for Hugging Face Papers 🤗
![](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/blob/main/images/hf-daily-paper-into-korean-site.png?raw=true)

이 Repository는 한국 시간을 기준으로 매일 오전 12시~1시 사이에 [Hugging Face Daily Papers](https://huggingface.co/papers)에서 소개하는 논문 정보를 수집하고, 한국어로 번역하여 [Notion](https://leejeongin.notion.site/ai-daily-briefing-in-korean)에 업로드합니다.

모든 과정은 **GitHub Action 을 통해 자동화**되므로, 유료 유지관리가 필요하지 않습니다.

# How this works?
![](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/blob/main/images/hf-daily-paper-into-korean.png?raw=true)
이 프로젝트는 GitHub Action Workflow 관점에서 세 단계로 이루어집니다!

1. [Download HF daily papers](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/download_hf_daily_paper.yml)
    - [Hugging Face Daily Papers](https://huggingface.co/papers) API Endpoint 에서 메타데이터를 다운로드 합니다. 일간지의 전체 목록이 업데이트 되는 시점이 불분명하기 때문에 목표 날짜는 "어제"입니다. 날짜는 동적으로 계산됩니니다.
    - 💥 주말에는 일간지 업데이트가 되고 있지 않아서, 한국 기준 일~월요일에는 메타데이터 다운로드 및 Notion 업로드가 되지 않습니다.
   
2. [Translate into Korean](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/translate_into_korean.yml)
    - [OpenAI API](https://openai.com/index/openai-api/)로 제공하는 LLM과 프롬프트 엔지니어링을 활용하여 문서를 번역합니다. LLM은 논문의 제목/요약을 번역 및 요약하고, 키워드를 추출합니다.
    - API 요금은 개인 자금을 사용하고 있습니다..

3. [Upload to Notion](https://github.com/jeongiin/hf-daily-paper-korean-autoflow/actions/workflows/upload_to_notion.yml)
    - 공개된 Notion 페이지에 업로드합니다. 모든 페이지는 Notion에서 제공하는 Database 형태로 관리됩니다.

* 현재는 beta version 으로 하루에 일부 논문만 작업 중이며, 요약 성능 개선 후 전체 논문을 번역하도록 변경 예정입니다.

# Welcome to Contionbute!

LLM 번역 결과가 미숙하다보니, 다른 API를 활용해서 번역하는 방법이나, 프롬프트 엔지니어링을 고도화 하는 방법 등으로 개선이 필요합니다!

이를 위한 PR은 언제든지 날려주세요 🎈


# To Do
- [X] README 작성 
- [X] `paper_openai_translation.py` 에서 목표 날짜에 번역된 json 이 이미 있으면 수행하지 않도록 예외 처리
- [ ] 요약 성능 고도화
    - [X] Prompt Engineering
    - [ ] API 교체(Claude, Solar 등)
- [X] 논문 대표 사진 다운 및 Notion Page 내 삽입 기능
- [ ] 통계 기능(ex. Weekly Keywords 등)

# Acknowledgement
- 두 분의 작업물을 참고하였습니다. 감사합니다!
- [hf-daily-paper-newsletter](https://github.com/deep-diver/hf-daily-paper-newsletter?tab=readme-ov-file)
- [hf-daily-paper-newsletter-chinese](https://github.com/2404589803/hf-daily-paper-newsletter-chinese/tree/main)


