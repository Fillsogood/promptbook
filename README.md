# 🧠 PromptBook - 프롬프트 관리 및 실행 API

LLM 기반 SaaS 기능의 핵심만 담은 **경량화된 프롬프트 관리/실행 시스템**입니다.  
GPT 프롬프트를 저장하고, 실행하고, 실행 이력을 확인할 수 있는 RESTful API를 구현했습니다.

> ✅ 비용 부담 없이 테스트 가능 (Mock 응답 사용)  
> ✅ JWT 토큰을 HttpOnly 쿠키에 저장하여 보안 강화  
> ✅ Pytest 기반으로 전체 기능 테스트 커버

---

## 🔧 기능 요약

### 1. 프롬프트 관리 (CRUD)
- 프롬프트 생성/조회/수정/삭제
- 태그를 통한 분류 기능 지원 (`ManyToMany`)
- 유저별 프라이빗한 프롬프트 저장

### 2. 프롬프트 실행 (Run)
- 저장된 프롬프트에 `input_text`를 넣어 실행
- 결과는 `[MOCK RESPONSE]` 형식으로 반환
- 실행 결과는 `PromptLog`로 저장됨

### 3. 실행 로그 관리
- 유저가 실행한 프롬프트의 입력/출력 이력 확인
- 분석 및 복기용 기록 저장

### 4. 인증 및 보안
- JWT Access / Refresh Token을 모두 `HttpOnly` 쿠키로 관리
- `Refresh Token`은 `Blacklist`에 등록 후 재사용 차단
- DRF 커스텀 인증 클래스 `CookieJWTAuthentication` 적용

### 5. 테스트 자동화
- Pytest 기반의 전 기능 테스트 작성 완료
- 유닛 테스트: 회원가입, 로그인, 프롬프트 CRUD, 실행, 로그
- APIClient를 이용한 통합 시나리오 커버

---

## 🛠 기술 스택

| 항목        | 내용                                       |
|-------------|--------------------------------------------|
| Language    | Python 3.13                                |
| Framework   | Django 4.2 + Django REST Framework         |
| DB          | MySQL (PyMySQL)                            |
| Auth        | SimpleJWT + 쿠키 기반 인증                 |
| Testing     | Pytest + Django Fixtures                   |
| 기타        | token_blacklist 사용, 커스텀 유저모델 적용 |

---

## ▶️ 실행 방법

```bash
# 1. Poetry로 의존성 설치
poetry install

# 2. DB 마이그레이션 적용
python manage.py migrate

# 3. 테스트 코드 실행 (Pytest)
./run.sh

---

## 🛠️ .env 환경 변수 예시

`.env` 파일은 프로젝트 설정값을 안전하게 관리하기 위한 환경 변수 파일입니다.

```env
# Django
SECRET_KEY=your_django_secret_key_here

# MySQL
DB_NAME=
DB_USER= 
DB_PASSWORD=
DB_HOST=
DB_PORT=

# JWT (선택)
ACCESS_TOKEN_LIFETIME_MINUTES=30
REFRESH_TOKEN_LIFETIME_DAYS=7
```

> `.env` 파일은 Git에 커밋되지 않으며, `.gitignore`에 포함되어 있습니다.
