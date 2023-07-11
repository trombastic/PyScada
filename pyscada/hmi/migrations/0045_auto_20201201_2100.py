# Generated by Django 2.2.17 on 2020-12-01 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0078_auto_20201123_1906"),
        ("hmi", "0044_auto_20201201_1539"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChartAxis",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(blank=True, default="", max_length=400)),
                ("min", models.FloatField(default=0)),
                ("max", models.FloatField(default=100)),
                (
                    "show_plot_points",
                    models.BooleanField(
                        default=False, help_text="Show the plots points"
                    ),
                ),
                (
                    "show_plot_lines",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "No"), (1, "Yes"), (2, "Yes as steps")],
                        default=2,
                        help_text="Show the plot lines",
                    ),
                ),
                (
                    "stack",
                    models.BooleanField(
                        default=False, help_text="Stack all variables of this axis"
                    ),
                ),
                (
                    "chart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="hmi.Chart"
                    ),
                ),
                ("variables", models.ManyToManyField(to="pyscada.Variable")),
            ],
        ),
    ]
