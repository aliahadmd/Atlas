from django.contrib import admin
from django.db.models import Q
from .models import Asset, Risk, RiskAssessment, AIAnalysis, Monitoring, MonitoringHistory

class UserSpecificAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(portfolios__owner=request.user) | Q(portfolio_assets__portfolio__owner=request.user)).distinct()

@admin.register(Asset)
class AssetAdmin(UserSpecificAdmin):
    list_display = ('name', 'asset_type', 'value')
    search_fields = ('name', 'asset_type')
    list_filter = ('asset_type',)

@admin.register(Risk)
class RiskAdmin(UserSpecificAdmin):
    list_display = ('name', 'risk_type', 'probability', 'impact')
    search_fields = ('name', 'description')
    list_filter = ('risk_type',)

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(UserSpecificAdmin):
    list_display = ('risk', 'assessor', 'assessment_date')
    search_fields = ('risk__name', 'assessor__username')
    list_filter = ('assessment_date',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(assessor=request.user)

@admin.register(AIAnalysis)
class AIAnalysisAdmin(UserSpecificAdmin):
    list_display = ('risk_assessment', 'analysis_date', 'risk_score')
    search_fields = ('risk_assessment__risk__name',)
    list_filter = ('analysis_date',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(risk_assessment__assessor=request.user)

@admin.register(Monitoring)
class MonitoringAdmin(UserSpecificAdmin):
    list_display = ('risk', 'monitor', 'monitoring_date', 'status', 'next_review_date')
    search_fields = ('risk__name', 'monitor__username')
    list_filter = ('status', 'monitoring_date', 'next_review_date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(monitor=request.user)

@admin.register(MonitoringHistory)
class MonitoringHistoryAdmin(UserSpecificAdmin):
    list_display = ('monitoring', 'changed_by', 'changed_date', 'old_status', 'new_status')
    search_fields = ('monitoring__risk__name', 'changed_by__username')
    list_filter = ('changed_date', 'old_status', 'new_status')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(changed_by=request.user)