import random
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from market.models import Asset, HistoricalPrice


class Command(BaseCommand):
    help = (
        "Genera variazioni di prezzo simulate per tutti gli asset attivi. "
        "Di default genera il prezzo per la data odierna; con --days N genera "
        "le ultime N giornate mancanti."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Numero di giorni da generare a partire da oggi indietro (default: 1).",
        )

    def handle(self, *args, **options):
        days = options["days"]
        assets = Asset.objects.filter(is_active=True)

        if not assets.exists():
            self.stdout.write(self.style.WARNING("Nessun asset attivo trovato."))
            return

        total_created = 0

        for asset in assets:
            self.stdout.write(f"  Asset {asset.symbol}...")

            for i in range(days):
                target_date = date.today() - timedelta(days=i)

                # Salta se il prezzo per questa data esiste già
                if HistoricalPrice.objects.filter(asset=asset, date=target_date).exists():
                    continue

                # Trova l'ultimo prezzo precedente come base
                previous = (
                    HistoricalPrice.objects.filter(asset=asset, date__lt=target_date)
                    .order_by("-date")
                    .first()
                )

                if previous:
                    base_price = previous.close_price
                else:
                    # Nessun prezzo precedente: genera un prezzo iniziale random
                    base_price = Decimal(str(random.randint(50, 500)))

                # Random walk: variazione giornaliera tra -3% e +3%
                pct_change = Decimal(str(random.uniform(-0.03, 0.03)))
                open_price = (base_price * (1 + pct_change)).quantize(Decimal("0.01"))

                # Variazione intraday
                intraday_pct = Decimal(str(random.uniform(-0.02, 0.02)))
                close_price = (open_price * (1 + intraday_pct)).quantize(Decimal("0.01"))

                high_price = max(open_price, close_price) + Decimal(
                    str(random.uniform(0.5, 3.0))
                ).quantize(Decimal("0.01"))
                low_price = min(open_price, close_price) - Decimal(
                    str(random.uniform(0.5, 3.0))
                ).quantize(Decimal("0.01"))

                volume = random.randint(100_000, 10_000_000)

                HistoricalPrice.objects.create(
                    asset=asset,
                    date=target_date,
                    open_price=open_price,
                    close_price=close_price,
                    high_price=high_price,
                    low_price=low_price,
                    volume=volume,
                )
                total_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Simulazione completata: {total_created} prezzi generati per {assets.count()} asset."
            )
        )
