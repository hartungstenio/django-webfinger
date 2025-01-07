from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, ClassVar

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View

from .finders import SchemeUserFinder, UserFinder

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class WebFingerView(View):
    http_method_names: ClassVar[list[str]] = [
        "get",
        "head",
        "options",
        "trace",
    ]

    async def get(self, request: HttpRequest) -> HttpResponse:
        try:
            resource: str = request.GET["resource"]
        except KeyError:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        else:
            finder: UserFinder = SchemeUserFinder()
            user: AbstractUser | None = await finder.afind_resource(resource)
            if not user:
                return HttpResponse(status=HTTPStatus.NOT_FOUND)

            data: dict[str, Any] = {
                "subject": f"acct:{user.get_username()}",
            }
            if email := getattr(user, user.get_email_field_name()):
                data["aliases"] = [f"mailto:{email}"]

            return JsonResponse(data, content_type="application/jrd+json")
