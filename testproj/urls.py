from django.urls import include, path

urlpatterns = [
    path(".well-known/", include("django_webfinger.urls", namespace="django_webfinger")),
]
