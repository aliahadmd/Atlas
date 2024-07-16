# risk_management/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.contrib import messages
from .models import Asset, MonitoringHistory, Risk, RiskAssessment, Monitoring, AIAnalysis
from .forms import AssetForm, MonitoringHistoryForm, RiskForm, RiskAssessmentForm, MonitoringForm
from .ai_prompts import get_risk_analysis_prompt
import google.generativeai as genai
from django.conf import settings
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'risk_management/dashboard.html'
    context_object_name = 'risks'
    model = Risk

    def get_queryset(self):
        return Risk.objects.filter(portfolios__owner=self.request.user).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assets'] = Asset.objects.filter(portfolio_assets__portfolio__owner=self.request.user).distinct()
        context['recent_assessments'] = RiskAssessment.objects.filter(assessor=self.request.user).order_by('-assessment_date')[:5]
        
        # Aggregate data for charts
        risk_types = self.get_queryset().values('risk_type').annotate(count=Count('id'))
        context['risk_type_labels'] = [rt['risk_type'] for rt in risk_types]
        context['risk_type_data'] = [rt['count'] for rt in risk_types]
        
        monitoring_status = Monitoring.objects.filter(risk__portfolios__owner=self.request.user).values('status').annotate(count=Count('id'))
        context['monitoring_status_labels'] = [ms['status'] for ms in monitoring_status]
        context['monitoring_status_data'] = [ms['count'] for ms in monitoring_status]
        
        avg_impact = self.get_queryset().aggregate(Avg('impact'))['impact__avg']
        context['avg_impact'] = round(avg_impact, 2) if avg_impact else 0
        
        return context

class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = 'risk_management/asset_list.html'
    context_object_name = 'assets'

    def get_queryset(self):
        return Asset.objects.filter(portfolio_assets__portfolio__owner=self.request.user).distinct()

class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = 'risk_management/asset_detail.html'

    def get_queryset(self):
        return Asset.objects.filter(portfolio_assets__portfolio__owner=self.request.user)

class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'risk_management/asset_form.html'
    success_url = reverse_lazy('asset_list')

class RiskListView(LoginRequiredMixin, ListView):
    model = Risk
    template_name = 'risk_management/risk_list.html'
    context_object_name = 'risks'

    def get_queryset(self):
        return Risk.objects.filter(portfolios__owner=self.request.user).distinct()

class RiskDetailView(LoginRequiredMixin, DetailView):
    model = Risk
    template_name = 'risk_management/risk_detail.html'

    def get_queryset(self):
        return Risk.objects.filter(portfolios__owner=self.request.user)

