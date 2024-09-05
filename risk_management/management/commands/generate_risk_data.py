from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from risk_management.models import Risk, RiskAssessment, AIAnalysis, Monitoring, MonitoringHistory
from portfolio_management.models import Portfolio, PortfolioAsset
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates fake data for the risk management app for the admin user'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating fake data for risk management...')

        # Get or create the admin user
        admin_user, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        })
        if created:
            admin_user.set_password('adminpassword')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write('Admin user already exists')

        # Get admin's portfolios and assets
        portfolios = Portfolio.objects.filter(owner=admin_user)
        assets = PortfolioAsset.objects.filter(portfolio__owner=admin_user).values_list('asset', flat=True).distinct()

        # Create risks
        risks = []
        risk_types = ['MARKET', 'CREDIT', 'OPERATIONAL', 'LIQUIDITY', 'REGULATORY']
        for i in range(10):
            risk = Risk.objects.create(
                name=f'Admin Risk {i+1}',
                description=f'Description for Admin Risk {i+1}',
                risk_type=random.choice(risk_types),
                probability=random.uniform(0, 1),
                impact=random.uniform(1, 10)
            )
            risk.assets.set(random.sample(list(assets), k=min(random.randint(1, 3), len(assets))))
            risk.portfolios.set(random.sample(list(portfolios), k=min(random.randint(1, 2), len(portfolios))))
            risks.append(risk)

        # Create risk assessments
        for risk in risks:
            for _ in range(random.randint(1, 3)):
                assessment = RiskAssessment.objects.create(
                    risk=risk,
                    assessor=admin_user,
                    mitigation_strategy=f'Mitigation strategy for {risk.name}'
                )

                # Create AI analysis for each assessment
                AIAnalysis.objects.create(
                    risk_assessment=assessment,
                    gemini_response='Simulated Gemini response',
                    risk_score=random.uniform(0, 10),
                    analysis=f'AI analysis for {risk.name}',
                    recommendations=f'Recommendations for {risk.name}',
                    scenarios=f'Possible scenarios for {risk.name}',
                    key_indicators=f'Key indicators for {risk.name}'
                )

        # Create monitoring entries
        status_choices = ['ON_TRACK', 'AT_RISK', 'OFF_TRACK', 'COMPLETED']
        for risk in risks:
            for _ in range(random.randint(2, 5)):
                monitoring = Monitoring.objects.create(
                    risk=risk,
                    monitor=admin_user,
                    status=random.choice(status_choices),
                    notes=f'Monitoring notes for {risk.name}',
                    key_indicators={'indicator1': random.randint(1, 100), 'indicator2': random.uniform(0, 1)},
                    next_review_date=timezone.now().date() + timedelta(days=random.randint(30, 180))
                )

                # Create monitoring history
                for _ in range(random.randint(1, 3)):
                    old_status = random.choice(status_choices)
                    new_status = random.choice(status_choices)
                    MonitoringHistory.objects.create(
                        monitoring=monitoring,
                        changed_by=admin_user,
                        old_status=old_status,
                        new_status=new_status,
                        change_reason=f'Status changed from {old_status} to {new_status}'
                    )

        self.stdout.write(self.style.SUCCESS('Successfully generated fake data for admin user risk management'))