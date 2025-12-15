from django.urls import path
from . import views

urlpatterns =[
    path('', views.dashboard, name='dashboard'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/delete/', views.delete_group, name='delete_group'),  
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('groups/<int:group_id>/expense/create/', views.create_expense, name='create_expense'),
    path('expenses/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('expenses/<int:group_id>/add-member/', views.add_member, name='add_member'),
    path('groups/<int:group_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),

]