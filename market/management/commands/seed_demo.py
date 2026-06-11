import random
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from market.models import Asset, HistoricalPrice, Portfolio, PortfolioItem

User = get_user_model()


class Command(BaseCommand):
    help = "Popola il database con dati demo per la Stock Market API"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creazione utenti demo...")

        admin_user, _ = User.objects.get_or_create(
            username="admin_demo",
            defaults={
                "email": "admin@example.com",
                "role": "pro",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        admin_user.set_password("admin12345")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.role = "pro"
        admin_user.save()

        basic_user, _ = User.objects.get_or_create(
            username="basic_demo",
            defaults={
                "email": "basic@example.com",
                "role": "basic",
            }
        )
        basic_user.set_password("basic12345")
        basic_user.role = "basic"
        basic_user.save()

        pro_user, _ = User.objects.get_or_create(
            username="pro_demo",
            defaults={
                "email": "pro@example.com",
                "role": "pro",
            }
        )
        pro_user.set_password("pro12345")
        pro_user.role = "pro"
        pro_user.save()

        self.stdout.write("Creazione asset demo...")

        assets_data = [
            ("AAPL", "Apple Inc.", "Technology"),
            ("GOOGL", "Alphabet Inc.", "Technology"),
            ("MSFT", "Microsoft Corp.", "Technology"),
            ("TSLA", "Tesla Inc.", "Automotive"),
            ("AMZN", "Amazon.com Inc.", "E-commerce"),
        ]

        assets = []
        for symbol, name, sector in assets_data:
            asset, _ = Asset.objects.get_or_create(
                symbol=symbol,
                defaults={
                    "name": name,
                    "sector": sector,
                    "description": f"{name} demo asset for stock market API project.",
                    "is_active": True,
                }
            )
            assets.append(asset)

        self.stdout.write("Creazione storico prezzi demo...")

        for asset in assets:
            HistoricalPrice.objects.filter(asset=asset).delete()

            base_price = Decimal(str(random.randint(80, 300)))
            for i in range(365):
                current_date = date.today() - timedelta(days=i)
                variation = Decimal(str(random.uniform(-5, 5))).quantize(Decimal("0.01"))
                open_price = (base_price + variation).quantize(Decimal("0.01"))
                close_price = (open_price + Decimal(str(random.uniform(-3, 3)))).quantize(Decimal("0.01"))
                high_price = max(open_price, close_price) + Decimal("1.50")
                low_price = min(open_price, close_price) - Decimal("1.50")
                volume = random.randint(100000, 5000000)

                HistoricalPrice.objects.create(
                    asset=asset,
                    date=current_date,
                    open_price=open_price,
                    close_price=close_price,
                    high_price=high_price,
                    low_price=low_price,
                    volume=volume,
                )

        self.stdout.write("Creazione portfolio demo...")

        portfolio_basic, _ = Portfolio.objects.get_or_create(
            user=basic_user,
            name="Basic Growth Portfolio"
        )
        portfolio_pro, _ = Portfolio.objects.get_or_create(
            user=pro_user,
            name="Pro Diversified Portfolio"
        )

        PortfolioItem.objects.get_or_create(
            portfolio=portfolio_basic,
            asset=assets[0],
            defaults={"quantity": 5, "average_buy_price": Decimal("150.00")}
        )
        PortfolioItem.objects.get_or_create(
            portfolio=portfolio_basic,
            asset=assets[2],
            defaults={"quantity": 3, "average_buy_price": Decimal("280.00")}
        )

        PortfolioItem.objects.get_or_create(
            portfolio=portfolio_pro,
            asset=assets[1],
            defaults={"quantity": 7, "average_buy_price": Decimal("120.00")}
        )
        PortfolioItem.objects.get_or_create(
            portfolio=portfolio_pro,
            asset=assets[3],
            defaults={"quantity": 4, "average_buy_price": Decimal("210.00")}
        )
        PortfolioItem.objects.get_or_create(
            portfolio=portfolio_pro,
            asset=assets[4],
            defaults={"quantity": 2, "average_buy_price": Decimal("130.00")}
        )

        self.stdout.write(self.style.SUCCESS("Seed demo completato con successo."))