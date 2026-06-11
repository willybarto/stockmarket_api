from django.urls import path
from .views import (
    AssetListView,
    AssetDetailView,
    AssetQuoteView,
    AssetHistoryView,
    PortfolioListCreateView,
    PortfolioDetailView,
    PortfolioItemCreateView,
    PortfolioItemDetailView,
    PortfolioValuationView,
)

urlpatterns = [
    path("assets/", AssetListView.as_view(), name="asset-list"),
    path("assets/<int:pk>/", AssetDetailView.as_view(), name="asset-detail"),
    path("assets/<int:pk>/quote/", AssetQuoteView.as_view(), name="asset-quote"),
    path("assets/<int:pk>/history/", AssetHistoryView.as_view(), name="asset-history"),

    path("portfolios/", PortfolioListCreateView.as_view(), name="portfolio-list-create"),
    path("portfolios/<int:pk>/", PortfolioDetailView.as_view(), name="portfolio-detail"),
    path("portfolios/<int:portfolio_id>/items/", PortfolioItemCreateView.as_view(), name="portfolio-item-create"),
    path("portfolio-items/<int:pk>/", PortfolioItemDetailView.as_view(), name="portfolio-item-detail"),
    path("portfolios/<int:pk>/valuation/", PortfolioValuationView.as_view(), name="portfolio-valuation"),
]