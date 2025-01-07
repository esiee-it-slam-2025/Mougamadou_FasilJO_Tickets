import uuid
from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum')
    ]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4)
    event = models.ForeignKey('Event', on_delete=models.PROTECT)  # PROTECT pour éviter la suppression accidentelle d'un événement avec des billets
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)  # Pour tracker si le billet a déjà été scanné

    def get_price_for_category(category):
        prices = {
            'SILVER': 100,
            'GOLD': 200,
            'PLATINUM': 300
        }
        return prices.get(category)

    def __str__(self):
        return f"Ticket {self.id} - {self.event} ({self.category})"