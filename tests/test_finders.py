import pytest
from django.contrib.auth import get_user_model

from django_webfinger.finders import AcctUserFinder, MailUserFinder, SchemeUserFinder

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: ARG001
    user_model = get_user_model()

    with django_db_blocker.unblock():
        user_model.objects.create_user("bob", email="bob@example.com")


@pytest.mark.asyncio
class TestAcctUserFinder:
    async def test_with_invalid_scheme(self):
        finder = AcctUserFinder()

        with pytest.raises(ValueError, match="Invalid scheme"):
            await finder.afind_resource("mailto:user@example.com")

    async def test_with_invalid_uri(self):
        finder = AcctUserFinder()

        with pytest.raises(ValueError, match="Invalid account"):
            await finder.afind_resource("acct:bob")

    async def test_with_missing_user(self):
        finder = AcctUserFinder()

        got = await finder.afind_resource("acct:mike@example.com")

        assert got is None

    async def test_with_existing_user(self):
        finder = AcctUserFinder()

        got = await finder.afind_resource("acct:bob@example.com")

        assert got.get_username() == "bob"


@pytest.mark.asyncio
class TestMailUserFinder:
    async def test_with_invalid_scheme(self):
        finder = MailUserFinder()

        with pytest.raises(ValueError, match="Invalid scheme"):
            await finder.afind_resource("acct:user@example.com")

    async def test_with_missing_user(self):
        finder = MailUserFinder()

        got = await finder.afind_resource("mailto:mike@example.com")

        assert got is None

    async def test_with_existing_user(self):
        finder = MailUserFinder()

        got = await finder.afind_resource("mailto:bob@example.com")

        assert getattr(got, got.get_email_field_name()) == "bob@example.com"


@pytest.mark.asyncio
class TestSchemeUserFinder:
    async def test_with_invalid_scheme(self):
        finder = SchemeUserFinder()

        with pytest.raises(ValueError, match="Invalid scheme"):
            await finder.afind_resource("https://example.com")

    async def test_with_missing_user(self):
        finder = SchemeUserFinder()

        got = await finder.afind_resource("mailto:mike@example.com")

        assert got is None

    @pytest.mark.parametrize("scheme", ["acct", "mailto"])
    async def test_with_existing_user(self, scheme):
        finder = SchemeUserFinder()

        got = await finder.afind_resource(f"{scheme}:bob@example.com")

        assert got.get_username() == "bob"
