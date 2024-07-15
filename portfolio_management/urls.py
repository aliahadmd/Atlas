# portfolio_management/urls.py

from django.urls import path
from . import views

app_name = 'portfolio_management'

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('<int:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('create/', views.portfolio_create, name='portfolio_create'),
    path('<int:portfolio_id>/update/', views.portfolio_update, name='portfolio_update'),
    path('<int:portfolio_id>/delete/', views.portfolio_delete, name='portfolio_delete'),
    
    path('<int:portfolio_id>/asset/add/', views.portfolio_asset_add, name='portfolio_asset_add'),
    path('<int:portfolio_id>/asset/<int:asset_id>/update/', views.portfolio_asset_update, name='portfolio_asset_update'),
    path('<int:portfolio_id>/asset/<int:asset_id>/delete/', views.portfolio_asset_delete, name='portfolio_asset_delete'),
    
    path('<int:portfolio_id>/transaction/add/', views.transaction_add, name='transaction_add'),
    path('<int:portfolio_id>/transaction/<int:transaction_id>/update/', views.transaction_update, name='transaction_update'),
    path('<int:portfolio_id>/transaction/<int:transaction_id>/delete/', views.transaction_delete, name='transaction_delete'),
    
    path('<int:portfolio_id>/performance/', views.portfolio_performance, name='portfolio_performance'),
    path('<int:portfolio_id>/associate-risk/', views.associate_risk_with_portfolio, name='associate_risk_with_portfolio'),
    path('<int:portfolio_id>/ai-advice/', views.ai_investment_advice, name='ai_investment_advice'),
    path('<int:portfolio_id>/ai-insights/', views.get_ai_insights, name='get_ai_insights'),
     
]
