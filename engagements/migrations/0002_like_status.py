# Generated manually to retain existing likes as active likes.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("engagements", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="like",
            name="status",
            field=models.CharField(
                choices=[("LIKE", "Like"), ("UNLIKE", "Unlike")], default="LIKE", max_length=10
            ),
        ),
    ]
