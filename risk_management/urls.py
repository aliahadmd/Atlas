# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('assets/create/', views.AssetCreateView.as_view(), name='asset_create'),
    
    path('risks/', views.RiskListView.as_view(), name='risk_list'),
    path('risks/<int:pk>/', views.RiskDetailView.as_view(), name='risk_detail'),
    path('risks/create/', views.RiskCreateView.as_view(), name='risk_create'),
    
    path('risk-assessment/create/', views.RiskAssessmentCreateView.as_view(), name='risk_assessment_create'),
    path('monitoring/create/', views.MonitoringCreateView.as_view(), name='monitoring_create'),
    
    path('ai-analysis/<int:pk>/', views.AIAnalysisDetailView.as_view(), name='ai_analysis_detail'),
    path('trigger-ai-analysis/<int:risk_assessment_id>/', views.trigger_ai_analysis, name='trigger_ai_analysis'),

    path('monitoring/', views.MonitoringListView.as_view(), name='monitoring_list'),
    path('monitoring/<int:pk>/', views.MonitoringDetailView.as_view(), name='monitoring_detail'),
    path('monitoring/create/', views.MonitoringCreateView.as_view(), name='monitoring_create'),
    path('monitoring/<int:pk>/update/', views.MonitoringUpdateView.as_view(), name='monitoring_update'),
    path('monitoring/<int:pk>/history/add/', views.add_monitoring_history, name='add_monitoring_history'),

    path('risk-heatmap/', views.RiskHeatmapView.as_view(), name='risk_heatmap'),
    path('risk-data-json/', views.risk_data_json, name='risk_data_json'),
]