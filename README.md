# Korea Micro Trend Dashboard

> **GitHub와 Streamlit 사이트에서 정확히 무엇을 눌러야 하는지 필요하다면 먼저 [DEPLOY_CLICK_GUIDE_KO.md](DEPLOY_CLICK_GUIDE_KO.md)를 여세요.** 계정 생성부터 `Create app`, Repository/Branch/File path, Secrets, Deploy 버튼까지 화면 순서대로 설명합니다.

한국에서 지금 관심이 커지는 작은 신호를 10~30분 단위로 살펴보는 Streamlit 전광판입니다. 첫 버전(MVP, **가장 작지만 실제로 쓸 수 있는 버전**)은 버튼으로 직접 갱신하며, Google Trends 공개 RSS와 Google News 공개 RSS를 사용합니다. YouTube API 키가 없으면 샘플 데이터로 대체됩니다.

> 이 프로젝트는 로그인 우회나 웹 화면 무단 크롤링을 하지 않습니다. 공개 RSS와 공식 API만 사용합니다.

## 1. 전체 개발 방향

데이터는 다음 순서로 흐릅니다.

`공개 RSS/공식 API 수집 → 중복 키워드 병합 → 점수 계산 → CSV 저장 → 카드·차트 표시`

- 지금: 수동 갱신 + CSV + 규칙 기반 요약
- 다음: 10~30분 자동 갱신 + 네이버 데이터랩 연동
- 운영 단계: Supabase(인터넷 DB) + AI 요약 + 별도 수집 스케줄러

점수는 0~100점입니다. 최신성, 여러 출처 동시 등장, 관련 링크, 반복 발견에 가점을 주고 오래된 항목과 일반어/스팸 후보에는 감점을 줍니다. 상세 화면에서 계산 근거를 확인할 수 있습니다.

## 2. 폴더 구조

```text
trend-dashboard/
├─ app.py                         # Streamlit 메인 화면과 수동 갱신
├─ requirements.txt               # 설치할 Python 패키지 목록
├─ README.md                      # 지금 읽고 있는 사용 설명서
├─ DEPLOY_CLICK_GUIDE_KO.md       # 사이트 화면에서 누를 버튼을 순서대로 설명
├─ .gitignore                     # GitHub에 올리지 않을 파일 목록
├─ .env.example                   # API 키 입력 형식 예시
├─ .streamlit/config.toml         # 어두운 전광판 기본 테마
├─ data/
│  ├─ .gitkeep
│  ├─ trends.csv                  # 실행 중 생성되는 현재 목록(Git 제외)
│  └─ history.csv                 # 시간 차트 기록(Git 제외)
├─ sample_data/
│  └─ sample_trends.csv           # API 없이 보여 주는 TOP 20 샘플
├─ utils/
│  ├─ fetch_google_trends.py      # Google Trends 공개 RSS
│  ├─ fetch_news.py               # Google News 공개 RSS
│  ├─ fetch_youtube.py            # YouTube 공식 API + 샘플 대체
│  ├─ fetch_naver_datalab.py      # 향후 네이버 연동 함수 자리
│  ├─ scoring.py                  # 중복 병합·점수·상태
│  ├─ storage.py                  # CSV 읽기·쓰기(Supabase 교체 지점)
│  └─ summarizer.py               # API 없는 규칙 기반 한 줄 요약
└─ components/
   ├─ cards.py                    # 순위 카드
   ├─ charts.py                   # Plotly 차트
   └─ filters.py                  # 사이드바 필터
```

## 3. 각 파일에서 하는 일

- `app.py`: 화면 조립, 버튼 클릭, 데이터 수집 흐름, 상세 정보 표시
- `utils/fetch_*.py`: 데이터원별 수집. 실패하면 빈 결과와 상태 메시지를 반환해 앱이 죽지 않음
- `utils/scoring.py`: 같은 키워드를 하나로 합치고 `신규/상승/관찰/하락` 상태 결정
- `utils/storage.py`: UTF-8 CSV 저장. DB를 바꿀 때 이 파일 중심으로 교체
- `components/*.py`: 화면을 기능별로 분리해 수정하기 쉽게 만듦
- `sample_data/sample_trends.csv`: 인터넷이나 API 키가 없어도 첫 화면을 보장

