# Generated by Django 5.0.7 on 2024-07-30 14:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portfolio_management', '0001_initial'),
        ('risk_management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioasset',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk_management.asset'),
        ),
        migrations.AddField(
            model_name='portfolioasset',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_assets', to='portfolio_management.portfolio'),
        ),
        migrations.AddField(
            model_name='portfolioperformance',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to='portfolio_management.portfolio'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk_management.asset'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='portfolio_management.portfolio'),
        ),
        migrations.AlterUniqueTogether(
            name='portfolioasset',
            unique_together={('portfolio', 'asset')},
        ),
        migrations.AlterUniqueTogether(
            name='portfolioperformance',
            unique_together={('portfolio', 'date')},
        ),
    ]
