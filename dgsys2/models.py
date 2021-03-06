from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum


class Membership(models.Model):
    label = models.CharField(max_length=32)

    def __str__(self):
        return self.label


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    membership = models.ForeignKey(Membership, on_delete=models.SET_DEFAULT, null=False, default=1)
    membership_expiry = models.DateTimeField(null=True)
    address = models.TextField(null=True, verbose_name="Address Line")
    zip_code = models.IntegerField(null=True, verbose_name='Zip Code')
    phone = models.IntegerField(null=True)
    city = models.TextField(null=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def is_member(self):
        return self.membership.id > 0

    def membership_label(self):
        return self.membership.label

    def account_balance(self):
        total_payments = get_sum_of_objects_per_user(Payment, 'amount', self)
        total_purchases = get_sum_of_objects_per_user(ItemPurchase, 'total', self)
        total_rentals = get_sum_of_objects_per_user(Rental, 'amount', self)

        return total_payments - total_purchases - total_rentals

    def __str__(self):
        return self.email + " / " + self.membership.label


class EquipmentCategory(models.Model):
    label = models.CharField(max_length=16)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Equipment Category'
        verbose_name_plural = 'Equipment Categories'


class Equipment(models.Model):
    category = models.ForeignKey(EquipmentCategory, on_delete=models.SET_NULL, null=True)
    label = models.CharField(max_length=16, unique=True)
    description = models.TextField(max_length=512)

    class Meta:
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return self.label


class EquipmentPrice(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    equipment_article = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='prices')
    price = models.FloatField()

    class Meta:
        unique_together = ('equipment_article', 'membership')

    def __str__(self):
        return self.membership.label + " / " + self.equipment_article.label


class Reservation(models.Model):
    equipment_articles = models.ManyToManyField(Equipment)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " / " + str(self.start_date)


class Rental(models.Model):
    equipment_articles = models.ManyToManyField(Equipment)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    estimated_end = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField(default=0, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField(default="", blank=True)

    def __str__(self):
        return self.user.username + " / " + str(self.start_date) + " / " + str(self.amount)


class Item(models.Model):
    label = models.CharField(max_length=32)
    rental_related = models.BooleanField(verbose_name='Associated to rentals')
    price_per_unit = models.BooleanField(verbose_name='Show number input in app')

    def __str__(self):
        return self.label


class ItemPrice(models.Model):
    price = models.FloatField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)


    class Meta:
        unique_together = ('item', 'membership')

    def __str__(self):
        return self.item.label + " / " + self.membership.label


class ItemPurchase(models.Model):
    item = models.ForeignKey(ItemPrice, null=False, default=1, on_delete=models.SET_DEFAULT, verbose_name='Item')
    amount = models.FloatField()
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total = models.FloatField()

    def item_purchase_price(self):
        return self.amount * self.item.price

    def __str__(self):
        return self.item.item.label + \
               " / " + self.user.get_full_name() + \
               " / " + str(self.item.price * self.amount) + "kr"


def get_sum_of_objects_per_user(table, key, user):
    amount = table.objects.filter(user=user).aggregate(Sum(key))[(key+'__sum')]
    if amount is None:
        amount = 0
    return amount


class Payment(models.Model):
    amount = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    explanation = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.user.email + " / " + str(self.date)

