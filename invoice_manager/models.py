from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = (
    ('VAT', 'VAT'),
    ('SVAT', 'SVAT'),
    ('NON-VAT', 'NON-VAT'),
)

def invoice_upload_path(instance, filename):
    now = datetime.now()
    category = instance.category or 'uncategorized'
    return f"invoices/{category}/{now.strftime('%Y-%m')}/{filename}"

class Invoice(models.Model):
    file = models.FileField(upload_to=invoice_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='VAT')

    code = models.CharField(max_length=50, unique=True, blank=True, null=True)  # VILTS-41816 etc.
    file_hash = models.CharField(max_length=64, blank=True, null=True)  # MD5 hash of file

    def __str__(self):
        return f"{self.code or self.file.name} - {self.category}"
