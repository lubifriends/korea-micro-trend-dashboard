# 완전 초보용: GitHub 업로드부터 Streamlit 배포까지 클릭 안내서

이 문서는 명령어를 몰라도 진행할 수 있는 **웹사이트 클릭 전용 안내서**입니다. 아래 순서대로 하면 됩니다.

## 시작하기 전에 준비할 것

1. `korea-micro-trend-dashboard-mvp.zip` 파일을 찾습니다.
2. ZIP 파일을 마우스 오른쪽 버튼으로 클릭합니다.
3. Windows 11이면 `모두 압축 풀기...`를 누릅니다.
4. 압축을 풀 위치를 확인하고 `압축 풀기`를 누릅니다.
5. 압축이 풀린 폴더를 엽니다.
6. 안쪽의 `github-upload-ready` 폴더를 엽니다.
7. 이 폴더 바로 안에 `app.py`, `README.md`, `requirements.txt`가 보이는지 확인합니다.

중요: GitHub에는 ZIP 파일 하나를 올리는 것이 아닙니다. **ZIP을 풀고 `github-upload-ready` 안의 파일과 폴더를 올립니다.**

---

# 1단계: GitHub 계정 만들기

이미 GitHub 계정이 있으면 2단계로 넘어갑니다.

1. Chrome 또는 Edge 브라우저를 엽니다.
2. 주소창에 `https://github.com`을 입력하고 Enter를 누릅니다.
3. 화면 오른쪽 위의 `Sign up` 버튼을 누릅니다.
4. 다음 방법 중 편한 것을 선택합니다.
   - Google 계정으로 만들려면 `Continue with Google`
   - 이메일로 만들려면 화면 안내에 따라 이메일, 비밀번호, 사용할 아이디를 입력
5. 이메일 확인을 요구하면 이메일 받은편지함을 엽니다.
6. GitHub가 보낸 메일의 확인 버튼을 누르거나 인증번호를 GitHub 화면에 입력합니다.
7. GitHub로 돌아와 로그인합니다.

성공 확인: 오른쪽 위에 `Sign up` 대신 내 프로필 사진 또는 동그란 사용자 아이콘이 보이면 로그인된 것입니다.

공식 안내: <https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github>

---

# 2단계: 빈 Repository 만들기

Repository(리포지토리)는 **GitHub 안에 만드는 프로젝트 폴더**입니다.

1. GitHub에 로그인한 상태에서 화면 오른쪽 위의 `+` 아이콘을 누릅니다.
2. 펼쳐진 메뉴에서 `New repository`를 누릅니다.
   - 바로 이동하려면 주소창에 `https://github.com/new`을 입력해도 됩니다.
3. `Owner`는 보통 내 GitHub 아이디가 선택되어 있습니다. 그대로 둡니다.
4. `Repository name` 입력칸에 아래 이름을 그대로 입력합니다.

```text
korea-micro-trend-dashboard
```

5. `Description`은 선택 사항입니다. 넣고 싶다면 아래 문장을 입력합니다.

```text
한국 실시간 마이크로 트렌드 전광판 Streamlit MVP
```

6. 공개 범위를 선택합니다.
   - `Public`: 누구나 코드를 볼 수 있음. 처음 배포할 때 가장 단순해서 권장
   - `Private`: 나와 허용한 사람만 코드를 볼 수 있음. Streamlit에 별도 접근 권한을 허용해야 함
7. `Add a README file`은 **체크하지 않습니다**.
8. `.gitignore` 선택 메뉴는 `None` 그대로 둡니다.
9. `Choose a license`도 `None` 그대로 둡니다.
10. 아래쪽의 초록색 `Create repository` 버튼을 누릅니다.

왜 README를 체크하지 않나요? 지금 올릴 프로젝트에 이미 `README.md`가 있기 때문입니다. 여기서 새 README를 만들면 같은 이름의 파일이 겹칠 수 있습니다.

성공 확인: 화면 위쪽에 `내아이디 / korea-micro-trend-dashboard`가 표시되고, 가운데에 `Quick setup`이 보이면 성공입니다.

공식 안내: <https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository>

---

# 3단계: 프로젝트 파일을 GitHub 웹사이트에서 올리기

## 방금 만든 빈 저장소의 Quick setup 화면에 있는 경우

1. `Quick setup` 아래 문장에서 `uploading an existing file`이라는 파란 링크를 찾습니다.
2. `uploading an existing file`을 누릅니다.

## 저장소에 다른 화면이 보이는 경우

