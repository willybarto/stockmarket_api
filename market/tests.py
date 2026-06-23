from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from market.models import Asset, HistoricalPrice, Portfolio, PortfolioItem, Watchlist

User = get_user_model()


class AssetTests(APITestCase):

    def setUp(self):
        self.asset = Asset.objects.create(
            symbol="TEST", name="Test Inc.", sector="Tech", is_active=True
        )
        Asset.objects.create(
            symbol="DEAD", name="Dead Corp.", sector="Other", is_active=False
        )

    def test_asset_list(self):
        response = self.client.get("/api/assets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        symbols = [a["symbol"] for a in response.data["results"]]
        self.assertIn("TEST", symbols)
        self.assertNotIn("DEAD", symbols)

    def test_asset_detail(self):
        response = self.client.get(f"/api/assets/{self.asset.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "TEST")

    def test_asset_detail_not_found(self):
        response = self.client.get("/api/assets/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class QuoteTests(APITestCase):

    def setUp(self):
        self.basic_user = User.objects.create_user(
            username="basic", password="pass12345678", role="basic"
        )
        self.asset = Asset.objects.create(
            symbol="AAPL", name="Apple", sector="Tech", is_active=True
        )
        HistoricalPrice.objects.create(
            asset=self.asset,
            date=date.today(),
            open_price=Decimal("150.00"),
            close_price=Decimal("152.00"),
            high_price=Decimal("155.00"),
            low_price=Decimal("148.00"),
            volume=1000000,
        )

    def test_quote_unauthenticated(self):
        response = self.client.get(f"/api/assets/{self.asset.id}/quote/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_quote_authenticated(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get(f"/api/assets/{self.asset.id}/quote/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "AAPL")
        self.assertEqual(response.data["daily_limit"], 10)
        self.assertEqual(response.data["role"], "basic")

    def test_quote_asset_not_found(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get("/api/assets/9999/quote/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class HistoryTests(APITestCase):

    def setUp(self):
        self.basic_user = User.objects.create_user(
            username="basic", password="pass12345678", role="basic"
        )
        self.pro_user = User.objects.create_user(
            username="pro", password="pass12345678", role="pro"
        )
        self.asset = Asset.objects.create(
            symbol="AAPL", name="Apple", sector="Tech", is_active=True
        )
        for i in range(60):
            HistoricalPrice.objects.create(
                asset=self.asset,
                date=date.today() - timedelta(days=i),
                open_price=Decimal("150.00") + Decimal(str(i)),
                close_price=Decimal("152.00") + Decimal(str(i)),
                high_price=Decimal("155.00") + Decimal(str(i)),
                low_price=Decimal("148.00") + Decimal(str(i)),
                volume=1000000,
            )

    def test_history_basic_30_days(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get(
            f"/api/assets/{self.asset.id}/history/?days=30"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["results"]), 30)

    def test_history_basic_365_forbidden(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get(
            f"/api/assets/{self.asset.id}/history/?days=365"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_history_pro_365_allowed(self):
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get(
            f"/api/assets/{self.asset.id}/history/?days=60"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_history_date_range(self):
        self.client.force_authenticate(user=self.basic_user)
        date_from = (date.today() - timedelta(days=10)).isoformat()
        date_to = date.today().isoformat()
        response = self.client.get(
            f"/api/assets/{self.asset.id}/history/?date_from={date_from}&date_to={date_to}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(response.data["count"], 11)
        self.assertIn("results", response.data)

    def test_history_invalid_date_format(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get(
            f"/api/assets/{self.asset.id}/history/?date_from=invalid"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_history_invalid_days(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get(
            f"/api/assets/{self.asset.id}/history/?days=abc"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_history_interval_weekly(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get(
            f"/api/assets/{self.asset.id}/history/?days=30&interval=weekly"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response.data["count"], 30)
        self.assertIn("next", response.data)


class PortfolioCRUDTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="owner", password="pass12345678", role="basic"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass12345678", role="basic"
        )
        self.asset = Asset.objects.create(
            symbol="AAPL", name="Apple", sector="Tech", is_active=True
        )
        HistoricalPrice.objects.create(
            asset=self.asset,
            date=date.today(),
            open_price=Decimal("150.00"),
            close_price=Decimal("152.00"),
            high_price=Decimal("155.00"),
            low_price=Decimal("148.00"),
            volume=1000000,
        )

    def test_create_portfolio(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/portfolios/", {"name": "My Portfolio"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_portfolio_short_name(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/portfolios/", {"name": "AB"}, format="json"
        )
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST])

    def test_list_own_portfolios(self):
        Portfolio.objects.create(user=self.user, name="My Portfolio")
        Portfolio.objects.create(user=self.other_user, name="Other Portfolio")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/portfolios/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "My Portfolio")

    def test_update_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user, name="Old Name")
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/portfolios/{portfolio.id}/",
            {"name": "New Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user, name="To Delete")
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/portfolios/{portfolio.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_access_other_user_portfolio(self):
        other_portfolio = Portfolio.objects.create(
            user=self.other_user, name="Not Mine"
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/portfolios/{other_portfolio.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_item_to_portfolio(self):
        portfolio = Portfolio.objects.create(user=self.user, name="My Portfolio")
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/portfolios/{portfolio.id}/items/",
            {"asset": self.asset.id, "quantity": 10, "average_buy_price": "100.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_portfolio_valuation(self):
        portfolio = Portfolio.objects.create(user=self.user, name="My Portfolio")
        PortfolioItem.objects.create(
            portfolio=portfolio,
            asset=self.asset,
            quantity=10,
            average_buy_price=Decimal("100.00"),
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/portfolios/{portfolio.id}/valuation/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_value", response.data)
        self.assertIn("total_gain_loss", response.data)
        self.assertIn("total_gain_loss_percent", response.data)
        self.assertGreater(float(response.data["total_gain_loss"]), 0)


class WatchlistTests(APITestCase):

    def setUp(self):
        self.basic_user = User.objects.create_user(
            username="basic", password="pass12345678", role="basic"
        )
        self.pro_user = User.objects.create_user(
            username="pro", password="pass12345678", role="pro"
        )
        self.asset = Asset.objects.create(
            symbol="AAPL", name="Apple", sector="Tech", is_active=True
        )

    def test_watchlist_basic_forbidden(self):
        self.client.force_authenticate(user=self.basic_user)
        response = self.client.get("/api/watchlist/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_watchlist_pro_add(self):
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.post(
            "/api/watchlist/", {"asset": self.asset.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["asset_symbol"], "AAPL")

    def test_watchlist_pro_list(self):
        Watchlist.objects.create(user=self.pro_user, asset=self.asset)
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.get("/api/watchlist/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_watchlist_pro_delete(self):
        wl = Watchlist.objects.create(user=self.pro_user, asset=self.asset)
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.delete(f"/api/watchlist/{wl.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_watchlist_unauthenticated(self):
        response = self.client.get("/api/watchlist/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_duplicate(self):
        Watchlist.objects.create(user=self.pro_user, asset=self.asset)
        self.client.force_authenticate(user=self.pro_user)
        response = self.client.post(
            "/api/watchlist/", {"asset": self.asset.id}, format="json"
        )
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST])
