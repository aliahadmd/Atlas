from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from portfolio_management.models import Portfolio, PortfolioAsset, PortfolioPerformance, Transaction
from risk_management.models import Asset
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates fake data for the portfolio management app for the admin user'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating fake data for portfolio management...')

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

        # Create portfolios for admin
        portfolios = []
        for i in range(5):
            portfolio, created = Portfolio.objects.get_or_create(
                name=f'Admin Portfolio {i+1}',
                defaults={
                    'description': f'Description for Admin Portfolio {i+1}',
                    'owner': admin_user
                }
            )
            portfolios.append(portfolio)

        # Create assets (assuming they don't exist yet)
        assets = []
        asset_types = ['Stock', 'Bond', 'ETF', 'Commodity', 'Cryptocurrency']
        for i in range(20):
            asset, created = Asset.objects.get_or_create(
                name=f'Asset {i+1}',
                defaults={
                    'asset_type': random.choice(asset_types),
                    'value': Decimal(random.uniform(10, 1000)).quantize(Decimal('0.01'))
                }
            )
            assets.append(asset)

        # Create portfolio assets
        for portfolio in portfolios:
            for _ in range(random.randint(5, 10)):
                PortfolioAsset.objects.get_or_create(
                    portfolio=portfolio,
                    asset=random.choice(assets),
                    defaults={
                        'quantity': Decimal(random.uniform(1, 100)).quantize(Decimal('0.000001')),
                        'purchase_price': Decimal(random.uniform(10, 1000)).quantize(Decimal('0.01')),
                        'purchase_date': timezone.now().date() - timedelta(days=random.randint(1, 365))
                    }
                )

        # Create portfolio performances
        for portfolio in portfolios:
            for i in range(30):
                date = timezone.now().date() - timedelta(days=i)
                PortfolioPerformance.objects.get_or_create(
                    portfolio=portfolio,
                    date=date,
                    defaults={
                        'total_value': Decimal(random.uniform(10000, 1000000)).quantize(Decimal('0.01')),
                        'daily_return': Decimal(random.uniform(-0.05, 0.05)).quantize(Decimal('0.0001')),
                        'cumulative_return': Decimal(random.uniform(-0.2, 0.5)).quantize(Decimal('0.0001'))
                    }
                )

        # Create transactions
        for portfolio in portfolios:
            for _ in range(random.randint(10, 20)):
                Transaction.objects.create(
                    portfolio=portfolio,
                    asset=random.choice(assets),
                    transaction_type=random.choice(['BUY', 'SELL']),
                    quantity=Decimal(random.uniform(1, 100)).quantize(Decimal('0.000001')),
                    price=Decimal(random.uniform(10, 1000)).quantize(Decimal('0.01')),
                    transaction_date=timezone.now() - timedelta(days=random.randint(1, 365))
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated fake data for admin user portfolio management'))