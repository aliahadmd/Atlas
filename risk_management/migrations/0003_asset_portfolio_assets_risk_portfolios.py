# Generated by Django 5.0.7 on 2024-07-14 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio_management', '0001_initial'),
        ('risk_management', '0002_alter_monitoring_key_indicators'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='portfolio_assets',
            field=models.ManyToManyField(related_name='risk_assets', to='portfolio_management.portfolioasset'),
        ),
        migrations.AddField(
            model_name='risk',
            name='portfolios',
            field=models.ManyToManyField(related_name='risks', to='portfolio_management.portfolio'),
        ),
    ]