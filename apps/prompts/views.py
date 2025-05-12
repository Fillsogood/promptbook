from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Prompt, PromptLog
from .serializers import PromptLogSerializer, PromptSerializer


class PromptListCreateView(generics.ListCreateAPIView):
    """
    - GET: 로그인 유저의 프롬프트 목록 조회
    - POST: 프롬프트 생성
    """

    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prompt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PromptRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET: 프롬프트 상세 조회
    - PUT/PATCH: 수정
    - DELETE: 삭제
    """

    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prompt.objects.filter(user=self.request.user)


class RunPromptView(APIView):
    """
    - POST: 프롬프트 실행(Mock) + 로그 저장
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        prompt = get_object_or_404(Prompt, pk=pk, user=request.user)
        input_text = request.data.get("input_text", "").strip()

        if not input_text:
            return Response({"message": "input_text는 필수이며 빈 문자열일 수 없습니다."}, status=400)

        output_text = f"[MOCK RESPONSE] '{prompt.title}' → '{input_text}'"

        try:
            PromptLog.objects.create(prompt=prompt, user=request.user, input_text=input_text, output_text=output_text)
        except Exception:
            return Response({"message": "프롬프트 실행 이력을 저장하지 못했습니다."}, status=500)

        return Response({"output": output_text}, status=200)


class PromptLogListView(generics.ListAPIView):
    """
    - GET: 유저의 프롬프트 실행 이력 조회
    """

    serializer_class = PromptLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PromptLog.objects.filter(user=self.request.user)
