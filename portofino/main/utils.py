from django.core.cache import cache
from django.conf import settings
import requests
import json

def get_cached_coin_data(coin_id):
    """Get coin data from cache or API"""
    cache_key = f'coin_data_{coin_id}'
    coin_data = cache.get(cache_key)
    
    if coin_data is None:
        response = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}')
        if response.status_code == 200:
            coin_data = response.json()
            cache.set(cache_key, json.dumps(coin_data), timeout=settings.CACHE_TTL)
        else:
            return None
    else:
        coin_data = json.loads(coin_data)
    
    return coin_data

def get_cached_search_results(query):
    """Get search results from cache or API"""
    cache_key = f'search_results_{query}'
    search_results = cache.get(cache_key)
    
    if search_results is None:
        response = requests.get(f'https://api.coingecko.com/api/v3/search?query={query}')
        if response.status_code == 200:
            search_results = response.json()
            cache.set(cache_key, json.dumps(search_results), timeout=settings.CACHE_TTL)
        else:
            return None
    else:
        search_results = json.loads(search_results)
    
    return search_results 