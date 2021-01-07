import datetime

from django.db import models
from django.core.cache import cache

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        
        return cache.get(cls.__name__)

class SiteSettings(SingletonModel):
    db_default_date = models.DateTimeField(
        default=datetime.datetime(1,1,1,0,0,0, tzinfo=datetime.timezone.utc)
    )
    monetary_decimal_places = models.PositiveIntegerField(
        default= 6
    )
    db_date_format = models.CharField(
        max_length= 20, 
        default='%Y-%m-%d %H:%M:%S'
    )

class StockManagementSettings(SingletonModel):
    internal_value_threshold = models.DecimalField(
        default= 100000, 
        max_digits= 18, 
        decimal_places= 6,
        help_text= 'Amount in USD at which to halt processing of an internal stock order.'
    )
    external_value_threshold = models.DecimalField(
        default= 1000000, 
        max_digits= 18, 
        decimal_places= 6,
        help_text= 'Amount in USD at which to halt processing of an external stock order.'
    )
    internal_share_proportion_threshold = models.DecimalField(
        default= 0.1,
        max_digits= 18,
        decimal_places= 6,
        help_text= 'Fraction of order shares over internally held shares at which to halt processing of an internal stock order.'
    )
    external_share_proportion_threshold = models.DecimalField(
        default= 0.1,
        max_digits= 18,
        decimal_places= 6,
        help_text= 'Fraction of order shares over externally held shares at which to halt processing of an external stock order'
    )
    internal_short_share_threshold = models.IntegerField(
        default= 1000,
        help_text= 'The maximum allowable share deficit.'
    )

    def __str__(self):
        return 'StockManagementSettings'

    def does_pass_internal_checks(self, order, outstanding_shares=1000000):
        return (
            (order.price * order.quantity < self.internal_value_threshold) and 
            (order.quantity / outstanding_shares < self.internal_share_proportion_threshold) 
        )

    def does_pass_external_checks(self, order, outstanding_shares):
        return (
            (order.price * order.quantity < self.external_value_threshold) and
            (order.quantity / outstanding_shares < self.external_share_proportion_threshold) 
        )