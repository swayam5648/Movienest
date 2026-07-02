from django.urls import path
from navbar.views import login_view, register_view, activate_account, password_reset_view, password_reset_confirm_view, logout_view, contact_view, about_view, privacy_policy_view, terms_conditions_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('admin-login/', login_view, name='admin_login'),
    path('register/', register_view, name='register'),
    path('activate/<str:uidb64>/<str:token>/', activate_account, name='activate'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('logout/', logout_view, name='logout'),
    path('contact/', contact_view, name='contact'),
    path('about/', about_view, name='about'),
    path('privacy-policy/', privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', terms_conditions_view, name='terms_conditions'),
]