1. 저장소 화면 위쪽의 `Code` 탭을 누릅니다.
2. 파일 목록 오른쪽 위의 `Add file` 버튼을 누릅니다.
3. 펼쳐진 메뉴에서 `Upload files`를 누릅니다.

## 실제 파일 선택

1. Windows 파일 탐색기에서 압축을 풀어 둔 `github-upload-ready` 폴더를 엽니다.
2. 폴더 안의 빈 공간을 한 번 클릭합니다.
3. 키보드에서 `Ctrl+A`를 눌러 **안에 있는 파일과 폴더를 모두 선택**합니다.
4. 선택된 항목을 마우스로 잡아 GitHub의 `Drag files here to add them to your repository` 영역에 끌어다 놓습니다.
5. 업로드가 끝날 때까지 기다립니다.

반드시 업로드 목록에 있어야 하는 항목:

```text
app.py
requirements.txt
README.md
.gitignore
.env.example
.streamlit/config.toml
components/...
utils/...
sample_data/sample_trends.csv
data/.gitkeep
DEPLOY_CLICK_GUIDE_KO.md
```

주의할 점:

- ZIP 파일 하나만 올리면 안 됩니다.
- `app.py`가 `github-upload-ready/app.py`처럼 한 단계 안쪽으로 들어가면 안 됩니다.
- GitHub 저장소 첫 화면에서 `app.py`가 바로 보여야 합니다.
- `.env`나 `secrets.toml`은 올리면 안 됩니다. 현재 패키지에는 실제 키가 든 파일이 없습니다.

## 업로드를 저장하는 버튼

1. 업로드 화면 아래의 `Commit changes` 영역으로 내려갑니다.
2. 첫 번째 입력칸에 아래처럼 입력합니다.

```text
첫 번째 트렌드 대시보드 업로드
```

3. 긴 설명 입력칸은 비워도 됩니다.
4. 선택지가 보이면 `Commit directly to the main branch`를 선택합니다.
5. 초록색 `Commit changes` 버튼을 누릅니다.
   - 새 창이 한 번 더 뜨면 그 창의 `Commit changes`도 다시 누릅니다.

commit(커밋)은 **현재 파일 상태를 GitHub에 한 번 저장하는 것**입니다.

성공 확인:

1. 저장소의 `Code` 탭으로 돌아옵니다.
2. 파일 목록 최상단에 `app.py`, `requirements.txt`, `README.md`가 바로 보여야 합니다.
3. `components`, `utils`, `sample_data` 폴더도 보여야 합니다.
4. 위쪽 branch 표시가 `main`인지 확인합니다.

여기까지 보이면 GitHub 업로드가 끝난 것입니다.

---

# 4단계: Streamlit Community Cloud 가입하기

1. 새 브라우저 탭을 엽니다.
2. 주소창에 `https://share.streamlit.io`를 입력하고 Enter를 누릅니다.
3. `Continue to sign-in` 버튼을 누릅니다.
4. `Continue with GitHub` 버튼을 누릅니다.
5. GitHub 로그인 화면이 나오면 방금 만든 GitHub 계정으로 로그인합니다.
6. 권한 확인 화면이 나오면 내용을 확인하고 `Authorize` 또는 `Authorize Streamlit Community Cloud` 버튼을 누릅니다.
7. 이름 같은 추가 정보를 묻는 화면이 나오면 입력합니다.
8. 화면 아래쪽의 `Continue` 또는 `I accept` 버튼을 누릅니다.

성공 확인: Streamlit 작업 화면이 열리고 왼쪽 위에 내 사용자 이름 또는 Workspace 이름이 보이면 가입된 것입니다.

공식 안내: <https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/create-your-account>

---

# 5단계: Streamlit에서 GitHub 저장소 접근 허용하기

GitHub로 로그인했어도 저장소 접근 권한은 한 번 더 연결해야 할 수 있습니다.

1. Streamlit 화면 왼쪽 위의 `Workspaces` 옆에 경고 표시가 있는지 확인합니다.
2. 경고 표시 또는 Workspace 이름을 누릅니다.
3. 메뉴에서 `Connect GitHub account`를 누릅니다.
4. GitHub 권한 화면이 열리면 `Authorize streamlit`을 누릅니다.
5. Public 저장소만 사용할 경우 공개 저장소 접근 권한이면 충분합니다.

Private 저장소가 목록에 안 보이는 경우:

