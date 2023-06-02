from django.db import models


class ExchangePage(models.Model):
    title_ru = models.CharField(max_length=255, verbose_name="заголовок ru")
    title_uk = models.CharField(max_length=255, verbose_name="заголовок uk")
    content_ru = models.TextField(verbose_name="текст ru", null=True, blank=True)
    content_uk = models.TextField(verbose_name="текст uk", null=True, blank=True)
    currency_from = models.CharField(max_length=20, verbose_name="валюта from")
    currency_to = models.CharField(max_length=20, verbose_name="валюта to")
    slug = models.CharField(max_length=255, verbose_name="url страницы", null=True, blank=True)

    class Meta:
        verbose_name = u'Страница обмена'
        verbose_name_plural = u'Страницы обмена'

    def save(self, *args, **kwargs):
        self.slug = self.currency_from + '-to-' + self.currency_to
        super(ExchangePage, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.title_ru
    

class StaticPage(models.Model):
    title_ru = models.CharField(max_length=255, verbose_name="заголовок ru")
    title_uk = models.CharField(max_length=255, verbose_name="заголовок uk")
    content_ru = models.TextField(verbose_name="текст ru", null=True, blank=True)
    content_uk = models.TextField(verbose_name="текст uk", null=True, blank=True)
    slug = models.CharField(max_length=255, verbose_name="url страницы", null=True, blank=True)

    class Meta:
        verbose_name = u'Статичная страница'
        verbose_name_plural = u'Статичные страницы'
        
    def __str__(self):
        return self.title_ru
    

class PageText(models.Model):
    title_ru = models.CharField(max_length=255, verbose_name="заголовок ru")
    title_uk = models.CharField(max_length=255, verbose_name="заголовок uk")
    content_ru = models.TextField(verbose_name="текст ru", null=True, blank=True)
    content_uk = models.TextField(verbose_name="текст uk", null=True, blank=True)

    class Meta:
        verbose_name = u'Текст для страницы'
        verbose_name_plural = u'Тексты для страниц'
        
    def __str__(self):
        return self.title_ru