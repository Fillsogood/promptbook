# apps/accounts/views.py

from django.db import DatabaseError, IntegrityError
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import RegisterSerializer


class RegisterView(APIView):
    """
    회원가입 처리
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "회원가입 되었습니다."}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"message": "데이터 무결성 오류가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError:
            return Response(
                {"message": "데이터베이스 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception:
            return Response(
                {"message": "알 수 없는 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(TokenObtainPairView):
    """
    로그인 처리 (Access / Refresh 토큰을 쿠키로 저장)
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.get("refresh")
        access = response.data.get("access")

        response.data.clear()
        response.data["message"] = "로그인 성공"

        response.set_cookie("access_token", access, httponly=True, secure=True, samesite="Strict", max_age=1800)
        response.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="Strict", max_age=604800)

        return response


class LogoutView(APIView):
    """
    로그아웃 처리 (Refresh 블랙리스트 등록 및 쿠키 제거)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"message": "Refresh token이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"message": "토큰 블랙리스트 등록 실패"}, status=status.HTTP_400_BAD_REQUEST)

        res = Response({"message": "로그아웃 완료"}, status=status.HTTP_200_OK)
        res.delete_cookie("access_token")
        res.delete_cookie("refresh_token")
        return res


class MeView(APIView):
    """
    로그인된 사용자 정보 조회
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({"email": user.email, "username": user.username}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    비밀번호 변경
    """

    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        if not user.check_password(request.data.get("current_password")):
            return Response({"message": "현재 비밀번호가 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(request.data.get("new_password"))
        user.save()
        return Response({"message": "비밀번호가 변경되었습니다."}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    """
    회원 탈퇴
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response({"message": "회원 탈퇴가 완료되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class CookieTokenRefreshView(TokenRefreshView):
    """
    쿠키 기반 토큰 재발급
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise AuthenticationFailed("Refresh token이 쿠키에 없습니다.")

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            raise AuthenticationFailed("유효하지 않은 refresh token입니다.")

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
