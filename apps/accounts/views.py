from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, UserCreateForm
from .models import User
from apps.audit.utils import log_action


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request=request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        if not form.cleaned_data.get('remember_me'):
            request.session.set_expiry(0)
        log_action(request, user, 'LOGIN', 'accounts', 'User', user.id, f"Connexion de {user.email}")
        messages.success(request, f"Bienvenue, {user.get_full_name()} !")
        return redirect(request.GET.get('next', 'dashboard'))

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    log_action(request, request.user, 'LOGOUT', 'accounts', 'User',
               request.user.id, f"Déconnexion de {request.user.email}")
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def users_list_view(request):
    if not request.user.is_admin:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    users = User.objects.all().order_by('last_name')
    return render(request, 'accounts/users_list.html', {'users': users})


@login_required
def user_create_view(request):
    if not request.user.is_admin:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        log_action(request, request.user, 'CREATE', 'accounts', 'User', user.id,
                   f"Création utilisateur {user.email} (rôle: {user.role})")
        messages.success(request, f"Utilisateur {user.get_full_name()} créé avec succès.")
        return redirect('users_list')

    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Créer'})


@login_required
def user_toggle_active(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    try:
        user = User.objects.get(pk=pk)
        user.is_active = not user.is_active
        user.save()
        action = "activé" if user.is_active else "désactivé"
        log_action(request, request.user, 'UPDATE', 'accounts', 'User', user.id,
                   f"Utilisateur {user.email} {action}")
        messages.success(request, f"Compte {action} avec succès.")
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    return redirect('users_list')
