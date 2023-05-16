from django.db import models

from datetime import datetime


# Create your models here.
class CryptoAccounts(models.Model):
    pub_date = models.DateTimeField(default=datetime.now,
                                    verbose_name="Дата публикации")

    address = models.CharField(max_length=255,
                               unique=True,
                               verbose_name="public key")

    raw_data = models.TextField(max_length=255,
                                null=False,
                                blank=False,
                                verbose_name="Full info")
