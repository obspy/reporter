from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="ciurl",
            field=models.URLField(
                blank=True, null=True, verbose_name="Continuous Integration URL"
            ),
        ),
    ]
