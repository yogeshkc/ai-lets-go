import requests
from typing import Dict

def get_available_currencies() -> Dict[str, str]:
    """Get list of available currencies and their names from the API"""
    try:
        response = requests.get("https://open.er-api.com/v6/latest")
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {})
    except Exception as e:
        raise ValueError(f"Failed to get available currencies: {str(e)}")

def exchange_rate(base_currency: str, quote_currency: str) -> float:
    """Get live exchange rate between any two currencies using ExchangeRate-API
    
    Args:
        base_currency: The currency to convert from (e.g., 'USD', 'EUR', 'GBP')
        quote_currency: The currency to convert to (e.g., 'JPY', 'INR', 'AUD')
    
    Returns:
        float: The exchange rate (1 base_currency = X quote_currency)
        
    Raises:
        ValueError: If currencies are invalid or API request fails
    """
    base_currency = base_currency.upper()
    quote_currency = quote_currency.upper()
    
    if base_currency == quote_currency:
        return 1.0
    
    try:
        # Using ExchangeRate-API's free endpoint
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data.get("result") == "success":
            if quote_currency not in data["rates"]:
                raise ValueError(f"Invalid quote currency: {quote_currency}")
            return data["rates"][quote_currency]
        else:
            if "error" in data and "Invalid Base Currency" in data["error"]:
                raise ValueError(f"Invalid base currency: {base_currency}")
            raise ValueError(f"API returned error: {data}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"API request failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to get exchange rate: {str(e)}")
