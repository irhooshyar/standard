import sys

try:
    from django.db import models
except Exception as e:
    print(f'Exception: Django Not Found, please install it with "pip install django". (error{e})')
    sys.exit()


# Sample User model
class Page(models.Model):
    url = models.CharField(max_length=50, null=False)
    num = models.IntegerField(null=False)

    def __str__(self):
        return self.url

    class Meta:
        unique_together = (('url', 'num'),)


class Act(models.Model):
    title = models.CharField(max_length=500, null=False)
    url = models.CharField(max_length=50, null=False, unique=True)
    number = models.CharField(max_length=100, null=True, blank=True)
    note = models.BooleanField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.title} ({self.url})'
