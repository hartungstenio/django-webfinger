from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model

from ._compat import override

if TYPE_CHECKING:
    from collections.abc import Mapping

    from django.contrib.auth.models import AbstractUser


class UserFinder(ABC):
    @abstractmethod
    async def afind_resource(self, uri: str) -> AbstractUser: ...

    def find_resource(self, uri: str) -> AbstractUser:
        return async_to_sync(self.afind_resource)(uri)


class AcctUserFinder(UserFinder):
    @override
    async def afind_resource(self, uri: str) -> AbstractUser:
        parsed: ParseResult = urlparse(uri)
        if parsed.scheme != "acct":
            msg = "Invalid scheme"
            raise ValueError(msg)

        try:
            user, _ = parsed.path.split("@")
        except ValueError as exc:
            msg = "Invalid account"
            raise ValueError(msg) from exc

        user_model: type[AbstractUser] = get_user_model()
        query: dict[str, str] = {user_model.USERNAME_FIELD: user}
        try:
            return await user_model.objects.aget(**query)
        except user_model.DoesNotExist:
            return None


class MailUserFinder(UserFinder):
    @override
    async def afind_resource(self, uri: str) -> AbstractUser:
        parsed: ParseResult = urlparse(uri)
        if parsed.scheme != "mailto":
            msg = "Invalid scheme"
            raise ValueError(msg)

        user_model: type[AbstractUser] = get_user_model()
        query: dict[str, str] = {user_model.EMAIL_FIELD: parsed.path}
        try:
            return await user_model.objects.aget(**query)
        except user_model.DoesNotExist:
            return None


class SchemeUserFinder(UserFinder):
    def __init__(self, lookups: Mapping[str, UserFinder] | None = None):
        if lookups is None:
            lookups = {
                "acct": AcctUserFinder(),
                "mailto": MailUserFinder(),
            }
        self.lookups = lookups

    @override
    async def afind_resource(self, uri: str) -> AbstractUser:
        parsed: ParseResult = urlparse(uri)
        try:
            finder = self.lookups[parsed.scheme]
        except KeyError as exc:
            msg = "Invalid scheme"
            raise ValueError(msg) from exc
        else:
            return await finder.afind_resource(uri)
