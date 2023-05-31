from django.core.management.base import BaseCommand
from datetime import datetime
from decimal import Decimal
from oper.models import simple_task
import json
import traceback
from django.core.management import call_command


class Command(BaseCommand):
    help = "simple task wrapper for background execute"

    def handle(self, *args, **options):

        tasks = simple_task.objects.filter(status="processing")
        for i in tasks:
            print("="*64)
            print("start task")
            print(i.key)
            print(i.command_name)
            i.status = "processing2"
            i.save()
            params = json.loads(i.command_params)
            call_command(i.command_name, **params)
            print("="*64)

