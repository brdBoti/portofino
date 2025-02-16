from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile

class SimpleUserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    haverda_password = forms.CharField(
        label='Szuper titkos jelszó',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_haverda_password(self):
        haverda_pw = self.cleaned_data.get('haverda_password')
        if haverda_pw != 'kolbász':
            raise ValidationError('Helytelen a szuper titkos jelszó!')
        return haverda_pw

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
        return user

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(
        label='Felhasználónév',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ['is_private', 'theme']
        labels = {
            'is_private': 'Privát profil',
            'theme': 'Téma',
        }
        widgets = {
            'is_private': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'theme': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['username'].initial = self.instance.user.username

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Régi jelszó'
        self.fields['new_password1'].label = 'Új jelszó'
        self.fields['new_password2'].label = 'Új jelszó megerősítése'
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
