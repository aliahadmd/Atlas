# forms.py

from django import forms
from .models import Asset, Risk, RiskAssessment, Monitoring

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'value']

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['name', 'description', 'risk_type', 'probability', 'impact', 'assets']

class RiskAssessmentForm(forms.ModelForm):
    class Meta:
        model = RiskAssessment
        fields = ['risk', 'ai_analysis', 'mitigation_strategy']

class MonitoringForm(forms.ModelForm):
    class Meta:
        model = Monitoring
        fields = ['risk', 'status', 'notes']