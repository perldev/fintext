from django.core.management.base import BaseCommand
from datetime import datetime
from decimal import Decimal
from oper.models import simple_task
import json
import traceback
from django.core.management import call_command
from io import StringIO


class Command(BaseCommand):
    help = "simple task wrapper for background execute"

    def handle(self, *args, **options):

        tasks = simple_task.objects.filter(status="processing")

        for i in tasks:
            print("="*64)
            print("start task")
            print(i.ext_key)
            print(i.command_name)
            i.status = "processing2"
            i.save()
            params = json.loads(i.command_params)
            print(params)
            args1 = []
            out = StringIO()

            try:
                call_command(i.command_name, *args1, **params, stdout=out)
            except:
                err = traceback.format_exc()
                i.history = out.getvalue() + "="*64+"error:" + err
                i.status = "failed"
                i.save()
                continue

            i.history = out.getvalue()
            i.status = "processed"
            i.save()
            print("="*64)

