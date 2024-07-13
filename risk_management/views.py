# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Asset, Risk, RiskAssessment, Monitoring, AIAnalysis
from .forms import AssetForm, RiskForm, RiskAssessmentForm, MonitoringForm
import google.generativeai as genai
from django.conf import settings
import logging
from django.contrib import messages
import re


# Configure logging
logger = logging.getLogger(__name__)

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'risk_management/dashboard.html'
    context_object_name = 'risks'
    model = Risk

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assets'] = Asset.objects.all()
        context['recent_assessments'] = RiskAssessment.objects.order_by('-assessment_date')[:5]
        return context

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'risk_management/asset_list.html'
    context_object_name = 'assets'

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'risk_management/asset_detail.html'

class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'risk_management/asset_form.html'
    success_url = reverse_lazy('asset_list')

class RiskListView(LoginRequiredMixin, ListView):
    model = Risk
    template_name = 'risk_management/risk_list.html'
    context_object_name = 'risks'

class RiskDetailView(LoginRequiredMixin, DetailView):
    model = Risk
    template_name = 'risk_management/risk_detail.html'

class RiskCreateView(LoginRequiredMixin, CreateView):
    model = Risk
    form_class = RiskForm
    template_name = 'risk_management/risk_form.html'
    success_url = reverse_lazy('risk_list')

class RiskAssessmentCreateView(LoginRequiredMixin, CreateView):
    model = RiskAssessment
    form_class = RiskAssessmentForm
    template_name = 'risk_management/risk_assessment_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.assessor = self.request.user
        return super().form_valid(form)

class MonitoringCreateView(LoginRequiredMixin, CreateView):
    model = Monitoring
    form_class = MonitoringForm
    template_name = 'risk_management/monitoring_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.monitor = self.request.user
        return super().form_valid(form)

class AIAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = AIAnalysis
    template_name = 'risk_management/ai_analysis_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = [
            ('Detailed Analysis', 'analysis'),
            ('Recommendations', 'recommendations'),
            ('Potential Scenarios', 'scenarios'),
            ('Key Performance Indicators (KPIs)', 'key_indicators'),
        ]
        return context





def extract_risk_score(text):
    risk_score_match = re.search(r'risk.*?score.*?(\d+(\.\d+)?)', text, re.IGNORECASE)
    if risk_score_match:
        return float(risk_score_match.group(1))
    return None

def extract_sections(text):
    sections = {
        'Analysis': '',
        'Recommendations': '',
        'Scenarios': '',
        'Key Indicators': ''
    }
    
    # Try to find sections based on headers or content
    current_section = 'Analysis'  # Default to Analysis if no headers found
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this line is a new section header
        lower_line = line.lower()
        if 'analysis' in lower_line or 'overview' in lower_line:
            current_section = 'Analysis'
        elif 'recommendation' in lower_line:
            current_section = 'Recommendations'
        elif 'scenario' in lower_line:
            current_section = 'Scenarios'
        elif 'key' in lower_line and ('indicator' in lower_line or 'kpi' in lower_line):
            current_section = 'Key Indicators'
        elif 'risk score' in lower_line:
            continue  # Skip risk score line as it's handled separately
        
        # Add content to the current section
        sections[current_section] += line + '\n'
    
    # Trim whitespace from each section
    for key in sections:
        sections[key] = sections[key].strip()
    
    return sections

def trigger_ai_analysis(request, risk_assessment_id):
    try:
        risk_assessment = get_object_or_404(RiskAssessment, id=risk_assessment_id)
        
        if not hasattr(settings, 'GEMINI_API_KEY'):
            raise ValueError("GEMINI_API_KEY is not set in settings")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        associated_assets = ', '.join([asset.name for asset in risk_assessment.risk.assets.all()])
        prompt = f"""
        Analyze the following risk assessment:
        Risk: {risk_assessment.risk.name}
        Type: {risk_assessment.risk.risk_type}
        Probability: {risk_assessment.risk.probability}
        Impact: {risk_assessment.risk.impact}
        Mitigation Strategy: {risk_assessment.mitigation_strategy}
        Associated Assets: {associated_assets}

        Provide a comprehensive risk analysis including:
        1. A risk score between 0 and 1
        2. Detailed analysis of the risk
        3. Recommendations for managing the risk
        4. Potential scenarios and their impacts
        5. Key performance indicators (KPIs) to monitor this risk

        Format your response with clear section headers for each part of the analysis.
        Use markdown formatting for better readability.
        """
        
        response = model.generate_content(prompt)
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        logger.info(f"Raw AI response for risk assessment ID {risk_assessment_id}:\n{response.text}")
        
        risk_score = extract_risk_score(response.text)
        if risk_score is None:
            logger.warning(f"Risk score not found in AI response for risk assessment ID: {risk_assessment_id}")
            risk_score = 0.5  # Default to mid-range if not found
        
        try:
            sections = extract_sections(response.text)
        except Exception as e:
            logger.error(f"Error extracting sections: {str(e)}")
            sections = {key: "Error extracting section" for key in ['Analysis', 'Recommendations', 'Scenarios', 'Key Indicators']}
        
        for key, value in sections.items():
            if not value.strip():
                sections[key] = f"No {key.lower()} provided in AI response."
                logger.warning(f"Section '{key}' not found in AI response for risk assessment ID: {risk_assessment_id}")
        
        ai_analysis, created = AIAnalysis.objects.update_or_create(
            risk_assessment=risk_assessment,
            defaults={
                'gemini_response': response.text,
                'risk_score': risk_score,
                'analysis': sections['Analysis'],
                'recommendations': sections['Recommendations'],
                'scenarios': sections['Scenarios'],
                'key_indicators': sections['Key Indicators']
            }
        )
        
        risk_assessment.ai_analysis = ai_analysis.analysis
        risk_assessment.save()
        
        messages.success(request, "AI analysis completed successfully.")
        return redirect('ai_analysis_detail', pk=ai_analysis.pk)
    
    except ValueError as ve:
        logger.error(f"Value error in AI analysis: {str(ve)}")
        messages.error(request, f"An error occurred during AI analysis: {str(ve)}")
    except Exception as e:
        logger.error(f"Unexpected error in AI analysis: {str(e)}")
        messages.error(request, "An unexpected error occurred during AI analysis. Please try again later.")
    
    return redirect('dashboard')