from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import Sum

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='expense_groups')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    def can_manage_members(self, user):
        return user == self.created_by

    def calculate_balances(self):
        """Calculate net balance for each member in the group"""
        balances = {}
        members_count = self.members.count()

        for member in self.members.all():
            # Total amount this member paid for expenses
            total_paid_result = self.expenses.filter(paid_by=member).aggregate(
                total_paid=Sum('amount')
            )
            total_paid = total_paid_result['total_paid'] or Decimal('0.00')

            # Total share this member owes across all expenses
            total_share = Decimal('0.00')
            if members_count > 0:
                for expense in self.expenses.all():
                    total_share += expense.amount / members_count

            # Settlements this member has made (they paid someone)
            settlements_paid = self.settlements.filter(from_user=member).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')

            # Settlements this member has received (someone paid them)
            settlements_received = self.settlements.filter(to_user=member).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')

            # Net balance
            balances[member] = total_paid - total_share  + settlements_paid - settlements_received 

        return balances
    
    def get_settlements(self):
        """Calculate who should pay whom to settle all debts"""
        balances = self.calculate_balances()
        debtors = []
        creditors = []
        
        for member, balance in balances.items():
            if balance < 0:
                debtors.append({'member': member, 'amount': -balance})
            elif balance > 0:
                creditors.append({'member': member, 'amount': balance})
        
        settlements = []
        for debtor in debtors:
            for creditor in creditors:
                if creditor['amount'] > 0 and debtor['amount'] > 0:
                    amount = min(creditor['amount'], debtor['amount'])
                    if amount > 0:
                        settlements.append({
                            'from_user': debtor['member'],
                            'to_user': creditor['member'],
                            'amount': amount
                        })
                        creditor['amount'] -= amount
                        debtor['amount'] -= amount
        
        return settlements

class Expense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expense_createed",null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.description} - ₹{self.amount}"

    def split_equally(self):
        members_count = self.group.members.count()
        if members_count > 0:
            return self.amount / members_count
        return Decimal('0.00')


class Settlement(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_made')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_recieved')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} paid {self.to_user.username} ₹{self.amount}"