# Generated by Django 5.0.7 on 2024-08-29 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_academicyear_year_alter_subject_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(choices=[('MATHEMATICS', 'MATHEMATICS'), ('ENGLISH', 'ENGLISH'), ('KISWAHILI', 'KISWAHILI'), ('CHEMISTRY', 'CHEMISTRY'), ('PHYSICS', 'PHYSICS'), ('BIOLOGY', 'BIOLOGY'), ('BUSINESS STUDIES', 'BUSINESS STUDIES'), ('COMPUTER STUDIES', 'COMPUTER STUDIES'), ('AGRICULTURE', 'AGRICULTURE'), ('HOME SCIENCE', 'HOME SCIENCE'), ('HISTORY', 'HISTORY'), ('GEOGRAPHY', 'GEOGRAPHY'), ('CRE', 'CRE')], max_length=100),
        ),
    ]
