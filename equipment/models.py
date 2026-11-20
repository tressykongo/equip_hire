
from django.db import models
from django.contrib.auth.models import User


class Equipment(models.Model):

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='equipment_listings',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)
    category = models.CharField(max_length=100)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class RentalRequest(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='rental_requests'
    )

    renter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rental_requests'
    )

    message = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.renter.username} - {self.equipment.name}"
