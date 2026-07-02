from django.shortcuts import render, redirect
from navbar.forms import RegistrationForm, PasswordResetForm
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from navbar.utils import send_activation_email, send_reset_apassword_email
from navbar.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required

# Replace this with your custom decorator if used
def login_not_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Allow password reset confirm view even if user is logged in
        if request.user.is_authenticated and 'password_reset_confirm' not in request.path:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# Login View (User-only login)
@login_not_required
def login_view(req):
    if req.user.is_authenticated:
        if req.user.is_admin:
            logout(req)
            messages.error(req, "Admins cannot login from user login page.")
            return redirect('admin_login')
        return redirect('home')

    if req.method == "POST":
        email = req.POST.get("email")
        password = req.POST.get("password")

        if not email or not password:
            messages.error(req, "Both fields are required.")
            return redirect('login')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(req, "Invalid email or password.")
            return redirect('login')

        if not user.is_active:
            messages.error(req, "Your account is inactive. Please activate your account.")
            return redirect('login')

        # Block admin login here
        if user.is_admin:
            messages.error(req, "Admins cannot login from user login page. Please use Admin Login.")
            return redirect('admin_login')

        # Authenticate user
        user = authenticate(req, email=email, password=password)
        if user is not None:
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, "Invalid email or password.")
            return redirect('login')

    return render(req, 'navbar/login.html')

# Register View
@login_not_required
def register_view(req):
    if req.method == "POST":
        form = RegistrationForm(req.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False
            user.save()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
            activation_url = f"{settings.SITE_DOMAIN}{activation_link}"
            send_activation_email(user.email, activation_url)

            messages.success(
                req,
                'Registration successful! Please check your email to activate your account.'
            )
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(req, 'navbar/register.html', {"form": form})


# Account Activation View
def activate_account(req, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user.is_active:
            messages.warning(req, "This account has already been activated.")
            return redirect('login')

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(req, "Your account has been activated successfully!")
            return redirect('login')
        else:
            messages.error(req, "The activation link is invalid or has expired.")
            return redirect('login')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(req, "Invalid activation link.")
        return redirect('login')

# Password Reset Request View
@login_not_required
def password_reset_view(req):
    if req.method == "POST":
        form = PasswordResetForm(req.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = reverse(
                    'password_reset_confirm',
                    kwargs={'uidb64': uidb64, 'token': token}
                )
                absolute_reset_url = req.build_absolute_uri(reset_url)
                send_reset_apassword_email(user.email, absolute_reset_url)

            messages.success(
                req,
                "We have sent you a password reset link. Please check your email."
            )
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(req, 'navbar/password_reset.html', {'form': form})

# Password Reset Confirm View
@login_not_required
def password_reset_confirm_view(req, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            messages.error(req, 'This link has expired or is invalid.')
            return redirect('password_reset')

        if req.method == "POST":
            form = SetPasswordForm(user, req.POST)
            if form.is_valid():
                form.save()
                messages.success(req, 'Your password has been successfully reset.')
                return redirect('login')
            else:
                for error_list in form.errors.values():
                    for error in error_list:
                        messages.error(req, str(error))
        else:
            form = SetPasswordForm(user)

        return render(req, 'navbar/password_reset_confirmation.html', {
            'form': form,
            'uidb64': uidb64,
            'token': token
        })

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(req, 'An error occurred. Please try again later.')
        return redirect('password_reset')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('home')

# Static Pages
def contact_view(request):
    return render(request, 'static_pages/contact.html')

def about_view(request):
    return render(request, 'static_pages/about.html')

def privacy_policy_view(request):
    return render(request, 'static_pages/privacy_policy.html')

def terms_conditions_view(request):
    return render(request, 'static_pages/terms_conditions.html')
