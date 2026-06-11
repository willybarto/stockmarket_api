from rest_framework import serializers
from .models import Asset, HistoricalPrice, Portfolio, PortfolioItem


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ["id", "symbol", "name", "sector", "description", "is_active"]


class HistoricalPriceSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)

    class Meta:
        model = HistoricalPrice
        fields = [
            "id",
            "asset",
            "asset_symbol",
            "date",
            "open_price",
            "close_price",
            "high_price",
            "low_price",
            "volume",
        ]


class PortfolioItemSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)
    asset_name = serializers.CharField(source="asset.name", read_only=True)

    class Meta:
        model = PortfolioItem
        fields = [
            "id",
            "asset",
            "asset_symbol",
            "asset_name",
            "quantity",
            "average_buy_price",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantità deve essere maggiore di zero.")
        return value

    def validate_average_buy_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Il prezzo medio di acquisto deve essere maggiore di zero.")
        return value


class PortfolioSerializer(serializers.ModelSerializer):
    items = PortfolioItemSerializer(many=True, read_only=True)
    owner = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Portfolio
        fields = ["id", "name", "owner", "created_at", "updated_at", "items"]

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Il nome del portfolio deve avere almeno 3 caratteri.")
        return value.strip()


class PortfolioCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["id", "name"]

    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Il nome del portfolio deve avere almeno 3 caratteri.")
        return value.strip()