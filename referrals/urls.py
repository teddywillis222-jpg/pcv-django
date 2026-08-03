from django.urls import path
from . import views

app_name = 'referrals'

urlpatterns = [
    path('p/<str:referral_code>/', views.ambassador_landing_page, name='landing'),
    path('cgu-ambassadeurs/', views.cgu_ambassadeurs, name='cgu'),
]
