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


class Doc(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.TextField(null=False)
    date = models.CharField(max_length=50, null=True)
    # url = models.CharField(max_length=256, null=False, unique=True)
    text = models.TextField(null=True, blank=True)
    labels = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, null=True)
    tickets_loaded = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.title}:({self.url})'
    
class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(null=False)
    text = models.TextField(null=True, blank=True)
    doc = models.ForeignKey(Doc, on_delete = models.CASCADE)
    keywords = models.TextField(null=True)
    types = models.TextField(null=True)
    
    
    def __str__(self):
        return f'{self.title} ({self.url})'
