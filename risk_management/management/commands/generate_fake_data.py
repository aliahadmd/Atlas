# risk_management/management/commands/generate_fake_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from risk_management.models import Asset, Risk, RiskAssessment, Monitoring, AIAnalysis
from django.utils import timezone
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generates fake data for the risk management system'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create users
        users = []
        for _ in range(5):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123'
            )
            users.append(user)

        # Create assets
        assets = []
        asset_types = ['Real Estate', 'Stocks', 'Bonds', 'Cash', 'Commodities']
        for _ in range(20):
            asset = Asset.objects.create(
                name=fake.company(),
                asset_type=random.choice(asset_types),
                value=random.uniform(10000, 10000000)
            )
            assets.append(asset)

        # Create risks
        risks = []
        for _ in range(15):
            risk = Risk.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(),
                risk_type=random.choice(Risk.RISK_TYPES)[0],
                probability=random.uniform(0, 1),
                impact=random.uniform(0, 1)
            )
            risk.assets.set(random.sample(assets, k=random.randint(1, 5)))
            risks.append(risk)

        # Create risk assessments
        for _ in range(30):
            risk_assessment = RiskAssessment.objects.create(
                risk=random.choice(risks),
                assessor=random.choice(users),
                mitigation_strategy=fake.text()
            )

            # Create AI analysis for each risk assessment
            AIAnalysis.objects.create(
                risk_assessment=risk_assessment,
                gemini_response=fake.text(),
                risk_score=random.uniform(0, 1),
                analysis=fake.text(),  # Populating 'analysis' field
                recommendations=fake.text(),
                scenarios=fake.text(),  # Populating 'scenarios' field
                key_indicators=fake.text()  # Populating 'key_indicators' field
            )

        # Create monitoring entries
        for _ in range(50):
            Monitoring.objects.create(
                risk=random.choice(risks),
                monitor=random.choice(users),
                status=random.choice(['Active', 'Resolved', 'Under Review']),
                notes=fake.text()
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated fake data'))