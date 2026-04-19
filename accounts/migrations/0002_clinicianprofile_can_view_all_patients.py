from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicianprofile',
            name='can_view_all_patients',
            field=models.BooleanField(
                default=False,
                help_text='If set, can open any patient (case study: view all users). Otherwise only assigned patients.',
            ),
        ),
    ]
