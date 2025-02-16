from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='employees/', null=True, blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='books/', null=True, blank=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name}"

class Publication(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image = models.ImageField(upload_to='publications/', null=True, blank=True)
    stock = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return self.publication.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Függőben'),
        ('completed', 'Teljesítve'),
        ('cancelled', 'Törölve'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Publication, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of purchase

class PortfolioItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_id = models.CharField(max_length=100)
    coin_symbol = models.CharField(max_length=10)
    coin_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    purchase_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # USD price per token
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coin_id')

    def get_total_value(self, current_price):
        return self.quantity * current_price
        
    def get_profit_percentage(self, current_price):
        if self.purchase_price == 0:
            return 0
        return ((current_price - self.purchase_price) / self.purchase_price) * 100

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Függőben'),
        ('accepted', 'Elfogadva'),
        ('rejected', 'Elutasítva')
    ], default='pending')

    class Meta:
        unique_together = ('from_user', 'to_user')

class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendships2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_private = models.BooleanField(default=True)
    theme = models.CharField(max_length=20, choices=[
        ('light', 'Világos'),
        ('dark', 'Sötét'),
        ('blue', 'Kék'),
    ], default='light')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} profilja"