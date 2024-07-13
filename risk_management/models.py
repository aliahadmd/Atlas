# risk_management/models.py

from django.db import models
from django.contrib.auth.models import User

class Asset(models.Model):
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    
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
    
    def __str__(self):
        return self.name

class RiskAssessment(models.Model):
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE)
    assessor = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment_date = models.DateTimeField(auto_now_add=True)
    ai_analysis = models.TextField()
    mitigation_strategy = models.TextField()
    
    def __str__(self):
        return f"Assessment of {self.risk.name} by {self.assessor.username}"

class Monitoring(models.Model):
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE)
    monitor = models.ForeignKey(User, on_delete=models.CASCADE)
    monitoring_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    notes = models.TextField()
    
    def __str__(self):
        return f"Monitoring of {self.risk.name} on {self.monitoring_date}"

class AIAnalysis(models.Model):
    risk_assessment = models.OneToOneField(RiskAssessment, on_delete=models.CASCADE)
    analysis_date = models.DateTimeField(auto_now_add=True)
    gemini_response = models.TextField()
    risk_score = models.FloatField()
    recommendations = models.TextField()
    
    def __str__(self):
        return f"AI Analysis for {self.risk_assessment}"
