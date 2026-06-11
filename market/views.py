from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Asset, Portfolio, PortfolioItem, HistoricalPrice
from .serializers import (
    AssetSerializer,
    HistoricalPriceSerializer,
    PortfolioSerializer,
    PortfolioCreateUpdateSerializer,
    PortfolioItemSerializer,
)
from .permissions import IsOwner
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

    def get(self, request, pk):
        try:
            asset = Asset.objects.get(pk=pk, is_active=True)
        except Asset.DoesNotExist:
            return Response({"detail": "Asset non trovato."}, status=status.HTTP_404_NOT_FOUND)

        allowed, limit, current_count = register_quote_request(request.user)
        if not allowed:
            return Response(
                {
                    "detail": "Limite giornaliero quote superato.",
                    "daily_limit": limit,
                    "requests_today": current_count,
                    "role": request.user.role,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        latest_price = get_latest_quote(asset)
        if not latest_price:
            return Response({"detail": "Nessuna quotazione disponibile per questo asset."},
                            status=status.HTTP_404_NOT_FOUND)

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
            return Response({"detail": "Asset non trovato."}, status=status.HTTP_404_NOT_FOUND)

        try:
            requested_days = int(request.query_params.get("days", 30))
        except ValueError:
            return Response({"detail": "Il parametro 'days' deve essere un intero."},
                            status=status.HTTP_400_BAD_REQUEST)

        if requested_days <= 0:
            return Response({"detail": "Il parametro 'days' deve essere maggiore di zero."},
                            status=status.HTTP_400_BAD_REQUEST)

        max_days = get_history_limit(request.user)
        if requested_days > max_days:
            return Response(
                {
                    "detail": "Intervallo storico non consentito per questo ruolo.",
                    "requested_days": requested_days,
                    "max_allowed_days": max_days,
                    "role": request.user.role,
                },
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = asset.historical_prices.all().order_by("-date")[:requested_days]
        serializer = HistoricalPriceSerializer(queryset, many=True)

        return Response({
            "asset_id": asset.id,
            "symbol": asset.symbol,
            "role": request.user.role,
            "requested_days": requested_days,
            "max_allowed_days": max_days,
            "results": serializer.data,
        })


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
                status=status.HTTP_404_NOT_FOUND
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
            return Response({"detail": "Portfolio non trovato."}, status=status.HTTP_404_NOT_FOUND)

        valuation = calculate_portfolio_value(portfolio)
        return Response(valuation)