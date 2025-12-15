from django import forms
from .models import Expense
from django.contrib.auth.models import User

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dinner, Rent, Groceries...'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }
        labels = {
            'description': 'What was this expense for?',
            'amount': 'Amount (₹)'
        }

class AddMemberForm(forms.Form):
    username = forms.CharField(max_length= 150, widget= forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Enter username to add...'
    })
    ) 