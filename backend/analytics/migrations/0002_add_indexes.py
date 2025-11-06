from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="channel",
            index=models.Index(fields=["channel_id"], name="channel_id_idx"),
        ),
        migrations.AddIndex(
            model_name="video",
            index=models.Index(fields=["video_id"], name="video_id_idx"),
        ),
        migrations.AddIndex(
            model_name="video",
            index=models.Index(fields=["published_at"], name="video_pub_at_idx"),
        ),
        migrations.AddIndex(
            model_name="video",
            index=models.Index(fields=["channel"], name="video_channel_idx"),
        ),
    ]
