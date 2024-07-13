# risk_management/admin.py

from django.contrib import admin
from .models import Asset, Risk, RiskAssessment, Monitoring, AIAnalysis

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'value')
    search_fields = ('name', 'asset_type')

@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ('name', 'risk_type', 'probability', 'impact')
    list_filter = ('risk_type',)
    search_fields = ('name', 'description')
    filter_horizontal = ('assets',)

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('risk', 'assessor', 'assessment_date')
    list_filter = ('assessment_date', 'assessor')
    search_fields = ('risk__name', 'assessor__username')

@admin.register(Monitoring)
class MonitoringAdmin(admin.ModelAdmin):
    list_display = ('risk', 'monitor', 'monitoring_date', 'status')
    list_filter = ('monitoring_date', 'status', 'monitor')
    search_fields = ('risk__name', 'monitor__username', 'notes')

@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('risk_assessment', 'analysis_date', 'risk_score')
    list_filter = ('analysis_date',)
    search_fields = ('risk_assessment__risk__name', 'recommendations')
