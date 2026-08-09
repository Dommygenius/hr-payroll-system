from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_extended_hr_features'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='enabled_roles',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Role codes available for this tenant. Empty = use system defaults.',
            ),
        ),
    ]
