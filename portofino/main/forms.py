from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class SimpleUserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    haverda_password = forms.CharField(
        label='Haverda jelszó',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_haverda_password(self):
        haverda_pw = self.cleaned_data.get('haverda_password')
        if haverda_pw != 'szex':
            raise ValidationError('Helytelen Haverda jelszó!')
        return haverda_pw

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
