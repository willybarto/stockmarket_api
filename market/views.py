from datetime import datetime, timedelta

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Asset, Portfolio, PortfolioItem, HistoricalPrice, Watchlist
from .serializers import (
    AssetSerializer,
    HistoricalPriceSerializer,
    PortfolioSerializer,
    PortfolioCreateUpdateSerializer,
    PortfolioItemSerializer,
    WatchlistSerializer,
)
from .permissions import IsOwner, IsProUser
from .throttles import RoleBasedDailyQuoteThrottle
from .services import (
    register_quote_request,
    get_latest_quote,
    get_history_limit,
    calculate_portfolio_value,
)


class AssetListView(generics.ListAPIView):
    queryset = Asset.objects.filter(is_active=True)
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny]


class AssetDetailView(generics.RetrieveAPIView):
    queryset = Asset.objects.filter(is_active=True)
    serializer_class = AssetSerializer
    permission_classes = [permissions.AllowAny]


class AssetQuoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [RoleBasedDailyQuoteThrottle]

    def get(self, request, pk):
        try:
            asset = Asset.objects.get(pk=pk, is_active=True)
        except Asset.DoesNotExist:
            return Response(
                {"detail": "Asset non trovato."},
                status=status.HTTP_404_NOT_FOUND,
            )

        allowed, limit, current_count = register_quote_request(request.user)

        latest_price = get_latest_quote(asset)
        if not latest_price:
            return Response(
                {"detail": "Nessuna quotazione disponibile per questo asset."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            "asset_id": asset.id,
            "symbol": asset.symbol,
            "name": asset.name,
            "date": latest_price.date,
            "open_price": latest_price.open_price,
            "close_price": latest_price.close_price,
            "high_price": latest_price.high_price,
            "low_price": latest_price.low_price,
            "volume": latest_price.volume,
            "requests_today": current_count,
            "daily_limit": limit,
            "role": request.user.role,
        })


class AssetHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            asset = Asset.objects.get(pk=pk, is_active=True)
        except Asset.DoesNotExist:
            return Response(
                {"detail": "Asset non trovato."},
                status=status.HTTP_404_NOT_FOUND,
            )

        max_days = get_history_limit(request.user)

        date_from_str = request.query_params.get("date_from")
        date_to_str = request.query_params.get("date_to")

        if date_from_str or date_to_str:
            try:
                date_from = (
                    datetime.strptime(date_from_str, "%Y-%m-%d").date()
                    if date_from_str
                    else None
                )
                date_to = (
                    datetime.strptime(date_to_str, "%Y-%m-%d").date()
                    if date_to_str
                    else None
                )
            except ValueError:
                return Response(
                    {"detail": "Formato data non valido. Usare YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if date_from and date_to and date_from > date_to:
                return Response(
                    {"detail": "date_from deve essere anteriore o uguale a date_to."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if date_from and date_to:
                delta = (date_to - date_from).days
                if delta > max_days:
                    return Response(
                        {
                            "detail": "Intervallo storico non consentito per questo ruolo.",
                            "requested_days": delta,
                            "max_allowed_days": max_days,
                            "role": request.user.role,
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            queryset = asset.historical_prices.all()
            if date_from:
                queryset = queryset.filter(date__gte=date_from)
            if date_to:
                queryset = queryset.filter(date__lte=date_to)
            queryset = queryset.order_by("-date")

        else:
            try:
                requested_days = int(request.query_params.get("days", 30))
            except ValueError:
                return Response(
                    {"detail": "Il parametro 'days' deve essere un intero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if requested_days <= 0:
                return Response(
                    {"detail": "Il parametro 'days' deve essere maggiore di zero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if requested_days > max_days:
                return Response(
                    {
                        "detail": "Intervallo storico non consentito per questo ruolo.",
                        "requested_days": requested_days,
                        "max_allowed_days": max_days,
                        "role": request.user.role,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            queryset = asset.historical_prices.all().order_by("-date")[:requested_days]

        interval = request.query_params.get("interval", "daily")
        if interval not in ("daily", "weekly", "monthly"):
            return Response(
                {"detail": "Il parametro 'interval' deve essere 'daily', 'weekly' o 'monthly'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = list(queryset)

        if interval == "weekly":
            results = _sample_by_interval(results, 7)
        elif interval == "monthly":
            results = _sample_by_interval(results, 30)

        serializer = HistoricalPriceSerializer(results, many=True)

        return Response({
            "asset_id": asset.id,
            "symbol": asset.symbol,
            "role": request.user.role,
            "max_allowed_days": max_days,
            "interval": interval,
            "count": len(serializer.data),
            "results": serializer.data,
        })


def _sample_by_interval(prices, interval_days):
    if not prices:
        return prices
    sampled = [prices[0]]
    last_date = prices[0].date
    for price in prices[1:]:
        if (last_date - price.date).days >= interval_days:
            sampled.append(price)
            last_date = price.date
    return sampled


class PortfolioListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PortfolioCreateUpdateSerializer
        return PortfolioSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PortfolioCreateUpdateSerializer
        return PortfolioSerializer


class PortfolioItemCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        except Portfolio.DoesNotExist:
            return Response(
                {"detail": "Portfolio non trovato."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PortfolioItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PortfolioItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return PortfolioItem.objects.filter(portfolio__user=self.request.user)


class PortfolioValuationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            portfolio = Portfolio.objects.get(pk=pk, user=request.user)
        except Portfolio.DoesNotExist:
            return Response(
                {"detail": "Portfolio non trovato."},
                status=status.HTTP_404_NOT_FOUND,
            )

        valuation = calculate_portfolio_value(portfolio)
        return Response(valuation)


class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsProUser]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related("asset")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WatchlistDeleteView(generics.DestroyAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsProUser]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)