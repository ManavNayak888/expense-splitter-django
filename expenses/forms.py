from django import forms
from .models import Expense, Group
from django.contrib.auth.models import User

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Trip to Goa, Flat expenses...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'What is this group for?',
                'rows': 3
            }),
        }
        labels = {
            'name': 'Group Name',
            'description': 'Description (optional)'
        }

class ExpenseForm(forms.ModelForm):
    paid_by = forms.ModelChoiceField(
        queryset=User.objects.none(),  # dynamically set in view
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Paid by'
    )

    class Meta:
        model = Expense
        fields = ['description', 'paid_by', 'amount']
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
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username to add...'
        })
    )