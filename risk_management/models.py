# risk_management/models.py

from django.db import models
from django.conf import settings

class Asset(models.Model):
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    portfolio_assets = models.ManyToManyField('portfolio_management.PortfolioAsset', related_name='risk_assets')
    
    def __str__(self):
        return self.name

class Risk(models.Model):
    RISK_TYPES = (
        ('MARKET', 'Market Risk'),
        ('CREDIT', 'Credit Risk'),
        ('OPERATIONAL', 'Operational Risk'),
        ('LIQUIDITY', 'Liquidity Risk'),
        ('REGULATORY', 'Regulatory Risk'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    probability = models.FloatField()
    impact = models.FloatField()
    assets = models.ManyToManyField(Asset, related_name='risks')
    portfolios = models.ManyToManyField('portfolio_management.Portfolio', related_name='risks')
    
    def __str__(self):
        return self.name

class RiskAssessment(models.Model):
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE)
    assessor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment_date = models.DateTimeField(auto_now_add=True)
    ai_analysis = models.TextField(blank=True, null=True)
    mitigation_strategy = models.TextField()
    
    def __str__(self):
        return f"Assessment of {self.risk.name} by {self.assessor.username}"

class AIAnalysis(models.Model):
    risk_assessment = models.OneToOneField(RiskAssessment, on_delete=models.CASCADE)
    analysis_date = models.DateTimeField(auto_now_add=True)
    gemini_response = models.TextField()
    risk_score = models.FloatField()
    analysis = models.TextField()
    recommendations = models.TextField()
    scenarios = models.TextField()
    key_indicators = models.TextField()
    
    def __str__(self):
        return f"AI Analysis for {self.risk_assessment}"

class Monitoring(models.Model):
    STATUS_CHOICES = [
        ('ON_TRACK', 'On Track'),
        ('AT_RISK', 'At Risk'),
        ('OFF_TRACK', 'Off Track'),
        ('COMPLETED', 'Completed'),
    ]

    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='monitoring_entries')
    monitor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    monitoring_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField()
    key_indicators = models.JSONField(default=dict, blank=True) 
    next_review_date = models.DateField()
    
    def __str__(self):
        return f"Monitoring of {self.risk.name} on {self.monitoring_date}"

class MonitoringHistory(models.Model):
    monitoring = models.ForeignKey(Monitoring, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_date = models.DateTimeField(auto_now_add=True)
    old_status = models.CharField(max_length=20, choices=Monitoring.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Monitoring.STATUS_CHOICES)
    change_reason = models.TextField()

    def __str__(self):
        return f"Status change for {self.monitoring} on {self.changed_date}"