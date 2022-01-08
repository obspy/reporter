from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("taggit", "0003_taggeditem_add_unique_index"),
    ]

    operations = [
        migrations.CreateModel(
            name="SelectedNode",
            fields=[
                (
                    "name",
                    models.CharField(max_length=64, primary_key=True, serialize=False),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Report",
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
                ("datetime", models.DateTimeField(verbose_name="Date/Time")),
                ("tests", models.IntegerField()),
                ("errors", models.IntegerField()),
                ("failures", models.IntegerField()),
                ("skipped", models.IntegerField(blank=True, null=True)),
                ("modules", models.IntegerField()),
                ("timetaken", models.FloatField(blank=True, null=True)),
                (
                    "installed",
                    models.CharField(
                        blank=True, db_index=True, max_length=255, null=True
                    ),
                ),
                ("node", models.CharField(max_length=64)),
                ("system", models.CharField(db_index=True, max_length=16)),
                ("version", models.CharField(db_index=True, max_length=16)),
                (
                    "prurl",
                    models.URLField(
                        blank=True,
                        db_index=True,
                        null=True,
                        verbose_name="Pull request URL",
                    ),
                ),
                (
                    "ciurl",
                    models.URLField(
                        blank=True, null=True, verbose_name="Continous Integration URL"
                    ),
                ),
                ("architecture", models.CharField(db_index=True, max_length=16)),
                ("xml", models.TextField(verbose_name="XML Document")),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "ordering": ["-datetime"],
            },
        ),
        migrations.CreateModel(
            name="MenuItem",
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
                (
                    "name",
                    models.CharField(help_text='Use "-" for dividers', max_length=50),
                ),
                (
                    "icon",
                    models.CharField(
                        blank=True,
                        help_text="see http://getbootstrap.com/components/"
                        + "#glyphicons-glyphs",
                        max_length=100,
                        null=True,
                    ),
                ),
                ("url", models.CharField(blank=True, max_length=200, null=True)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="core.MenuItem",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
