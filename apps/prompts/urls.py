# apps/prompts/urls.py
from django.urls import path

from .views import (
    PromptListCreateView,
    PromptLogListView,
    PromptRetrieveUpdateDestroyView,
    RunPromptView,
)

urlpatterns = [
    path("", PromptListCreateView.as_view(), name="prompt-list-create"),
    path("<int:pk>/", PromptRetrieveUpdateDestroyView.as_view(), name="prompt-detail"),
    path("<int:pk>/run/", RunPromptView.as_view(), name="prompt-run"),
    path("logs/", PromptLogListView.as_view(), name="prompt-logs"),
]
