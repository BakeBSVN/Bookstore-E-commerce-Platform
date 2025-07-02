from django.db import models


# Create your models here.


class Payment_VNPay(models.Model):
    order_id = models.IntegerField(default=0,null=True, blank=True)
    amount = models.FloatField(default=0.0, null=True, blank=True)
    oder_desc = models.CharField(max_length=100, null=True, blank=True)
    vnp_TransactionNo = models.CharField(max_length=100, null=True, blank=True)
    vnp_ResponseCode = models.CharField(max_length=100, null=True, blank=True)




