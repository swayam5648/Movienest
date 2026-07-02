from django.urls import path
from payment import views

app_name = 'payment'

urlpatterns = [
    path('payment/<int:payment_id>/', views.payment_page, name='payment_page'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]
