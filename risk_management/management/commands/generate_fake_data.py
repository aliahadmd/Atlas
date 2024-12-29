from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from risk_management.models import Asset, Risk, RiskAssessment, AIAnalysis, Monitoring, MonitoringHistory
from portfolio_management.models import Portfolio, PortfolioAsset, PortfolioPerformance, Transaction
from decimal import Decimal
import random
from datetime import datetime, timedelta
import faker
import json

User = get_user_model()
fake = faker.Faker()

class Command(BaseCommand):
    help = 'Generate fake data for portfolio and risk management'

    def generate_key_indicators(self):
        return {
            'volatility': round(random.uniform(0.1, 0.5), 2),
            'sharpe_ratio': round(random.uniform(-1, 3), 2),
            'beta': round(random.uniform(0.5, 1.5), 2),
            'alpha': round(random.uniform(-0.2, 0.2), 2),
            'r_squared': round(random.uniform(0.7, 1.0), 2),
            'tracking_error': round(random.uniform(0.02, 0.1), 2),
            'information_ratio': round(random.uniform(-0.5, 1.5), 2)
        }

    def generate_risk_scenarios(self):
        scenarios = []
        for i in range(3):
            scenarios.append({
                'name': fake.catch_phrase(),
                'probability': round(random.uniform(0.1, 0.9), 2),
                'impact': round(random.uniform(1, 10), 2),
                'description': fake.text(),
                'mitigation_steps': [fake.sentence() for _ in range(3)]
            })
        return json.dumps(scenarios, indent=2)

    def handle(self, *args, **kwargs):
        # Create test user if not exists
        user, created = User.objects.get_or_create(
            username='aliahadmd3',
            email='aliahadmd3@gmail.com',
            defaults={
                'is_staff': True,
                'first_name': 'Ali',
                'last_name': 'Ahmad'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {user.username}'))

        # Generate Assets
        asset_types = [
            'Large Cap Stock', 'Mid Cap Stock', 'Small Cap Stock',
            'Government Bond', 'Corporate Bond', 'Municipal Bond',
            'Real Estate', 'Cryptocurrency', 'Commodity',
            'ETF', 'Mutual Fund', 'Options'
        ]
        assets = []
        for i in range(20):  # Increased from 10 to 20 assets
            asset = Asset.objects.create(
                name=f"{fake.company()} {random.choice(asset_types)}",
                asset_type=random.choice(asset_types),
                value=Decimal(str(random.uniform(1000, 1000000)))
            )
            assets.append(asset)
            self.stdout.write(f'Created asset: {asset.name}')

        # Generate Multiple Portfolios
        portfolios = []
        portfolio_names = [
            "Main Investment Portfolio",
            "Retirement Fund",
            "High Risk Growth Portfolio",
            "Conservative Income Portfolio"
        ]
        
        for portfolio_name in portfolio_names:
            portfolio = Portfolio.objects.create(
                name=f"{user.username}'s {portfolio_name}",
                description=fake.text(),
                owner=user,
            )
            portfolios.append(portfolio)
            self.stdout.write(f'Created portfolio: {portfolio.name}')

        # Generate Portfolio Assets
        for portfolio in portfolios:
            # Randomly select 5-15 assets for each portfolio
            selected_assets = random.sample(assets, random.randint(5, 15))
            for asset in selected_assets:
                purchase_date = timezone.now().date() - timedelta(days=random.randint(1, 730))  # Up to 2 years history
                portfolio_asset = PortfolioAsset.objects.create(
                    portfolio=portfolio,
                    asset=asset,
                    quantity=Decimal(str(random.uniform(1, 1000))),
                    purchase_price=Decimal(str(random.uniform(10, 10000))),
                    purchase_date=purchase_date
                )
                self.stdout.write(f'Added asset to portfolio: {portfolio_asset}')

        # Generate Portfolio Performance
        for portfolio in portfolios:
            cumulative_return = Decimal('0.0')
            for i in range(365):  # Full year of daily performance
                date = timezone.now().date() - timedelta(days=i)
                daily_return = Decimal(str(random.uniform(-0.03, 0.03)))
                cumulative_return += daily_return
                
                PortfolioPerformance.objects.create(
                    portfolio=portfolio,
                    date=date,
                    total_value=Decimal(str(random.uniform(100000, 1000000))),
                    daily_return=daily_return,
                    cumulative_return=cumulative_return
                )

        # Generate Risks
        risks = []
        risk_names = [
            "Market Volatility", "Interest Rate Changes", "Credit Default",
            "Operational System Failure", "Regulatory Changes", "Liquidity Crunch",
            "Cybersecurity Breach", "Political Instability", "Currency Fluctuation",
            "Climate Change Impact"
        ]
        
        for risk_name in risk_names:
            risk = Risk.objects.create(
                name=risk_name,
                description=fake.text(max_nb_chars=500),
                risk_type=random.choice(Risk.RISK_TYPES)[0],
                probability=random.uniform(0, 1),
                impact=random.uniform(1, 10)
            )
            # Associate with multiple assets and portfolios
            risk.assets.set(random.sample(assets, k=random.randint(2, 5)))
            risk.portfolios.set(random.sample(portfolios, k=random.randint(1, len(portfolios))))
            risks.append(risk)
            self.stdout.write(f'Created risk: {risk.name}')

        # Generate Risk Assessments and AI Analysis
        for risk in risks:
            # Create multiple assessments per risk
            for _ in range(random.randint(2, 4)):
                assessment_date = timezone.now() - timedelta(days=random.randint(1, 180))
                assessment = RiskAssessment.objects.create(
                    risk=risk,
                    assessor=user,
                    assessment_date=assessment_date,
                    ai_analysis=fake.text(max_nb_chars=1000),
                    mitigation_strategy='\n'.join([fake.sentence() for _ in range(5)])
                )
                
                AIAnalysis.objects.create(
                    risk_assessment=assessment,
                    analysis_date=assessment_date,
                    gemini_response=fake.text(max_nb_chars=1000),
                    risk_score=random.uniform(1, 10),
                    analysis=fake.text(max_nb_chars=1000),
                    recommendations='\n'.join([f"{i+1}. {fake.sentence()}" for i in range(5)]),
                    scenarios=self.generate_risk_scenarios(),
                    key_indicators=json.dumps(self.generate_key_indicators(), indent=2)
                )

        # Generate Monitoring with History
        for risk in risks:
            # Create multiple monitoring entries per risk
            for _ in range(random.randint(3, 6)):
                monitoring_date = timezone.now() - timedelta(days=random.randint(1, 90))
                status = random.choice(['ON_TRACK', 'AT_RISK', 'OFF_TRACK', 'COMPLETED'])
                
                monitoring = Monitoring.objects.create(
                    risk=risk,
                    monitor=user,
                    monitoring_date=monitoring_date,
                    status=status,
                    notes=fake.text(max_nb_chars=500),
                    key_indicators=self.generate_key_indicators(),
                    next_review_date=timezone.now().date() + timedelta(days=random.randint(1, 30))
                )
                
                # Generate history entries for each monitoring
                previous_status = 'ON_TRACK'
                for _ in range(random.randint(2, 4)):
                    new_status = random.choice(['ON_TRACK', 'AT_RISK', 'OFF_TRACK', 'COMPLETED'])
                    MonitoringHistory.objects.create(
                        monitoring=monitoring,
                        changed_by=user,
                        changed_date=monitoring_date - timedelta(days=random.randint(1, 30)),
                        old_status=previous_status,
                        new_status=new_status,
                        change_reason=fake.text(max_nb_chars=200)
                    )
                    previous_status = new_status

        # Generate Transactions
        for portfolio in portfolios:
            # Generate more transactions per portfolio
            for _ in range(random.randint(20, 30)):
                asset = random.choice(assets)
                transaction_date = timezone.now() - timedelta(days=random.randint(1, 365))
                
                Transaction.objects.create(
                    portfolio=portfolio,
                    asset=asset,
                    transaction_type=random.choice(['BUY', 'SELL']),
                    quantity=Decimal(str(random.uniform(1, 100))),
                    price=Decimal(str(random.uniform(10, 5000))),
                    transaction_date=transaction_date
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated comprehensive fake data'))
