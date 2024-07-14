# forms.py

from django import forms
from .models import Asset, MonitoringHistory, Risk, RiskAssessment, Monitoring
import json


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
        fields = ['risk', 'status', 'notes', 'key_indicators', 'next_review_date']
        widgets = {
            'next_review_date': forms.DateInput(attrs={'type': 'date'}),
            'key_indicators': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_key_indicators(self):
        key_indicators = self.cleaned_data['key_indicators']
        if isinstance(key_indicators, str):
            try:
                return json.loads(key_indicators)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for key indicators")
        elif isinstance(key_indicators, dict):
            return key_indicators
        else:
            raise forms.ValidationError("Key indicators must be a JSON string or a dictionary")

class MonitoringHistoryForm(forms.ModelForm):
    class Meta:
        model = MonitoringHistory
        fields = ['new_status', 'change_reason']