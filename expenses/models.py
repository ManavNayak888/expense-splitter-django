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
        for member in self.members.all():
            # Total amount member paid - FIXED: use 'amount__sum'
            total_paid_result = self.expenses.filter(paid_by=member).aggregate(
                total_paid=Sum('amount')
            )
            total_paid = total_paid_result['total_paid'] or Decimal('0.00')
            
            # Total amount member should pay (their share of all expenses)
            total_share = Decimal('0.00')
            for expense in self.expenses.all():
                total_share += expense.split_equally()
            
            # Net balance (positive = owed money, negative = owes money)
            balances[member] = total_paid - total_share
        
        return balances
    
    def get_settlements(self):
        """Calculate who should pay whom to settle all debts"""
        balances = self.calculate_balances()
        debtors = []
        creditors = []
        
        # Separate debtors (negative balance) and creditors (positive balance)
        for member, balance in balances.items():
            if balance < 0:  # Owes money
                debtors.append({'member': member, 'amount': -balance})
            elif balance > 0:  # Owed money  
                creditors.append({'member': member, 'amount': balance})
        
        # Calculate settlements (simplified algorithm)
        settlements = []
        for debtor in debtors:
            for creditor in creditors:
                if creditor['amount'] > 0 and debtor['amount'] > 0:
                    # Determine settlement amount
                    amount = min(creditor['amount'], debtor['amount'])
                    if amount > 0:
                        settlements.append({
                            'from_user': debtor['member'],
                            'to_user': creditor['member'],
                            'amount': amount
                        })
                        # Update remaining amounts
                        creditor['amount'] -= amount
                        debtor['amount'] -= amount
        
        return settlements

class Expense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"

    def split_equally(self):
        members_count = self.group.members.count()
        if members_count > 0:
            return self.amount / members_count
        return Decimal('0.00')
