from django.core.management.base import BaseCommand
from analytics.models import Channel

class Command(BaseCommand):
    help = "List stored YouTube channels"

    def handle(self, *args, **options):
        qs = Channel.objects.order_by("title")
        if not qs.exists():
            self.stdout.write("No channels found.")
            return
        for c in qs:
            self.stdout.write(f"{c.channel_id}\t{c.title}\t{sub_or_none(c.subscribers)} subs")

def sub_or_none(v):
    return v if v is not None else "n/a"
