# Generated by Django 5.1.7 on 2025-03-16 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_repo', '0006_teacher_letter_of_intent_alter_teacher_branch_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Other', max_length=10),
        ),
    ]
