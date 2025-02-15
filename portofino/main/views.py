from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SimpleUserRegisterForm
import requests
from .models import PortfolioItem
from .utils import get_cached_coin_data, get_cached_search_results
from django.http import JsonResponse
from decimal import Decimal

def home(request):
    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = SimpleUserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Fiók létrehozva: {username}!')
            return redirect('login')
    else:
        form = SimpleUserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

@login_required
def crypto_details(request, coin_id):
    coin_data = get_cached_coin_data(coin_id)
    if coin_data:
        is_in_portfolio = PortfolioItem.objects.filter(
            user=request.user,
            coin_id=coin_id
        ).exists()

        context = {
            'coin': coin_data,
            'is_in_portfolio': is_in_portfolio
        }
        return render(request, 'main/crypto_details.html', context)
    else:
        messages.error(request, 'Nem sikerült betölteni a kriptovaluta adatait.')
        return redirect('home')

@login_required
def add_to_portfolio(request, coin_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if not quantity:
            messages.error(request, "Kérlek adj meg egy mennyiséget!")
            return redirect('crypto_details', coin_id=coin_id)
            
        try:
            quantity = float(quantity)
        except ValueError:
            messages.error(request, "Érvénytelen mennyiség!")
            return redirect('crypto_details', coin_id=coin_id)

        response = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}')
        if response.status_code == 200:
            coin_data = response.json()
            PortfolioItem.objects.get_or_create(
                user=request.user,
                coin_id=coin_id,
                defaults={
                    'coin_symbol': coin_data['symbol'],
                    'coin_name': coin_data['name'],
                    'quantity': quantity
                }
            )
            messages.success(request, f"{coin_data['name']} hozzáadva a portfolióhoz!")
        return redirect('crypto_details', coin_id=coin_id)

@login_required
def update_portfolio_quantity(request, coin_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        try:
            quantity = float(quantity)
            portfolio_item = PortfolioItem.objects.get(user=request.user, coin_id=coin_id)
            portfolio_item.quantity = quantity
            portfolio_item.save()
            messages.success(request, "Mennyiség sikeresen frissítve!")
        except (ValueError, PortfolioItem.DoesNotExist):
            messages.error(request, "Hiba történt a mennyiség frissítésekor!")
    return redirect('portfolio')

@login_required
def portfolio(request):
    portfolio_items = PortfolioItem.objects.filter(user=request.user)
    portfolio_data = []
    
    for item in portfolio_items:
        coin_data = get_cached_coin_data(item.coin_id)
        if coin_data:
            current_price = Decimal(str(coin_data['market_data']['current_price']['usd']))
            portfolio_data.append({
                'item': item,
                'coin': coin_data,
                'total_value': item.quantity * current_price
            })
    
    return render(request, 'main/portfolio.html', {
        'portfolio_data': portfolio_data,
        'total_portfolio_value': sum(data['total_value'] for data in portfolio_data)
    })

@login_required
def remove_from_portfolio(request, coin_id):
    if request.method == 'POST':
        PortfolioItem.objects.filter(user=request.user, coin_id=coin_id).delete()
        messages.success(request, "Token eltávolítva a portfolióból!")
    return redirect('portfolio')

def api_search(request):
    query = request.GET.get('query', '')
    if len(query) < 2:
        return JsonResponse({'coins': []})
    
    search_results = get_cached_search_results(query)
    return JsonResponse(search_results if search_results else {'coins': []})
