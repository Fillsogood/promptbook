# tests/accounts/test_auth.py (pytest 버전)
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()
pytestmark = pytest.mark.django_db  # 전체 테스트에서 DB 사용 허용


# DRF APIClient 인스턴스 제공
@pytest.fixture
def api_client():
    return APIClient()


# 테스트 유저 생성용 fixture
@pytest.fixture
def create_user():
    def _create_user(email="user@example.com", username="user", password="pass1234"):
        return User.objects.create_user(email=email, username=username, password=password)

    return _create_user


# 회원가입 성공 테스트
def test_user_registration_success(api_client):
    url = reverse("register")
    data = {"email": "test@naver.com", "username": "testuser", "password": "pass1234"}
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert response.data["message"] == "회원가입 되었습니다."


# 로그인 성공 테스트 (쿠키 기반)
def test_user_login_success(api_client, create_user):
    create_user(email="test@naver.com", username="testuser", password="pass1234")
    response = api_client.post(reverse("login"), data={"email": "test@naver.com", "password": "pass1234"})
    assert response.status_code == 200
    assert response.data["message"] == "로그인 성공"
    assert "access_token" not in response.data  # 쿠키에만 저장됨
    assert "refresh_token" not in response.data
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


# 회원가입 실패 테스트 (이메일 중복)
def test_user_registration_failure(api_client, create_user):
    create_user(email="test@naver.com")
    response = api_client.post(
        reverse("register"),
        data={"email": "test@naver.com", "username": "otheruser", "password": "pass1234"},
    )
    assert response.status_code == 400
    assert "email" in response.data
    assert "already exists" in response.data["email"][0]


# 인증된 사용자 정보 조회 테스트 (access_token 쿠키 기반)
def test_get_me_success(api_client, create_user):
    create_user(email="me@naver.com", username="me", password="pass1234")
    login_response = api_client.post(reverse("login"), data={"email": "me@naver.com", "password": "pass1234"})
    assert "access_token" in login_response.cookies
    cookie = login_response.cookies["access_token"].value
    api_client.cookies["access_token"] = cookie

    response = api_client.get(reverse("me"))
    assert response.status_code == 200
    assert response.data["email"] == "me@naver.com"


# 인증 없이 사용자 정보 조회 시도 → 실패
def test_get_me_unauthorized(api_client):
    response = api_client.get(reverse("me"))
    assert response.status_code == 401


# 비밀번호 변경 성공 테스트 (access_token 쿠키 사용)
def test_change_password_success(api_client, create_user):
    user = create_user(password="oldpass123")
    login_response = api_client.post(reverse("login"), data={"email": user.email, "password": "oldpass123"})
    api_client.cookies["access_token"] = login_response.cookies["access_token"].value

    url = reverse("change_password")
    data = {"current_password": "oldpass123", "new_password": "newpass456"}
    response = api_client.put(url, data)
    assert response.status_code == 200
    assert response.data["message"] == "비밀번호가 변경되었습니다."


# 비밀번호 변경 실패 테스트 (잘못된 현재 비밀번호)
def test_change_password_fail(api_client, create_user):
    user = create_user(password="correctpass")
    login_response = api_client.post(reverse("login"), data={"email": user.email, "password": "correctpass"})
    api_client.cookies["access_token"] = login_response.cookies["access_token"].value

    url = reverse("change_password")
    data = {"current_password": "wrongpass", "new_password": "newpass"}
    response = api_client.put(url, data)
    assert response.status_code == 400
    assert response.data["message"] == "현재 비밀번호가 틀렸습니다."


# 회원 탈퇴 테스트 (access_token 쿠키 사용)
def test_delete_account(api_client, create_user):
    user = create_user(email="delete@example.com")
    login_response = api_client.post(reverse("login"), data={"email": user.email, "password": "pass1234"})
    api_client.cookies["access_token"] = login_response.cookies["access_token"].value

    response = api_client.delete(reverse("delete_account"))
    assert response.status_code == 204
    assert User.objects.filter(email="delete@example.com").count() == 0
