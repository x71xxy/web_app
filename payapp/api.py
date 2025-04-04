from django.http import JsonResponse, HttpResponseBadRequest
from decimal import Decimal
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["GET"])
def conversion_view(request, currency1, currency2, amount):
    """
    RESTful API endpoint for currency conversion.
    
    Args:
        currency1 (str): Source currency code (GBP, USD, EUR)
        currency2 (str): Target currency code (GBP, USD, EUR)
        amount (str): Amount to convert
        
    Returns:
        JsonResponse with conversion details or HttpResponseBadRequest if invalid
    """
    # 硬编码汇率
    exchange_rates = {
        'GBP_USD': Decimal('1.30'),
        'GBP_EUR': Decimal('1.17'),
        'USD_GBP': Decimal('0.77'),
        'USD_EUR': Decimal('0.90'),
        'EUR_GBP': Decimal('0.85'),
        'EUR_USD': Decimal('1.11')
    }
    
    # 检查货币是否支持
    supported_currencies = ['GBP', 'USD', 'EUR']
    if currency1 not in supported_currencies or currency2 not in supported_currencies:
        return HttpResponseBadRequest('Unsupported currency. Must be one of: GBP, USD, EUR')
    
    try:
        amount_decimal = Decimal(amount)
        if amount_decimal <= 0:
            return HttpResponseBadRequest('Amount must be positive')
    except (ValueError, decimal.InvalidOperation):
        return HttpResponseBadRequest('Invalid amount format')
    
    # 如果货币相同，无需转换
    if currency1 == currency2:
        return JsonResponse({
            'from_currency': currency1,
            'to_currency': currency2,
            'from_amount': str(amount_decimal),
            'converted_amount': str(amount_decimal),
            'exchange_rate': '1.0'
        })
    
    # 获取汇率
    rate_key = f"{currency1}_{currency2}"
    if rate_key not in exchange_rates:
        return HttpResponseBadRequest('Exchange rate not available for the specified currency pair')
    
    rate = exchange_rates[rate_key]
    converted_amount = amount_decimal * rate
    
    return JsonResponse({
        'from_currency': currency1,
        'to_currency': currency2,
        'from_amount': str(amount_decimal),
        'converted_amount': str(converted_amount.quantize(Decimal('0.01'))),
        'exchange_rate': str(rate)
    }) 