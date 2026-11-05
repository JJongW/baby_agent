# 오늘의 타로

하루에 한 장 타로 카드를 뽑아 운세를 보고, 그 운을 지키는 미션 하나를 해내는 웹 서비스. 기획은 [PRD.md](PRD.md).
baby_agent 에이전트로 점검하며 만들었다. 점검 결과는 [reviews/](reviews/).

## 파일
| 파일 | 하는 일 |
| --- | --- |
| `prototype.html` | 화면 전부 (입장, 섞기, 등장, 공개, 지킴). 화면은 이 파일만 고친다 |
| `app.py` | Streamlit에서 `prototype.html`을 띄운다. 이미지와 폰트를 HTML 안에 넣어 준다 |
| `assets/web/` | 화면에 쓰는 그림 (WebP). 원본 PNG는 레포에 올리지 않는다 |
| `fonts/` | 머니그라피 Rounded(한국어), Avigea(영어) |
| `design-options.html` | 디자인 시안 6가지와 화면 흐름 |

## 내 컴퓨터에서 보기
```bash
pip install -r members/shin/tarot/requirements.txt
streamlit run members/shin/tarot/app.py
```

## Streamlit Community Cloud에 배포
1. https://share.streamlit.io 에 GitHub 계정으로 로그인한다. 비공개 레포라 레포 접근 권한을 허락해야 한다
2. **Create app** → **Deploy a public app from GitHub**
3. Repository `JJongW/baby_agent`, Branch `main`, Main file path `members/shin/tarot/app.py`
4. App URL을 정하고 **Deploy**. `requirements.txt`는 `app.py` 옆에 있어서 자동으로 읽힌다
5. API 키가 필요 없어 Secrets 설정은 없다

## 폰트 사용 범위
- 머니그라피: 토스가 무료로 배포한 폰트
- Avigea: 공개 배포 전에 라이선스(웹 사용 허용 여부)를 확인해야 한다