## 4. 내 컴퓨터에서 실행하기

### 4-1. Python 설치

Python이 없다면 설치가 필요합니다. **Python 3.11을 권장**합니다. Python 공식 사이트에서 설치할 때 Windows 사용자는 `Add Python to PATH`를 반드시 체크하세요. PATH는 터미널이 Python 프로그램의 위치를 찾는 목록입니다.

PowerShell(Windows의 명령 입력 창)을 열고 확인합니다.

```powershell
python --version
```

`Python 3.11.x`처럼 나오면 준비된 것입니다. `python`을 찾지 못하면 터미널을 닫았다 다시 열거나 Python을 재설치하세요. Windows에서는 `py --version`도 시도할 수 있습니다.

### 4-2. 가상환경 만들기

가상환경은 **이 프로젝트만 쓰는 별도 Python 상자**입니다. 다른 프로젝트와 패키지 버전이 섞이는 일을 막습니다.

프로젝트 폴더에서 아래 명령을 한 줄씩 실행합니다.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

실행 정책 오류가 나면 현재 창에서만 허용한 뒤 다시 활성화합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

성공하면 터미널 줄 앞에 `(.venv)`가 표시됩니다.

### 4-3. 패키지 설치와 실행

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

브라우저가 자동으로 열립니다. 열리지 않으면 [http://localhost:8501](http://localhost:8501)에 접속하세요. 종료는 터미널에서 `Ctrl+C`입니다.

API 키 없이도 샘플 TOP 20이 보입니다. `지금 수동 갱신`을 누르면 공개 RSS를 시도하고, YouTube는 키가 없을 경우 샘플 행을 사용합니다.

## 5. GitHub에 올리기

### 5-1. 계정과 저장소 만들기

1. [GitHub](https://github.com/)에서 `Sign up`을 눌러 계정을 만듭니다.
2. 로그인 후 오른쪽 위 `+` → `New repository`를 누릅니다.
3. 이름은 `korea-micro-trend-dashboard`를 추천합니다.
4. `Public`은 누구나 코드를 볼 수 있고, `Private`은 허용한 사람만 볼 수 있습니다. 포트폴리오/공개 서비스면 Public이 편하고, 공개하고 싶지 않으면 Private을 선택하세요. Community Cloud는 연결 권한을 주면 둘 다 사용할 수 있습니다.
5. 이 폴더에는 이미 `README.md`가 있으므로 `Add a README file`은 **체크하지 않습니다**. 체크하면 업로드할 때 같은 파일이 충돌할 수 있습니다.
6. `Create repository`를 누릅니다.

### 5-2. 웹사이트에서 직접 업로드

Git을 아직 설치하지 않았다면 가장 쉬운 방법입니다.

1. 새 저장소 화면에서 `uploading an existing file` 또는 `Add file` → `Upload files`를 누릅니다.
2. 이 프로젝트의 파일과 폴더를 끌어다 놓습니다. `.env`, `.venv`, `data/trends.csv`, `data/history.csv`는 올리지 마세요.
3. 아래 `Commit changes`를 누릅니다.

**commit(커밋)**은 “현재 파일 상태에 이름표를 붙여 저장한 기록”입니다.

### 5-3. Git 명령으로 업로드

먼저 [Git](https://git-scm.com/downloads)을 설치합니다. 프로젝트 폴더 터미널에서 아래를 실행하되, GitHub 주소의 `내아이디`를 바꾸세요.

```powershell
git init
git add .
git commit -m "첫 번째 MVP 완성"
git branch -M main
git remote add origin https://github.com/내아이디/korea-micro-trend-dashboard.git
git push -u origin main
```

- **branch(브랜치)**: 같은 프로젝트에서 작업 흐름을 나누는 가지입니다. `main`은 기본 가지입니다.
- **push(푸시)**: 내 컴퓨터의 커밋을 GitHub 서버로 올리는 작업입니다.
- `git status`: 올릴 파일과 제외된 파일을 미리 확인합니다.

API 키는 계정 과금, 데이터 접근 권한과 연결된 비밀번호 같은 값입니다. GitHub에 공개되면 다른 사람이 악용할 수 있고, 삭제 커밋을 해도 과거 기록에 남을 수 있습니다. 실수로 올렸다면 해당 서비스에서 **즉시 키를 폐기하고 새 키를 발급**하세요.

## 6. Streamlit Community Cloud 배포

공식 배포 문서: [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

1. [Streamlit Community Cloud](https://share.streamlit.io/)에 접속해 가입/로그인합니다.
2. GitHub 계정 연결을 허용합니다. Private 저장소라면 해당 저장소 접근 권한도 허용해야 합니다.
3. 작업 화면 오른쪽 위 `Create app`을 누릅니다.
4. 질문이 보이면 `Yup, I have an app`을 선택합니다.
5. `Repository`에서 `내아이디/korea-micro-trend-dashboard`를 선택합니다. 목록에 없으면 직접 입력할 수 있습니다.
6. `Branch`는 `main`을 선택합니다.
7. `Main file path` 또는 `File path`에는 `app.py`를 입력합니다.
8. `Advanced settings`에서 Python `3.11`을 선택하고 필요한 Secrets를 입력합니다.
9. `Deploy`를 누릅니다. 몇 분 뒤 `https://...streamlit.app` 형태의 공유 주소가 생깁니다.

`requirements.txt`는 클라우드 컴퓨터에게 “이 앱에 streamlit, pandas, plotly 등이 필요하다”고 알려 주는 설치 목록입니다. 이 파일이 없거나 패키지가 빠지면 `ModuleNotFoundError`가 발생합니다. 공식 설명은 [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)에서 볼 수 있습니다.

주의: Community Cloud의 로컬 CSV는 앱 재시작/재배포 때 초기화될 수 있습니다. MVP의 수동 확인에는 충분하지만, 과거 기록을 안정적으로 보관하려면 4차 버전에서 Supabase 같은 외부 DB로 옮기세요.

## 7. API 키와 Secrets 설정

### 로컬: `.env`

`.env.example`을 복사해 이름을 `.env`로 바꾸고 필요한 키만 입력합니다.

```dotenv
YOUTUBE_API_KEY=실제_키
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
OPENAI_API_KEY=
GEMINI_API_KEY=
```

`.env`는 `.gitignore`에 들어 있어 GitHub에서 제외됩니다. 그래도 `git status`로 한 번 더 확인하세요.

### 로컬 Streamlit 또는 Community Cloud: Secrets

로컬에서는 프로젝트 안에 `.streamlit/secrets.toml`을 만들 수 있습니다.

```toml
YOUTUBE_API_KEY = "실제_키"
NAVER_CLIENT_ID = ""
NAVER_CLIENT_SECRET = ""
OPENAI_API_KEY = ""
GEMINI_API_KEY = ""
```

Cloud에서는 배포 시 `Advanced settings` → `Secrets`에 위 내용을 붙여 넣습니다. 배포 후에는 앱 `Settings`에서도 수정할 수 있습니다. `secrets.toml`은 절대 GitHub에 올리지 마세요. 공식 설명: [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

## 8. 자동 갱신 확장 순서

### 1차: 현재 버전 — 수동 갱신

사용자가 버튼을 눌렀을 때만 수집합니다. 호출량을 통제하기 쉽고 오류 원인을 찾기 좋아 MVP에 적합합니다.

### 2차: 화면 자동 새로고침

`streamlit-autorefresh` 패키지를 추가하고 10~30분마다 화면을 다시 실행할 수 있습니다.

```powershell
pip install streamlit-autorefresh
```

`requirements.txt`에 `streamlit-autorefresh`를 추가한 뒤 `app.py`에 아래를 넣습니다.

```python
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=15 * 60 * 1000, key="trend_refresh")  # 15분
```

단, 화면 재실행과 데이터 수집은 구분하는 것이 좋습니다. 방문자가 없으면 Cloud 앱이 쉬는 상태가 될 수 있으므로 안정적인 수집기는 아닙니다.

### 3차: GitHub Actions 또는 외부 스케줄러

수집 코드를 `refresh.py`라는 별도 실행 파일로 분리하고 GitHub Actions의 `schedule`로 10~30분마다 실행합니다. Actions는 예약 시각이 조금 늦어질 수 있습니다. CSV를 계속 Git에 커밋하기보다는 이 단계부터 외부 DB 사용을 권장합니다.

### 4차: Supabase + 독립 수집 작업

스케줄러가 Supabase에 저장하고 Streamlit은 Supabase에서 읽기만 하게 합니다. 방문자 수와 상관없이 기록이 유지되고, 나중에 Next.js/Vercel 화면도 같은 데이터를 사용할 수 있습니다. 현재 `utils/storage.py`가 교체 지점입니다.

## 9. 오류 해결 체크리스트

### 로컬 실행 오류

- `python is not recognized`: Python 재설치 시 `Add Python to PATH` 체크, 터미널 재시작
- `streamlit is not recognized`: 가상환경이 켜졌는지 확인 후 `pip install -r requirements.txt`
- `ModuleNotFoundError`: 프로젝트 폴더에서 설치했는지와 `(.venv)` 표시 확인
- PowerShell 실행 정책 오류: 위의 `Set-ExecutionPolicy -Scope Process ...` 실행
- 포트 8501 사용 중: `streamlit run app.py --server.port 8502` 후 `http://localhost:8502`
- 한글 깨짐: CSV를 UTF-8 또는 UTF-8 with BOM으로 저장. 이 앱은 `utf-8-sig`로 읽고 씀
- 빈 화면: 사이드바 필터를 모두 선택하고 `sample_data/sample_trends.csv` 존재 확인
- RSS 실패: 인터넷 연결·회사 방화벽 확인. 수집 상태 펼침에서 이유 확인. 앱은 샘플로 계속 동작

### Community Cloud 배포 오류

- GitHub 저장소에 `app.py`, `requirements.txt`, `sample_data/sample_trends.csv`가 실제로 있는지 확인
- Repository/Branch/File path가 `저장소 / main / app.py`인지 확인
- `ModuleNotFoundError`에 나온 패키지가 `requirements.txt`에 있는지 확인
- Python 버전을 로컬과 같은 3.11로 선택했는지 확인
- Secrets 형식이 `KEY = "value"`인 TOML 형식인지 확인
- Private 저장소 접근 권한을 Streamlit에 허용했는지 확인
- 앱 오른쪽의 로그에서 가장 아래쪽 빨간 오류부터 확인
- 수정한 뒤 GitHub에 commit/push 되었는지 확인
- 일시적 문제면 앱 `Settings`에서 `Reboot app` 실행

## 10. 다음 단계 확장 아이디어

1. 네이버 데이터랩 공식 API 연결 후 10대·20대 반응 컬럼 추가
2. YouTube 제목에서 핵심 키워드를 추출해 중복 품질 개선
3. OpenAI/Gemini로 기사 2~3개를 근거로 한 한 줄 요약 생성
4. 스팸 사전과 동의어 사전 관리 화면 추가
5. 점수 변화 그래프와 24시간 최고점 기록
6. Supabase로 현재/과거 테이블 이전
7. GitHub Actions 또는 외부 스케줄러로 15분 수집
8. 사용량이 커지면 Next.js + Vercel 전광판으로 화면 분리

샘플 데이터는 기능 확인용이며 실제 현재 순위를 뜻하지 않습니다. `수동 갱신` 뒤 공개 피드에서 받아온 행부터 실제 수집 시각과 점수 근거가 적용됩니다.
