# Generated manually — alter existing users table to match phase 2 model
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='nickname',
            field=models.CharField(default='', max_length=50, verbose_name='昵称'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=11, unique=True, verbose_name='手机号'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('admin', '管理员'), ('reception', '前台'), ('member', '会员')],
                default='member',
                max_length=20,
                verbose_name='角色',
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='level',
            field=models.CharField(
                choices=[('normal', '普通会员'), ('gold', '金卡会员')],
                default='normal',
                max_length=20,
                verbose_name='会员等级',
            ),
        ),
    ]
