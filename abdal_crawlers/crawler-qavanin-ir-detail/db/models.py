import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


# Sample User model
class Law(models.Model):
    pid = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=5000)
    approve = models.CharField(max_length=500)
    data = models.CharField(max_length=50)
    noe_ghanon = models.CharField(max_length=500)
    tabaghe_bandi = models.CharField(max_length=500)
    tarikh_sanad_tasvib = models.CharField(max_length=500)
    shomare_sanad_tasvib = models.CharField(max_length=500)
    shomare_eblagh = models.CharField(max_length=500)
    tarikh_eblagh = models.CharField(max_length=500)
    marjae_eblagh = models.CharField(max_length=500)
    tarikh_ejra = models.CharField(max_length=500)
    akharin_vaziat = models.CharField(max_length=500)
    dastgah_mojri = models.CharField(max_length=500)
    ronevesht = models.CharField(max_length=500)
    has_text = models.CharField(max_length=10)
    status = models.CharField(max_length=10, default='empty')

    def __str__(self):
        return self.name
