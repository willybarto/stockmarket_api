from datetime import date
from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper

from .models import HistoricalPrice, QuoteRequestLog


def get_daily_quote_limit(user):
    if user.role == "pro":
        return 100
    return 10


def get_history_limit(user):
    if user.role == "pro":
        return 365
    return 30


def register_quote_request(user):
    today = date.today()
    log, created = QuoteRequestLog.objects.get_or_create(
        user=user,
        request_date=today,
        defaults={"count": 0}
    )
    limit = get_daily_quote_limit(user)

    if log.count >= limit:
        return False, limit, log.count

    log.count += 1
    log.save()
    return True, limit, log.count


def get_latest_quote(asset):
    latest_price = asset.historical_prices.order_by("-date").first()
    if not latest_price:
        return None
    return latest_price


def calculate_portfolio_value(portfolio):
    items = portfolio.items.select_related("asset")
    total_value = Decimal("0.00")
    breakdown = []

    for item in items:
        latest_price = item.asset.historical_prices.order_by("-date").first()
        current_price = latest_price.close_price if latest_price else Decimal("0.00")
        item_value = current_price * item.quantity
        total_value += item_value

        breakdown.append({
            "asset_id": item.asset.id,
            "symbol": item.asset.symbol,
            "name": item.asset.name,
            "quantity": item.quantity,
            "average_buy_price": item.average_buy_price,
            "current_price": current_price,
            "market_value": item_value,
        })

    return {
        "portfolio_id": portfolio.id,
        "portfolio_name": portfolio.name,
        "owner": portfolio.user.username,
        "total_value": total_value,
        "items": breakdown,
    }