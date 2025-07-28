from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import User
# OR, if using a custom user model:
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=150, blank=True, default='Unknown')  # ✅
    last_name = models.CharField(max_length=150, blank=True, default='Unknown')   # ✅
    email = models.EmailField(max_length=100, blank=True, unique=True, null=True)
    phone = models.CharField(verbose_name=_("Mobile phone"), max_length=14, blank=True, null=True, unique=True)
    photo = models.ImageField(verbose_name=_("Photo"), upload_to='users/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class Station(models.Model):
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, {self.place}" if self.place else self.name

class ClassType(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name





from django.db import models
from django.utils.translation import gettext_lazy as _

class Train(models.Model):
    name = models.CharField(
        verbose_name=_("Train Name"),
        max_length=255,
        null=True,
        blank=True
    )
    nos = models.PositiveIntegerField(
        verbose_name=_("Number of Seats"),
        null=True,
        blank=True,
        help_text=_("Total number of available seats on the train")
    )
    source = models.ForeignKey(
        'Station',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='departing_trains',
        verbose_name=_("Source Station")
    )
    destination = models.ForeignKey(
        'Station',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='arriving_trains',
        verbose_name=_("Destination Station")
    )
    departure_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Departure Time")
    )
    arrival_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Arrival Time")
    )
    class_type = models.ManyToManyField(
        'ClassType',
        blank=True,
        verbose_name=_("Class Types"),
        help_text=_("Select all available classes for this train")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name if self.name else "Unnamed Train"

    class Meta:
        verbose_name = _("Train")
        verbose_name_plural = _("Trains")
        ordering = ['name']


class Booking(models.Model):
    status_choices = (
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Canceled", "Canceled"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    booking_date = models.DateField(auto_now_add=True, null=True, blank=True)
    booking_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=50, default='Pending', choices=status_choices, null=True, blank=True)
    train_name = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    destination = models.CharField(max_length=100, null=True, blank=True)
    departure_time = models.CharField(max_length=50, null=True, blank=True)
    arrival_time = models.CharField(max_length=50, null=True, blank=True)
    # class_type = models.CharField(max_length=50, null=True, blank=True)
    
    class_type = models.ForeignKey(ClassType, null=True, blank=True, on_delete=models.SET_NULL)

    total_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    passengers_adult = models.IntegerField(null=True, blank=True)
    passengers_child = models.IntegerField(null=True, blank=True)
    payment_code = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    travel_date = models.DateField(null=True, blank=True)
    travel_dt = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user.username if self.user else 'Anonymous'}"





class BillingInfo(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Billing for Booking {self.booking.id}"





class BookingDetail(models.Model):
    booking = models.OneToOneField(Booking, null=True, blank=True, on_delete=models.CASCADE)
    train = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    destination = models.CharField(max_length=255, null=True, blank=True)
    travel_date = models.DateField(null=True, blank=True)
    travel_time = models.TimeField(null=True, blank=True)
    nop = models.PositiveIntegerField(verbose_name=_("Number of Passengers"), null=True, blank=True)
    adult = models.PositiveIntegerField(null=True, blank=True)
    child = models.PositiveIntegerField(null=True, blank=True)
    class_type = models.CharField(max_length=255, null=True, blank=True)
    fpp = models.PositiveIntegerField(verbose_name=_("Fare Per Passenger"), null=True, blank=True)
    total_fare = models.PositiveIntegerField(null=True, blank=True)

    travel_dt = models.DateTimeField(blank=True, null=True)
    booking_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class Payment(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pay_amount = models.CharField(max_length=10)
    pay_method = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    trxid = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='Paid', auto_created=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


    def __str__(self):
        return f"Payment for Booking {self.booking.id}"



class Ticket(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure = models.CharField(max_length=50)
    travel_date = models.DateField()
    train_name = models.CharField(max_length=100)
    class_type = models.CharField(max_length=50)
    fare = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Ticket for Booking {self.booking.id}"





class MpesaTransaction(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    checkout_request_id = models.CharField(max_length=100)
    merchant_request_id = models.CharField(max_length=100)
    trx_id = models.CharField(max_length=100, null=True, blank=True)
    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_desc = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"MPesa Transaction for Booking {self.booking.id if self.booking else 'None'}"



class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True) 

    def __str__(self):
        return f"Contact from {self.name}"


   


class ContactNumber(models.Model):
    phone = models.CharField(max_length=20)
    station = models.OneToOneField(Station, on_delete=models.CASCADE, null=True, blank=True)
    station_phone = models.CharField(verbose_name=_("Station Phone Number"), max_length=255, null=True, blank=True)
    emergency_center = models.CharField(verbose_name=_("Emergency Center Phone Number"), max_length=255, null=True, blank=True)
    help_desk = models.CharField(verbose_name=_("Help Desk Phone Number"), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    feedback = models.TextField()

    def __str__(self):
        return f"Feedback from {self.name}"