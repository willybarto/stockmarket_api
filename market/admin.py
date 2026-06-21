from django.contrib import admin
from .models import Asset, HistoricalPrice, Portfolio, PortfolioItem, QuoteRequestLog, Watchlist


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "sector", "is_active")
    search_fields = ("symbol", "name")


@admin.register(HistoricalPrice)
class HistoricalPriceAdmin(admin.ModelAdmin):
    list_display = ("asset", "date", "open_price", "close_price", "volume")
    list_filter = ("asset", "date")


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("portfolio", "asset", "quantity", "average_buy_price")


@admin.register(QuoteRequestLog)
class QuoteRequestLogAdmin(admin.ModelAdmin):
    list_display = ("user", "request_date", "count")


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "asset", "added_at")
