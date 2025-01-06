from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test import AsyncClient, Client
from django.urls import reverse

if TYPE_CHECKING:
    from django.http import HttpResponse

pytestmark = pytest.mark.django_db


class TestWebFingerView:
    @pytest.mark.asyncio
    async def test_get_without_resource_fails(self, async_client: Client):
        response: HttpResponse = await async_client.get(reverse("django_webfinger:webfinger"))

        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
    async def test_methods_not_allowed_async(self, method: str, async_client: AsyncClient):
        django_client_method = getattr(async_client, method)

        response: HttpResponse = await django_client_method(reverse("django_webfinger:webfinger"))

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
