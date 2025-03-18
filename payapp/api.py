from django.http import JsonResponse, HttpResponseBadRequest
from decimal import Decimal

def conversion_view(request, currency1, currency2, amount):
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
        return HttpResponseBadRequest('Unsupported currency')
    
    # 如果货币相同，无需转换
    if currency1 == currency2:
        return JsonResponse({
            'from_currency': currency1,
            'to_currency': currency2,
            'from_amount': amount,
            'converted_amount': amount,
            'exchange_rate': 1.0
        })
    
    # 获取汇率
    rate_key = f"{currency1}_{currency2}"
    if rate_key not in exchange_rates:
        return HttpResponseBadRequest('Exchange rate not available')
    
    rate = exchange_rates[rate_key]
    converted_amount = Decimal(amount) * rate
    
    return JsonResponse({
        'from_currency': currency1,
        'to_currency': currency2,
        'from_amount': amount,
        'converted_amount': str(converted_amount),
        'exchange_rate': str(rate)
    }) 