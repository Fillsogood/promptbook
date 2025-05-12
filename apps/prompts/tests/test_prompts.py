import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.prompts.models import Prompt, PromptLog

User = get_user_model()
pytestmark = pytest.mark.django_db  # 모든 테스트에서 DB 사용 허용


# 테스트용 사용자 생성
@pytest.fixture
def user():
    return User.objects.create_user(email="tester@example.com", username="tester", password="pass1234")


# 로그인된 APIClient 제공 (access_token을 쿠키로 설정)
@pytest.fixture
def api_client_logged_in(user):
    client = APIClient()
    login_response = client.post(reverse("login"), data={"email": user.email, "password": "pass1234"})
    assert login_response.status_code == 200
    client.cookies["access_token"] = login_response.cookies["access_token"].value
    return client


# 테스트용 프롬프트 생성
@pytest.fixture
def prompt(user):
    return Prompt.objects.create(user=user, title="Test Prompt", content="Say {input}!")


# 프롬프트 생성 테스트
def test_create_prompt(api_client_logged_in):
    url = reverse("prompt-list-create")
    data = {"title": "My Prompt", "content": "Answer as {input}."}
    res = api_client_logged_in.post(url, data)

    # 프롬프트가 성공적으로 생성되었는지 확인
    assert res.status_code == 201
    assert res.data["title"] == "My Prompt"


# 프롬프트 목록 조회 테스트
def test_list_prompts(api_client_logged_in, prompt):
    url = reverse("prompt-list-create")
    res = api_client_logged_in.get(url)

    # 응답에 이전에 생성한 프롬프트가 포함되어 있는지 확인
    assert res.status_code == 200
    assert any(p["title"] == "Test Prompt" for p in res.data)


# 프롬프트 실행 테스트 (MOCK 응답 확인)
def test_run_prompt(api_client_logged_in, prompt):
    url = reverse("prompt-run", args=[prompt.id])
    data = {"input_text": "world"}
    res = api_client_logged_in.post(url, data)

    # 프롬프트 실행 결과가 MOCK 응답인지 확인
    assert res.status_code == 200
    assert "[MOCK RESPONSE]" in res.data["output"]


# 프롬프트 실행 로그 조회 테스트
def test_prompt_logs(api_client_logged_in, prompt, user):
    # 사전 로그 데이터 생성
    PromptLog.objects.create(prompt=prompt, user=user, input_text="Hi", output_text="Hello!")

    url = reverse("prompt-logs")
    res = api_client_logged_in.get(url)

    # 로그 리스트에 예상 출력이 포함되어 있는지 확인
    assert res.status_code == 200
    assert any("Hello!" in log["output_text"] for log in res.data)
