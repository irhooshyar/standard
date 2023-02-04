import sys

try:
    from django.db import models
except Exception as e:
    print(f'Exception: Django Not Found, please install it with "pip install django". (error{e})')
    sys.exit()


# Sample User model
class Page(models.Model):
    url = models.CharField(max_length=500, null=False)
    config = models.JSONField(default=dict)
    status = models.TextField(null=False)
    # count = models.IntegerField(null=False)

    def __str__(self):
        return self.url


class Legislation(models.Model):
    id = models.BigIntegerField(primary_key=True)
    statement_digest = models.TextField(null=True)
    judgment_number = models.CharField(max_length=50, null=True)
    judgment_approve_date_persian = models.CharField(max_length=50, null=True)
    complaint_serial = models.CharField(max_length=50, null=True)
    conclusion_display_name = models.CharField(max_length=255, null=True)

    subject_type_display_name = models.CharField(max_length=255, null=True)
    judgment_type = models.CharField(max_length=255, null=True)
    content = models.TextField(null=True)
    complainant = models.CharField(max_length=255, null=True)
    complaint_from = models.CharField(max_length=255, null=True)
    laws = models.TextField(null=True)
    categories = models.TextField(null=True)

    def __str__(self):
        return f'{self.title} ({self.url})'
