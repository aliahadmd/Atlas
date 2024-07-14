from django.contrib import admin
from .models import Asset, Risk, RiskAssessment, AIAnalysis, Monitoring, MonitoringHistory

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'value')
    search_fields = ('name', 'asset_type')
    list_filter = ('asset_type',)

@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ('name', 'risk_type', 'probability', 'impact')
    search_fields = ('name', 'description')
    list_filter = ('risk_type',)

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('risk', 'assessor', 'assessment_date')
    search_fields = ('risk__name', 'assessor__username')
    list_filter = ('assessment_date',)

@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('risk_assessment', 'analysis_date', 'risk_score')
    search_fields = ('risk_assessment__risk__name',)
    list_filter = ('analysis_date',)

@admin.register(Monitoring)
class MonitoringAdmin(admin.ModelAdmin):
    list_display = ('risk', 'monitor', 'monitoring_date', 'status', 'next_review_date')
    search_fields = ('risk__name', 'monitor__username')
    list_filter = ('status', 'monitoring_date', 'next_review_date')

@admin.register(MonitoringHistory)
class MonitoringHistoryAdmin(admin.ModelAdmin):
    list_display = ('monitoring', 'changed_by', 'changed_date', 'old_status', 'new_status')
    search_fields = ('monitoring__risk__name', 'changed_by__username')
    list_filter = ('changed_date', 'old_status', 'new_status')