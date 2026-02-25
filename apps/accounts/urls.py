from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),      # /  -> login (yoki redirect)
    path("login/", views.login_view, name="login_page"),  # xohlasangiz alohida url
    path("logout/", views.logout_view, name="logout"),

    path("superadmin/admins/", views.superadmin_admin_list, name="superadmin_admin_list"),
    path("superadmin/admins/create/", views.superadmin_admin_create, name="superadmin_admin_create"),
    path("superadmin/admins/<int:user_id>/toggle/", views.superadmin_admin_toggle_block, name="superadmin_admin_toggle"),
    path("superadmin/admins/<int:user_id>/delete/", views.superadmin_admin_delete, name="superadmin_admin_delete"),

    path("p/admin/", views.admin_dashboard, name="admin_dashboard"),
]