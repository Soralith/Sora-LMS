from django.urls import path
from . import views
from apps.komunitas import views as komunitas_views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.course_create, name='course_create'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('<slug:slug>/delete/', views.course_delete, name='course_delete'),
    path('<slug:slug>/enrollments/', views.manage_enrollments, name='manage_enrollments'),
    path('<slug:slug>/teachers/', views.assign_teachers, name='assign_teachers'),
    path('<slug:slug>/community/', komunitas_views.course_community, name='course_community'),
    path('<slug:slug>/community/messages/', komunitas_views.course_community_message_list, name='course_community_messages'),
    path('<slug:slug>/community/post/', komunitas_views.course_community_post_message, name='course_community_post'),
    path('<slug:slug>/module/create/', views.module_create, name='module_create'),
    path('<slug:slug>/announce/', views.announcement_create, name='announcement_create'),
    path('module/<int:pk>/edit/', views.module_edit, name='module_edit'),
    path('module/<int:pk>/delete/', views.module_delete, name='module_delete'),
    path('module/<int:module_pk>/material/create/', views.material_create, name='material_create'),
    path('material/<int:pk>/', views.material_detail, name='material_detail'),
    path('material/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('material/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('material/<int:material_pk>/comment/add/', views.comment_add, name='comment_add'),
    path('comment/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
]
