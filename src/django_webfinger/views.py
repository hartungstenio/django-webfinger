from __future__ import annotations

from http import HTTPStatus
from typing import ClassVar

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View


class WebFingerView(View):
    http_method_names: ClassVar[list[str]] = [
        "get",
        "head",
        "options",
        "trace",
    ]

    async def get(self, request: HttpRequest) -> HttpResponse:
        try:
            resource = request.GET["resource"]
        except KeyError:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        else:
            return JsonResponse(content_type="application/jrd+json")
