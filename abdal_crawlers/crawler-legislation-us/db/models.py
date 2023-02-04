import sys

try:
    from django.db import models
except Exception as e:
    print(f'Exception: Django Not Found, please install it with "pip install django". (error{e})')
    sys.exit()


# Sample User model
class Page(models.Model):
    url = models.CharField(max_length=500, null=False)
    num = models.IntegerField(null=False)
    status = models.TextField(null=False)
    count = models.IntegerField(null=False)

    def __str__(self):
        return self.url

    class Meta:
        unique_together = (('url', 'num'),)


class Legislation(models.Model):
    title = models.TextField(null=False)
    url = models.CharField(max_length=500, null=False, unique=True)
    code_name = models.CharField(max_length=50, null=False)
    congress = models.CharField(max_length=500, null=False)
    sponsor = models.CharField(max_length=500, null=True)
    introduce_date = models.CharField(max_length=100, null=True)
    committees = models.CharField(max_length=500, null=True)
    became_law_date = models.CharField(max_length=100, null=False)
    number = models.CharField(max_length=100, null=True)
    text = models.TextField(null=True)
    pdf_url = models.CharField(max_length=500, null=True,default=None)
    text_url = models.CharField(max_length=500, null=True,default=None)
    type = models.CharField(max_length=100, null=True)
    summary = models.TextField(null=True)

    def __str__(self):
        return f'{self.title} ({self.url})'

    class Meta:
        unique_together = (('code_name', 'congress'),)