class RiskCreateView(LoginRequiredMixin, CreateView):
    model = Risk
    form_class = RiskForm
    template_name = 'risk_management/risk_form.html'
    success_url = reverse_lazy('risk_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class RiskAssessmentCreateView(LoginRequiredMixin, CreateView):
    model = RiskAssessment
    form_class = RiskAssessmentForm
    template_name = 'risk_management/risk_assessment_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.assessor = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class AIAnalysisDetailView(LoginRequiredMixin, DetailView):
    model = AIAnalysis
    template_name = 'risk_management/ai_analysis_detail.html'

    def get_queryset(self):
        return AIAnalysis.objects.filter(risk_assessment__assessor=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = [
            ('Detailed Analysis', 'analysis'),
            ('Recommendations', 'recommendations'),
            ('Potential Scenarios', 'scenarios'),
            ('Key Performance Indicators (KPIs)', 'key_indicators'),
        ]
        return context

@login_required
def trigger_ai_analysis(request, risk_assessment_id):
    try:
        risk_assessment = get_object_or_404(RiskAssessment, id=risk_assessment_id, assessor=request.user)
        
        if not hasattr(settings, 'GEMINI_API_KEY'):
            raise ValueError("GEMINI_API_KEY is not set in settings")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        associated_assets = ', '.join([asset.name for asset in risk_assessment.risk.assets.all()])
        prompt = get_risk_analysis_prompt(risk_assessment, associated_assets)
        
        response = model.generate_content(prompt)
        if not response.text:
            raise ValueError("Empty response from Gemini API")
        
        logger.info(f"Raw AI response for risk assessment ID {risk_assessment_id}:\n{response.text}")
        
        risk_score = extract_risk_score(response.text)
        if risk_score is None:
            logger.warning(f"Risk score not found in AI response for risk assessment ID: {risk_assessment_id}")
            risk_score = 0.5  # Default to mid-range if not found
        
        sections = extract_sections(response.text)
        
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
    
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        messages.error(request, f"An error occurred during AI analysis: {str(e)}")
    
    return redirect('dashboard')

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
    
    current_section = 'Analysis'
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
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
            continue
        
        sections[current_section] += line + '\n'
    
    for key in sections:
        sections[key] = sections[key].strip()
    
    return sections

class MonitoringListView(LoginRequiredMixin, ListView):
    model = Monitoring
    template_name = 'risk_management/monitoring_list.html'
    context_object_name = 'monitoring_entries'

    def get_queryset(self):
        return Monitoring.objects.filter(risk__portfolios__owner=self.request.user).distinct()

class MonitoringDetailView(LoginRequiredMixin, DetailView):
    model = Monitoring
    template_name = 'risk_management/monitoring_detail.html'

    def get_queryset(self):
        return Monitoring.objects.filter(risk__portfolios__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history'] = self.object.history.all().order_by('-changed_date')
        return context

class MonitoringCreateView(LoginRequiredMixin, CreateView):
    model = Monitoring
    form_class = MonitoringForm
    template_name = 'risk_management/monitoring_form.html'
    success_url = reverse_lazy('monitoring_list')

    def form_valid(self, form):
        form.instance.monitor = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class MonitoringUpdateView(LoginRequiredMixin, UpdateView):
    model = Monitoring
    form_class = MonitoringForm
    template_name = 'risk_management/monitoring_form.html'
    success_url = reverse_lazy('monitoring_list')

    def get_queryset(self):
        return Monitoring.objects.filter(risk__portfolios__owner=self.request.user)

    def form_valid(self, form):
        old_status = self.get_object().status
        response = super().form_valid(form)
        new_status = form.instance.status

        if old_status != new_status:
            MonitoringHistory.objects.create(
                monitoring=self.object,
                changed_by=self.request.user,
                old_status=old_status,
                new_status=new_status,
                change_reason="Status updated"
            )

        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@login_required
def add_monitoring_history(request, pk):
    monitoring = get_object_or_404(Monitoring, pk=pk, risk__portfolios__owner=request.user)
    if request.method == 'POST':
        form = MonitoringHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            history.monitoring = monitoring
            history.changed_by = request.user
            history.old_status = monitoring.status
            history.save()
            
            monitoring.status = history.new_status
            monitoring.save()
            
            messages.success(request, "Monitoring history added successfully.")
            return redirect('monitoring_detail', pk=pk)
    else:
        form = MonitoringHistoryForm()
    
    return render(request, 'risk_management/add_monitoring_history.html', {'form': form, 'monitoring': monitoring})

class RiskHeatmapView(LoginRequiredMixin, TemplateView):
    template_name = 'risk_management/risk_heatmap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        risks = Risk.objects.filter(portfolios__owner=self.request.user).distinct()
        risk_data = [
            {
                'id': risk.id,
                'name': risk.name,
                'probability': risk.probability,
                'impact': risk.impact,
                'risk_type': risk.get_risk_type_display()
            }
            for risk in risks
        ]
        context['risk_data'] = risk_data
        return context

@login_required
def risk_data_json(request):
    risks = Risk.objects.filter(portfolios__owner=request.user).distinct()
    risk_data = [
        {
            'id': risk.id,
            'name': risk.name,
            'probability': risk.probability,
            'impact': risk.impact,
            'risk_type': risk.get_risk_type_display()
        }
        for risk in risks
    ]
    return JsonResponse(risk_data, safe=False)