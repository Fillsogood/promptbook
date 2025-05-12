from typing import Type

from django.contrib.auth import authenticate
from django.db import DatabaseError, IntegrityError
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.models import User

from .serializers import LoginSerializer, RegisterSerializer


# 회원가입
class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({"message": "회원가입 되었습니다."}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({"message": "데이터 무결성 오류가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST)

        except DatabaseError:
            return Response(
                {"message": "데이터베이스 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response({"message": f"알 수 없는 오류: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 로그인
class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        refresh = response.data.get("refresh")
        access = response.data.get("access")

        # 응답에서 토큰 제거
        response.data.pop("refresh", None)
        response.data.pop("access", None)
        response.data["message"] = "로그인 성공"

        # Access Token 쿠키
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=30 * 60,  # 30분
        )

        # Refresh Token 쿠키
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=7 * 24 * 60 * 60,  # 7일
        )

        return response

# 로그아웃
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"message": "Refresh token이 없습니다."}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"message": f"토큰 블랙리스트 등록 실패: {str(e)}"}, status=400)

        res = Response({"message": "로그아웃 완료"}, status=200)
        res.delete_cookie("access_token")
        res.delete_cookie("refresh_token")
        return res

# 내 정보
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"message": "인증되지 않은 사용자입니다."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "email": user.email,
                "username": user.username,
            },
            status=status.HTTP_200_OK,
        )

# 비밀번호 초기화
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response({"message": "현재 비밀번호가 틀렸습니다."}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"message": "비밀번호가 변경되었습니다."}, status=200)

# 회원탈퇴
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=204)

# 토큰 재발급
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise AuthenticationFailed("Refresh token이 쿠키에 없습니다.")

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            raise AuthenticationFailed("유효하지 않은 refresh token입니다.")

        return Response(serializer.validated_data, status=200)
