from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SimpleUserRegisterForm, UserProfileForm, CustomPasswordChangeForm
import requests
from .models import PortfolioItem, FriendRequest, Friendship, UserProfile
from .utils import get_cached_coin_data, get_cached_search_results
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash

def home(request):
    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = SimpleUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
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
        purchase_price = request.POST.get('purchase_price')
        
        if not quantity or not purchase_price:
            messages.error(request, "Kérlek add meg a mennyiséget és a vásárlási árat!")
            return redirect('crypto_details', coin_id=coin_id)
            
        try:
            quantity = float(quantity)
            purchase_price = float(purchase_price)
        except ValueError:
            messages.error(request, "Érvénytelen mennyiség vagy ár!")
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
                    'quantity': quantity,
                    'purchase_price': purchase_price
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
    total_investment = Decimal('0')
    total_current_value = Decimal('0')
    
    for item in portfolio_items:
        coin_data = get_cached_coin_data(item.coin_id)
        if coin_data:
            current_price = Decimal(str(coin_data['market_data']['current_price']['usd']))
            profit_percentage = item.get_profit_percentage(current_price)
            
            # Calculate investment and current value for this item
            investment = item.quantity * item.purchase_price
            current_value = item.quantity * current_price
            
            total_investment += investment
            total_current_value += current_value
            
            portfolio_data.append({
                'item': item,
                'coin': coin_data,
                'total_value': current_value,
                'profit_percentage': profit_percentage
            })
    
    # Calculate total portfolio profit/loss percentage
    total_profit_percentage = 0
    if total_investment > 0:
        total_profit_percentage = ((total_current_value - total_investment) / total_investment) * 100
    
    return render(request, 'main/portfolio.html', {
        'portfolio_data': portfolio_data,
        'total_portfolio_value': total_current_value,
        'total_investment': total_investment,
        'total_profit_percentage': total_profit_percentage
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

@login_required
def friends_list(request):
    # Get all friendships
    friendships = Friendship.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )
    
    friends = []
    for friendship in friendships:
        if friendship.user1 == request.user:
            friends.append(friendship.user2)
        else:
            friends.append(friendship.user1)
            
    # Ensure all friends have profiles
    for friend in friends:
        try:
            _ = friend.profile
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=friend)
    
    # Get pending friend requests
    pending_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status='pending'
    )
    
    return render(request, 'main/friends_list.html', {
        'friends': friends,
        'pending_requests': pending_requests
    })

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id)
        
        # Get existing friendships and requests
        friendships = Friendship.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        )
        friend_requests = FriendRequest.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user)
        )
        
        # Mark users who are already friends or have pending requests
        for user in users:
            user.is_friend = any(
                (f.user1 == user or f.user2 == user) 
                for f in friendships
            )
            user.has_request = any(
                (r.from_user == user or r.to_user == user) 
                for r in friend_requests
            )
    else:
        users = []
    
    return render(request, 'main/search_users.html', {'users': users, 'query': query})

@login_required
def send_friend_request(request, user_id):
    if request.method == 'POST':
        to_user = User.objects.get(id=user_id)
        FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={'status': 'pending'}
        )
        messages.success(request, f'Barátkérelem elküldve {to_user.username}-nak/nek!')
    return redirect('search_users')

@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        friend_request.status = 'accepted'
        friend_request.save()
        
        # Create friendship
        Friendship.objects.create(
            user1=friend_request.from_user,
            user2=friend_request.to_user
        )
        
        messages.success(request, f'Barátkérelem elfogadva!')
    return redirect('friends_list')

@login_required
def reject_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
        friend_request.status = 'rejected'
        friend_request.save()
        messages.info(request, 'Barátkérelem elutasítva.')
    return redirect('friends_list')

@login_required
def profile_settings(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, instance=profile)
            password_form = CustomPasswordChangeForm(request.user)
            if form.is_valid():
                form.save()
                # Update username only
                request.user.username = form.cleaned_data['username']
                request.user.save()
                messages.success(request, 'Profil sikeresen frissítve!')
                return redirect('profile_settings')
        
        elif 'change_password' in request.POST:
            form = UserProfileForm(instance=profile)
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Jelszó sikeresen módosítva!')
                return redirect('profile_settings')
    else:
        form = UserProfileForm(instance=profile)
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'main/profile_settings.html', {
        'form': form,
        'password_form': password_form
    })

@login_required
def view_friend_portfolio(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    
    # First check if profile is private
    try:
        if friend.profile.is_private:
            messages.error(request, 'Ez egy privát profil!')
            return redirect('friends_list')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Hiba történt a profil elérése során!')
        return redirect('friends_list')
    
    # Then check if they are friends
    is_friend = Friendship.objects.filter(
        (Q(user1=request.user) & Q(user2=friend)) |
        (Q(user1=friend) & Q(user2=request.user))
    ).exists()
    
    if not is_friend:
        messages.error(request, 'Csak barátok tekinthetik meg egymás portfolióját!')
        return redirect('friends_list')
    
    # Get friend's portfolio
    portfolio_items = PortfolioItem.objects.filter(user=friend)
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
    
    return render(request, 'main/friend_portfolio.html', {
        'friend': friend,
        'portfolio_data': portfolio_data,
        'total_portfolio_value': sum(data['total_value'] for data in portfolio_data)
    })
