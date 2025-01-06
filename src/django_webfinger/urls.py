from django.urls import path

from .views import WebFingerView

app_name = "django_webfinger"

urlpatterns = [
    path("", WebFingerView.as_view(), name="webfinger"),
]
