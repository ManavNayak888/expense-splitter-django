from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, Expense
from .forms import ExpenseForm, AddMemberForm

@login_required
def dashboard(request):
    groups = Group.objects.filter(members=request.user)
    recent_expenses = Expense.objects.filter(group__members= request.user).order_by('-date')[:5]
    context = {
        'groups': groups,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'expenses/dashboard.html',context)

@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            group = Group.objects.create(name= name, description= description, created_by= request.user)
            group.members.add(request.user)
            messages.success(request,f'Group "{name}" created successfully')
            return redirect('dashboard')
    return render(request,'expenses/create_group.html')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    expenses = group.expenses.all().order_by('-date')
    
    # Calculate balances and settlements
    balances = group.calculate_balances()  # Get member balances
    settlements = group.get_settlements()  # Get settlement suggestions
    
    context = {
        'group': group,
        'expenses': expenses,
        'balances': balances,
        'settlements': settlements,
    }
    return render(request, 'expenses/group_detail.html', context)

@login_required
def create_expense(request, group_id):
    group = get_object_or_404(Group, id= group_id, members= request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense= form.save(commit= False)
            expense.paid_by = request.user
            expense.group = group
            expense.save()
            messages.success(request, f'Expense "{expense.description}" added successfully!')
            return redirect('group_detail', group_id= group.id)
    else:
        form= ExpenseForm()
    
    context = {
        'form': form,
        'group': group,
        }
    return render(request, 'expenses/create_expense.html', context)

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id= expense_id, group__members= request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance = expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense Updated Successfully!')
            return redirect('group_detail', group_id= expense.group.id)
    else:
        form = ExpenseForm(instance= expense)
    return render(request, 'expenses/edit_expense.html',{'form': form, 'expense': expense})

@login_required
def delete_expense(request, expense_id):
    expense= get_object_or_404(Expense, id= expense_id, group__members= request.user)
    group_id = expense.group.id
    if request.method == "POST":
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('group_detail', group_id= group_id)
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id= group_id)

    if not group.can_manage_members(request.user):
        messages.error(request, 'only group creater can add members.')
        return redirect('group_detail', group_id= group.id)

    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_add= User.objects.get(username= username)
                if user_to_add in group.members.all():
                    messages.warning(request, f'{username} is already in the group.')
                else:
                    group.members.add(user_to_add)
                    messages.success(request, f'{username} added to group!')
                    return redirect('group_detail', group_id= group.id)
            except User.DeosNotExist:
                messages.error(request, f'User {username} not found.')
    else:
        form= AddMemberForm()
    return render(request, 'expenses/add_member.html', {'form': form, 'group': group})

from django.contrib.auth.models import User
from .forms import ExpenseForm, AddMemberForm

@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if not group.can_manage_members(request.user):  # Check permission
        messages.error(request, 'Only group creator can add members.')
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_add = User.objects.get(username=username)  # Find user by username
                if user_to_add in group.members.all():
                    messages.warning(request, f'{username} is already in the group.')
                else:
                    group.members.add(user_to_add)  # Add user to group members
                    messages.success(request, f'{username} added to group!')
                    return redirect('group_detail', group_id=group.id)
            except User.DoesNotExist:
                messages.error(request, f'User "{username}" not found.')
    else:
        form = AddMemberForm()
    
    return render(request, 'expenses/add_member.html', {'form': form, 'group': group})

@login_required
def remove_member(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    if not group.can_manage_members(request.user):  # Check permission
        messages.error(request, 'Only group creator can remove members.')
        return redirect('group_detail', group_id=group.id)
    
    if user_to_remove == group.created_by:
        messages.error(request, 'Cannot remove group creator.')
    elif user_to_remove in group.members.all():
        group.members.remove(user_to_remove)  # Remove user from group
        messages.success(request, f'{user_to_remove.username} removed from group.')
    else:
        messages.error(request, 'User not in group.')
    
    return redirect('group_detail', group_id=group.id) 


@login_required
def delete_group(request, group_id):
    """Delete a group (only group creator can do this)"""
    group = get_object_or_404(Group, id=group_id, created_by=request.user)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()  # Delete the group and all its expenses
        messages.success(request, f'Group "{group_name}" deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'expenses/delete_group.html', {'group': group})

@login_required
def leave_group(request, group_id):
    """Leave a group (members can leave, creator cannot)"""
    group = get_object_or_404(Group, id=group_id, members=request.user)
    
    if request.user == group.created_by:
        messages.error(request, 'Group creator cannot leave the group. Delete the group instead.')
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        group.members.remove(request.user)
        messages.success(request, f'You left "{group.name}"')
        return redirect('dashboard')
    
    return render(request, 'expenses/leave_group.html', {'group': group})
                

    




