from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_csv, name='upload_csv'),
    path('datasets/', views.dataset_list, name='dataset_list'),
    path('datasets/<int:dataset_id>/summary/', views.dataset_summary, name='dataset_summary'),
    path('datasets/<int:dataset_id>/equipment/', views.equipment_list, name='equipment_list'),
    path('datasets/<int:dataset_id>/pdf/', views.generate_pdf, name='generate_pdf'),
]
