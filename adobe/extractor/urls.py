from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('extract/', views.extract_outline, name='extract_outline'),
    path('results/', views.view_results, name='view_results'),
    path('download/<str:filename>/', views.download_result, name='download_result'),
]
