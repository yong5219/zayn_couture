import django.db

class Transaction(django.db.models.Model):
    created = django.db.models.DateTimeField(auto_now_add=True)
    approved = django.db.models.DateTimeField(null=True)
    # Needed upon creation
    RefNo = django.db.models.CharField(max_length=255)
    Amount = django.db.models.DecimalField(max_digits=10, decimal_places=2)
    Currency = django.db.models.CharField(max_length=5)
    # Received from iPay88
    Remark = django.db.models.CharField(max_length=100, default='')
    TransId = django.db.models.CharField(max_length=30, default='')
    AuthCode = django.db.models.CharField(max_length=20, default='')
    Status = django.db.models.CharField(max_length=1, default='0')
    ErrDesc = django.db.models.CharField(max_length=100, default='')
    Signature = django.db.models.CharField(max_length=100, default='')


