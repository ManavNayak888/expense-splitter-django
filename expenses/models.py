from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='expense_groups')
    created_by = models.ForeignKey(User, on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    description = models.CharField(max_length= 200)
    amount =models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date =models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.description} - {self.amount}"


