from rest_framework import serializers

class CurrencyConversionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    from_currency = serializers.ChoiceField(choices=[('GBP', 'GB Pounds'), ('USD', 'US Dollars'), ('EUR', 'Euros')])
    to_currency = serializers.ChoiceField(choices=[('GBP', 'GB Pounds'), ('USD', 'US Dollars'), ('EUR', 'Euros')])