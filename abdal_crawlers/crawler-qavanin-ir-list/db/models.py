import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


# Sample User model
class Law(models.Model):
    name = models.CharField(max_length=5000)
    approve = models.CharField(max_length=500)
    data = models.CharField(max_length=50)
    pid = models.IntegerField(unique=True,primary_key=True)

    def __str__(self):
        return self.name

