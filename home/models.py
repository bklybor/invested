import uuid
import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_broker = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)

class Company(SingletonModel):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    name = models.CharField(max_length=100, default= 'The Company')
    established = models.CharField(max_length=15, default='2000-01-01')
    company_id = models.CharField(max_length= 100, default='company_id')
    
    def __str__(self):
        return self.name

class Client(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE, primary_key= True)
    client_id = models.UUIDField(default= uuid.uuid4, editable= False)

    def __str__(self):
        return self.user.username

    def get_portfolios_values(self):
        ''''''
        portfolios = self.portfolios.all()
        for portfolio in portfolios:
            portfolio.current_value = portfolio.get_value_at_datetime()
        return portfolios

class Broker(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE, primary_key= True)
    broker_id = models.UUIDField(default= uuid.uuid4, editable= False)

    def __str__(self):
        return self.user.username



