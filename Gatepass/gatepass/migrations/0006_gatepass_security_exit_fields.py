# Generated migration for adding security exit time fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatepass', '0005_student_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='gatepass',
            name='security_exit_date',
            field=models.DateField(blank=True, help_text='Date when student exited (security approval)', null=True),
        ),
        migrations.AddField(
            model_name='gatepass',
            name='security_exit_time',
            field=models.TimeField(blank=True, help_text='Exact time when student exited (security approval)', null=True),
        ),
    ]

