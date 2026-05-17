from django.db import migrations
import django.db.models.fields

class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scholarship',
            name='country',
            field=django.db.models.fields.CharField(
                choices=[
                    ('indonesia', 'Indonesia'),
                    ('malaysia',  'Malaysia'),
                    ('thailand',  'Thailand'),
                    ('taiwan',    'Taiwan'),
                    ('japan',     'Japan'),
                    ('singapore', 'Singapore'),
                    ('china',     'China'),
                    ('other',     'Other'),
                ],
                default='indonesia',
                max_length=20,
            ),
        ),
    ]