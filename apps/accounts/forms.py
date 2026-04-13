from django import forms
from django.contrib.auth import authenticate
from .models import User


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'placeholder': 'votre@email.com', 'autofocus': True})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    remember_me = forms.BooleanField(required=False, label="Se souvenir de moi")

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Email ou mot de passe incorrect.")
            if not self.user.is_active:
                raise forms.ValidationError("Ce compte est désactivé.")
        return self.cleaned_data

    def get_user(self):
        return self.user


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(),
        min_length=8
    )
    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
