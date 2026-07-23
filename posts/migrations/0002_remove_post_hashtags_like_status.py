# Generated manually to preserve the explicit PostHashtag join model.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="hashtags",
        ),
    ]
