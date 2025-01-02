from django.urls import path
from . import views
from .views import custom_403_view

handler403 = custom_403_view
app_name = 'board'

urlpatterns = [
    path('', views.RecListView.as_view(), name='info-list'),
    path('create/', views.RecCreateView.as_view(), name='r-create'),
    path('info/<int:pk>/', views.RecDetailView.as_view(), name='info_detail'),
    path('info/<int:pk>/update/', views.RecUpdateView.as_view(), name='info-update'),
    path('info/<int:pk>/delete/', views.RecDeleteView.as_view(), name='info-delete'),
    path('board3/', views.board3_view, name='board3'),
    path('list2/', views.RestaurantListView.as_view(), name='info-list2'),
    path('info2/<int:pk>/', views.RestaurantDetailView.as_view(), name='info_detail2'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment2/<int:comment_id>/edit/', views.edit_comment2, name='edit_comment2'),
    path('comment2/<int:comment_id>/delete/', views.delete_comment2, name='delete_comment2'),
]