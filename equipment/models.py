
from django.db import models
from django.contrib.auth.models import User


class Equipment(models.Model):

    COUNTY_CHOICES = [
        ('Baringo', 'Baringo'),
        ('Bomet', 'Bomet'),
        ('Bungoma', 'Bungoma'),
        ('Busia', 'Busia'),
        ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'),
        ('Embu', 'Embu'),
        ('Garissa', 'Garissa'),
        ('Homa Bay', 'Homa Bay'),
        ('Isiolo', 'Isiolo'),
        ('Kajiado', 'Kajiado'),
        ('Kakamega', 'Kakamega'),
        ('Kericho', 'Kericho'),
        ('Kiambu', 'Kiambu'),
        ('Kilifi', 'Kilifi'),
        ('Kirinyaga', 'Kirinyaga'),
        ('Kisii', 'Kisii'),
        ('Kisumu', 'Kisumu'),
        ('Kitui', 'Kitui'),
        ('Kwale', 'Kwale'),
        ('Laikipia', 'Laikipia'),
        ('Lamu', 'Lamu'),
        ('Machakos', 'Machakos'),
        ('Makueni', 'Makueni'),
        ('Mandera', 'Mandera'),
        ('Marsabit', 'Marsabit'),
        ('Meru', 'Meru'),
        ('Migori', 'Migori'),
        ('Mombasa', 'Mombasa'),
        ('Murang’a', 'Murang’a'),
        ('Nairobi', 'Nairobi'),
        ('Nakuru', 'Nakuru'),
        ('Nandi', 'Nandi'),
        ('Narok', 'Narok'),
        ('Nyamira', 'Nyamira'),
        ('Nyandarua', 'Nyandarua'),
        ('Nyeri', 'Nyeri'),
        ('Samburu', 'Samburu'),
        ('Siaya', 'Siaya'),
        ('Taita-Taveta', 'Taita-Taveta'),
        ('Tana River', 'Tana River'),
        ('Tharaka-Nithi', 'Tharaka-Nithi'),
        ('Trans Nzoia', 'Trans Nzoia'),
        ('Turkana', 'Turkana'),
        ('Uasin Gishu', 'Uasin Gishu'),
        ('Vihiga', 'Vihiga'),
        ('Wajir', 'Wajir'),
        ('West Pokot', 'West Pokot'),
    ]

    RENTAL_PERIOD_CHOICES = [
        ('HOUR', 'Per Hour'),
        ('DAY', 'Per Day'),
        ('MONTH', 'Per Month'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='equipment_listings',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    description = models.TextField()

    image = models.ImageField(
        upload_to='equipment/',
        blank=True,
        null=True
    )

    category = models.CharField(max_length=100)

    county = models.CharField(
        max_length=100,
        choices=COUNTY_CHOICES,
        blank=True
    )

    town = models.CharField(
        max_length=100,
        blank=True
    )

    area = models.CharField(
        max_length=150,
        blank=True
    )

    rental_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    rental_period = models.CharField(
        max_length=10,
        choices=RENTAL_PERIOD_CHOICES,
        default='DAY'
    )

    available = models.BooleanField(default=True)

    def get_formatted_price(self):
        return f"KSh {self.rental_price:,.2f} {self.get_rental_period_display().lower()}"

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


class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    rental_request = models.ForeignKey(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"


class Conversation(models.Model):

    rental_request = models.OneToOneField(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name='conversation'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation for {self.rental_request}"


class ChatMessage(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_chat_messages'
    )

    content = models.TextField()

    is_read = models.BooleanField(default=False)

    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:40]}"
