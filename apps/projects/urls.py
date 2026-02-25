from . import views
from . import api_views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Kichik admin
    path("p/admin/projects/", views.admin_project_list, name="admin_project_list"),
    path("p/admin/projects/create/", views.admin_project_create, name="admin_project_create"),
    path("p/admin/projects/<int:project_id>/edit/", views.admin_project_edit, name="admin_project_edit"),
    path("p/admin/projects/<int:project_id>/submit/", views.admin_project_submit, name="admin_project_submit"),
    path("p/admin/projects/<int:project_id>/delete/", views.admin_project_delete, name="admin_project_delete"),
    path("admin/projects/<int:pk>/detail/", views.admin_project_detail, name="admin_project_detail"),

    # Superadmin tekshiruv
    path("p/superadmin/pending/", views.superadmin_pending_list, name="superadmin_pending_list"),
    path("p/superadmin/review/<int:project_id>/", views.superadmin_review, name="superadmin_review"),
    path("p/superadmin/publish/<int:project_id>/", views.superadmin_publish, name="superadmin_publish"),

    # Public
    path("", views.public_project_list, name="public_project_list"),
    path("project/<int:pk>/", views.public_project_detail, name="public_project_detail"),

    path("p/superadmin/reviewed/", views.superadmin_reviewed_list, name="superadmin_reviewed_list"),
    path("p/superadmin/published/", views.superadmin_published_list, name="superadmin_published_list"),

# JWT (admin/login uchun token)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Public API (users frontend ishlatadi)
    path("api/projects/", api_views.public_projects_list, name="api_public_projects"),
    path("api/projects/<int:pk>/", api_views.public_projects_detail, name="api_public_project_detail"),

    path("p/superadmin/projects/", views.superadmin_projects_all, name="superadmin_projects_all"),
    path("p/superadmin/projects/<int:project_id>/", views.superadmin_project_detail, name="superadmin_project_detail"),
    path("p/superadmin/projects/<int:project_id>/edit/", views.superadmin_project_edit, name="superadmin_project_edit"),
    path("p/superadmin/unpublish/<int:project_id>/",  views.superadmin_unpublish,  name="superadmin_unpublish"),
    path("superadmin/projects/bulk-delete/", views.superadmin_projects_bulk_delete, name="superadmin_projects_bulk_delete"),
]
