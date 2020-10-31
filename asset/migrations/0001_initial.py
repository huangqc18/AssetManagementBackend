# Generated by Django 2.2.4 on 2020-10-31 23:10

from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='资产名称')),
                ('quantity', models.IntegerField(default=1, verbose_name='数量')),
                ('value', models.IntegerField(default=1, verbose_name='价值')),
                ('type_name', models.CharField(choices=[('ITEM', '价值型'), ('AMOUNT', '数量型')], default='ITEM', max_length=20, verbose_name='资产类型')),
                ('description', models.CharField(blank=True, default='', max_length=150, verbose_name='简介')),
                ('status', models.CharField(choices=[('IDLE', '闲置'), ('IN_USE', '使用'), ('IN_MAINTAIN', '维护'), ('RETIRED', '清退'), ('DELETED', '删除')], default='IDLE', max_length=20)),
                ('start_time', models.DateTimeField(auto_now_add=True, verbose_name='录入时间')),
                ('service_life', models.IntegerField(default=1, verbose_name='使用年限')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='资产分类')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssetCustomAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100, verbose_name='属性值')),
            ],
        ),
        migrations.CreateModel(
            name='CustomAttr',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='属性名')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalAsset',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='资产名称')),
                ('quantity', models.IntegerField(default=1, verbose_name='数量')),
                ('value', models.IntegerField(default=1, verbose_name='价值')),
                ('type_name', models.CharField(choices=[('ITEM', '价值型'), ('AMOUNT', '数量型')], default='ITEM', max_length=20, verbose_name='资产类型')),
                ('description', models.CharField(blank=True, default='', max_length=150, verbose_name='简介')),
                ('status', models.CharField(choices=[('IDLE', '闲置'), ('IN_USE', '使用'), ('IN_MAINTAIN', '维护'), ('RETIRED', '清退'), ('DELETED', '删除')], default='IDLE', max_length=20)),
                ('service_life', models.IntegerField(default=1, verbose_name='使用年限')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('category', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='asset.AssetCategory', verbose_name='类别')),
            ],
            options={
                'verbose_name': 'historical asset',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
