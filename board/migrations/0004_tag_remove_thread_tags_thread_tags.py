# Generated by Django 5.1.6 on 2025-02-25 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_post_parent_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='thread',
            name='tags',
        ),
        migrations.AddField(
            model_name='thread',
            name='tags',
            field=models.ManyToManyField(blank=True, to='board.tag'),
        ),
    ]
