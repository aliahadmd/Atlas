from django.db import migrations, models

def default_key_indicators(apps, schema_editor):
    Monitoring = apps.get_model('risk_management', 'Monitoring')
    for monitoring in Monitoring.objects.all():
        monitoring.key_indicators = {}
        monitoring.save()

class Migration(migrations.Migration):

    dependencies = [
        ('risk_management', '0001_initial'),  # replace with your previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='monitoring',
            name='key_indicators',
            field=models.JSONField(default=dict, blank=True),
        ),
        migrations.RunPython(default_key_indicators),
    ]