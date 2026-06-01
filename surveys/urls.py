from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('fundraiser/create/', views.fundraiser_create, name='fundraiser_create'),
    path('fundraiser/edit/<int:pk>/', views.fundraiser_edit, name='fundraiser_edit'),
    path('fundraiser/delete/<int:pk>/', views.fundraiser_delete, name='fundraiser_delete'),
    path('vote/create/', views.vote_create, name='vote_create'),
    path('vote/edit/<int:pk>/', views.vote_edit, name='vote_edit'),
    path('vote/delete/<int:pk>/', views.vote_delete, name='vote_delete'),
    path('withdrawal/request/<str:source_type>/<int:source_id>/', views.request_withdrawal, name='request_withdrawal'),
    path('withdrawal/slip/<int:withdrawal_id>/', views.download_withdrawal_slip, name='download_withdrawal_slip'),
]
