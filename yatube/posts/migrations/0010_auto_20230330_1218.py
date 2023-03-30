# Generated by Django 2.2.16 on 2023-03-30 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20230328_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='К какой группе отнесем пост?', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='posts', to='posts.Group', verbose_name='Выбери группу'),
        ),
    ]