1. Streamlit 왼쪽 위의 내 Workspace 이름을 누릅니다.
2. `Settings`를 누릅니다.
3. 왼쪽 메뉴에서 `Linked accounts`를 누릅니다.
4. `Source control` 영역의 `Connect here →`를 누릅니다.
5. GitHub 화면에서 `Authorize streamlit`을 누릅니다.
6. 저장소 선택 화면이 나오면 `korea-micro-trend-dashboard` 접근을 허용합니다.

성공 확인: Workspace의 경고 표시가 사라지거나 GitHub가 Connected 상태로 표시됩니다.

공식 안내: <https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/quickstart>

---

# 6단계: Create app을 눌러 실제 사이트 배포하기

1. Streamlit 작업 화면 오른쪽 위의 `Create app` 버튼을 누릅니다.
2. `Do you already have an app?`이라는 질문이 나오면 `Yup, I have an app`을 누릅니다.
3. 배포 설정 화면에 다음 값을 입력합니다.

## Repository

`Repository` 선택칸을 누릅니다.

목록에서 아래 항목을 선택합니다.

```text
내GitHub아이디/korea-micro-trend-dashboard
```

목록에 없으면:

- Repository 입력칸에 `내GitHub아이디/korea-micro-trend-dashboard`를 직접 입력합니다.
- 그래도 안 되면 앞의 5단계 GitHub 연결을 다시 확인합니다.
- GitHub 저장소가 Private이면 Private 저장소 접근 권한을 확인합니다.

## Branch

`Branch` 입력칸 또는 선택칸에 아래 값을 넣습니다.

```text
main
```

branch(브랜치)는 **프로젝트 작업 흐름을 나눈 가지**입니다. 지금은 기본 가지인 `main`만 사용합니다.

## Main file path 또는 File path

아래 값을 정확히 입력합니다.

```text
app.py
```

`/app.py`, `github-upload-ready/app.py`, `trend-dashboard/app.py`라고 쓰지 않습니다. GitHub 첫 화면에 `app.py`가 바로 보인다면 `app.py`가 정답입니다.

## App URL

선택 사항입니다. 입력칸이 보이면 원하는 주소를 입력할 수 있습니다.

예:

```text
korea-micro-trend
```

이미 다른 사람이 사용 중이면 다른 이름을 입력하거나 비워 둡니다. 비워 두면 Streamlit이 자동으로 주소를 만듭니다.

---

# 7단계: Advanced settings 설정하기

1. 배포 설정 화면에서 `Advanced settings`를 누릅니다.
2. `Python version` 선택 메뉴를 누릅니다.
3. `3.11`을 선택합니다.

## YouTube API 키가 아직 없는 경우

`Secrets` 입력칸은 비워 둬도 됩니다. 앱은 YouTube 샘플 데이터를 사용합니다.

## YouTube API 키가 있는 경우

`Secrets` 입력칸에 아래처럼 입력합니다. 따옴표 안의 값만 실제 키로 바꿉니다.

```toml
YOUTUBE_API_KEY = "여기에_실제_키"
```

나중에 다른 API 키도 생기면 다음 형식으로 추가합니다.

```toml
YOUTUBE_API_KEY = "실제_YouTube_키"
NAVER_CLIENT_ID = "실제_네이버_ID"
NAVER_CLIENT_SECRET = "실제_네이버_비밀값"
OPENAI_API_KEY = "실제_OpenAI_키"
GEMINI_API_KEY = "실제_Gemini_키"
```

주의:

- `YOUTUBE_API_KEY=값`이 아니라 TOML 형식인 `YOUTUBE_API_KEY = "값"`으로 씁니다.
- 실제 키를 GitHub의 코드 파일이나 README에 쓰면 안 됩니다.
- Secrets 화면에 저장한 값은 일반 방문자에게 보이지 않습니다.

4. 설정을 마쳤으면 `Save`를 누릅니다.

공식 안내: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management>

---

# 8단계: Deploy 누르기

최종 입력값을 다시 확인합니다.

```text
Repository: 내아이디/korea-micro-trend-dashboard
Branch: main
File path: app.py
Python: 3.11
```

1. 화면 아래 또는 오른쪽의 `Deploy` 버튼을 누릅니다.
2. 화면에 설치 로그가 흐르면 그대로 기다립니다.
3. 첫 배포는 보통 몇 분 걸릴 수 있습니다.
4. 브라우저 탭을 닫지 말고 앱 화면이 나타날 때까지 기다립니다.

성공 확인:

