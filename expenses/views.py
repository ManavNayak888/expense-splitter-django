from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Group, Expense, Settlement
from .forms import ExpenseForm, AddMemberForm, GroupForm  # added GroupForm

@login_required
def dashboard(request):
    groups = Group.objects.filter(members=request.user)
    recent_expenses = Expense.objects.filter(group__members=request.user).order_by('-date')[:5]
    context = {
        'groups': groups,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'expenses/dashboard.html', context)

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)          # now using GroupForm
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('dashboard')
    else:
        form = GroupForm()
    return render(request, 'expenses/create_group.html', {'form': form})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    expenses = group.expenses.all().order_by('-date')
    balances = group.calculate_balances()
    settlements = group.get_settlements()
    context = {
        'group': group,
        'expenses': expenses,
        'balances': balances,
        'settlements': settlements,
    }
    return render(request, 'expenses/group_detail.html', context)

@login_required
def create_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        form.fields['paid_by'].queryset = group.members.all()
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.created_by = request.user  # ← track who added it
            expense.save()
            messages.success(request, f'Expense "{expense.description}" added successfully!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = ExpenseForm()
        form.fields['paid_by'].queryset = group.members.all()
        form.initial['paid_by'] = request.user  # ← default to logged in user
    return render(request, 'expenses/create_expense.html', {'form': form, 'group': group})

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    # Only the person who added the expense can edit it
    if expense.created_by != request.user:
        messages.error(request, 'You can only edit expenses you added.')
        return redirect('group_detail', group_id=expense.group.id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        form.fields['paid_by'].queryset = expense.group.members.all()
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('group_detail', group_id=expense.group.id)
    else:
        form = ExpenseForm(instance=expense)
        form.fields['paid_by'].queryset = expense.group.members.all()
    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    # Only the person who added the expense can delete it
    if expense.created_by != request.user:
        messages.error(request, 'You can only delete expenses you added.')
        return redirect('group_detail', group_id=expense.group.id)

    group_id = expense.group.id
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('group_detail', group_id=group_id)
    return render(request, 'expenses/delete_expense.html', {'expense': expense})

@login_required
def add_member(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if not group.can_manage_members(request.user):
        messages.error(request, 'Only group creator can add members.')
        return redirect('group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_add = User.objects.get(username=username)
                if user_to_add in group.members.all():
                    messages.warning(request, f'{username} is already in the group.')
                else:
                    group.members.add(user_to_add)
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
    
    if not group.can_manage_members(request.user):
        messages.error(request, 'Only group creator can remove members.')
        return redirect('group_detail', group_id=group.id)
    
    if user_to_remove == group.created_by:
        messages.error(request, 'Cannot remove group creator.')
    elif user_to_remove in group.members.all():
        group.members.remove(user_to_remove)
        messages.success(request, f'{user_to_remove.username} removed from group.')
    else:
        messages.error(request, 'User not in group.')
    
    return redirect('group_detail', group_id=group.id)

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, created_by=request.user)
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Group "{group_name}" deleted successfully!')
        return redirect('dashboard')
    return render(request, 'expenses/delete_group.html', {'group': group})

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    if request.user == group.created_by:
        messages.error(request, 'Group creator cannot leave. Delete the group instead.')
        return redirect('group_detail', group_id=group.id)
    if request.method == 'POST':
        group.members.remove(request.user)
        messages.success(request, f'You left "{group.name}"')
        return redirect('dashboard')
    return render(request, 'expenses/leave_group.html', {'group': group})

@login_required
def settle_up(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    settlements = group.get_settlements()

    user_settlement = None
    for settlement in settlements:
        if settlement['from_user'] == request.user:
            user_settlement = settlement
            break

    if not user_settlement:
        messages.info(request, "You don't owe anything in this group.")
        return redirect('group_detail', group_id=group.id)

    if request.method == 'POST':
        # Re-check settlements at POST time to avoid double recording
        fresh_settlements = group.get_settlements()
        fresh_user_settlement = None
        for s in fresh_settlements:
            if s['from_user'] == request.user:
                fresh_user_settlement = s
                break

        if not fresh_user_settlement:
            messages.info(request, "You don't owe anything in this group.")
            return redirect('group_detail', group_id=group.id)

        Settlement.objects.create(
            group=group,
            from_user=fresh_user_settlement['from_user'],
            to_user=fresh_user_settlement['to_user'],
            amount=fresh_user_settlement['amount'],
            note=request.POST.get('note', '')
        )
        messages.success(request, f'Payment of ₹{fresh_user_settlement["amount"]} recorded successfully!')
        return redirect('group_detail', group_id=group.id)

    return render(request, 'expenses/settle_up.html', {
        'group': group,
        'settlement': user_settlement
    })


@login_required
def settlement_history(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    settlements = group.settlements.all().order_by('-date')
    return render(request, 'expenses/settlement_history.html', {
        'group': group,
        'settlements': settlements
    })
