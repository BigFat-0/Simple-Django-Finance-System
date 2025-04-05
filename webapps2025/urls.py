from django.contrib import admin
from django.urls import path, include
from payapp.views import CurrencyConversionView
from register.views import user_login

urlpatterns = [
    path('', user_login, name='home'),
    path('webapps2025/admin/', admin.site.urls),  # Admin path
    path('webapps2025/', include('register.urls')),  # Register app URLs
    path('webapps2025/', include('payapp.urls')),    # Payapp URLs
    path('api/convert/', CurrencyConversionView.as_view(), name='currency_convert'),  # API for testing
]