- `Korea Micro Trend Dashboard` 제목이 보입니다.
- 왼쪽에 카테고리/출처 필터가 보입니다.
- TOP 20 카드가 보입니다.
- 주소창이 `https://어떤이름.streamlit.app` 형태입니다.
- `지금 수동 갱신` 버튼을 누를 수 있습니다.

이 주소가 다른 사람에게 공유할 수 있는 실제 사이트 주소입니다.

공식 안내: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>

---

# 9단계: 배포가 실패했을 때 화면에서 확인하는 곳

## `Repository not found` 또는 저장소가 목록에 없음

1. Streamlit Workspace 이름을 누릅니다.
2. `Settings`를 누릅니다.
3. `Linked accounts`를 누릅니다.
4. GitHub 연결 상태를 확인합니다.
5. 필요하면 `Connect here →`를 눌러 다시 허용합니다.

## `File does not exist: app.py`

1. GitHub 저장소로 돌아갑니다.
2. `Code` 탭을 누릅니다.
3. 첫 화면에 `app.py`가 바로 보이는지 확인합니다.
4. 바로 보이면 Streamlit File path를 `app.py`로 입력합니다.
5. `github-upload-ready` 폴더 안에 들어가야 app.py가 보인다면 파일을 잘못된 단계에 올린 것입니다. 저장소 최상단으로 다시 올려야 합니다.

## `ModuleNotFoundError`

1. 오류 문장에서 `No module named '무언가'` 부분을 찾습니다.
2. GitHub 저장소 첫 화면에 `requirements.txt`가 있는지 확인합니다.
3. `requirements.txt`를 눌렀을 때 `streamlit`, `pandas`, `requests`, `feedparser`, `plotly`, `python-dotenv`가 보이는지 확인합니다.
4. Streamlit 앱 메뉴에서 `Reboot app`을 누릅니다.

## Secrets 오류 또는 TOML 오류

1. Streamlit 앱 화면 오른쪽 아래 또는 오른쪽 위의 `Manage app`을 누릅니다.
2. `Settings`를 누릅니다.
3. `Secrets`를 엽니다.
4. 모든 값에 큰따옴표가 있는지 확인합니다.

정상 예:

```toml
YOUTUBE_API_KEY = "abc123"
```

잘못된 예:

```text
YOUTUBE_API_KEY=abc123
```

## 앱은 열리지만 실시간 데이터가 안 나옴

1. 앱의 `전체 수집 상태`를 누릅니다.
2. Google Trends 또는 Google News 실패 메시지를 확인합니다.
3. 잠시 뒤 `지금 수동 갱신`을 다시 누릅니다.
4. 외부 RSS가 실패해도 샘플 화면은 계속 표시되는 것이 정상입니다.

## 코드를 고쳤는데 사이트가 그대로임

1. GitHub 저장소에서 수정한 파일이 실제로 보이는지 확인합니다.
2. 저장소 위쪽의 branch가 `main`인지 확인합니다.
3. 마지막 commit 시간이 방금 수정한 시간인지 확인합니다.
4. Streamlit의 `Manage app` → `Reboot app`을 누릅니다.

---

# 10단계: 나중에 파일을 다시 수정해서 올리는 방법

가장 쉬운 웹 업로드 방법입니다.

1. GitHub에서 `korea-micro-trend-dashboard` 저장소를 엽니다.
2. `Code` 탭을 누릅니다.
3. `Add file`을 누릅니다.
4. `Upload files`를 누릅니다.
5. 수정된 파일을 끌어다 놓습니다.
6. 아래 commit 메시지에 수정 내용을 씁니다.

예:

```text
카드 디자인 수정
```

7. `Commit directly to the main branch`를 선택합니다.
8. `Commit changes`를 누릅니다.
9. Streamlit Community Cloud는 GitHub의 새 commit을 감지해 자동으로 다시 배포합니다.

---

# 마지막 30초 확인표

- [ ] GitHub 저장소 첫 화면에 `app.py`가 바로 보인다.
- [ ] GitHub 저장소 첫 화면에 `requirements.txt`가 바로 보인다.
- [ ] GitHub branch는 `main`이다.
- [ ] `.env`와 `secrets.toml`을 GitHub에 올리지 않았다.
- [ ] Streamlit Repository는 `내아이디/korea-micro-trend-dashboard`다.
- [ ] Streamlit Branch는 `main`이다.
- [ ] Streamlit File path는 `app.py`다.
- [ ] Python은 `3.11`이다.
- [ ] 배포된 주소가 `.streamlit.app`으로 끝난다.

