import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_broker = models.BooleanField(default=False)

class Client(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE, primary_key= True)
    client_id = models.UUIDField(default= uuid.uuid4, editable= False)

    def __str__(self):
        return self.user.username

    def get_portfolios_values(self):
        ''''''
        portfolios = self.portfolios.all()
        for portfolio in portfolios:
            portfolio.current_value = round(portfolio.get_value(), 2)
        return portfolios

class Broker(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE, primary_key= True)
    broker_id = models.UUIDField(default= uuid.uuid4, editable= False)

    def __str__(self):
        return self.user.username