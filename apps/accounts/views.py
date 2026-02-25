from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from apps.projects.models import Project
from .forms import CreateAdminForm
from .services import generate_password, generate_unique_username

User = get_user_model()


def is_superadmin(user):
    return user.is_authenticated and getattr(user, "role", None) == "SUPERADMIN"

def is_admin(user):
    return user.is_authenticated and getattr(user, "role", None) == "ADMIN"


def login_view(request):
    # Allaqachon login bo'lsa
    if request.user.is_authenticated:
        if is_superadmin(request.user):
            return redirect("superadmin_admin_list")
        if is_admin(request.user):
            return redirect("admin_dashboard")
        return redirect("login")  # boshqa role bo'lsa

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Login yoki parol xato.", extra_tags="lg")
            return redirect("login")

        if not user.is_active:
            messages.error(request, "Siz bloklangansiz. Superadmin bilan bog'laning.", extra_tags="lg")
            return redirect("login")

        login(request, user)

        # Login bo'lgandan keyin role bo'yicha yuboramiz
        if is_superadmin(user):
            return redirect("superadmin_admin_list")
        if is_admin(user):
            return redirect("admin_dashboard")

        logout(request)
        return redirect("login")

    return render(request, "accounts/login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
@user_passes_test(is_superadmin)
def superadmin_admin_list(request):
    admins = User.objects.filter(role="ADMIN").order_by("-id")

    # ✅ faqat 1 marta ko'rsin: sahifa yangilansa yo'qoladi
    created_creds = request.session.pop("created_admin_creds", None)

    return render(
        request,
        "accounts/superadmin/admin_list.html",
        {"admins": admins, "created_creds": created_creds}
    )

@login_required
@user_passes_test(is_superadmin)
def superadmin_admin_create(request):
    if request.method == "POST":
        form = CreateAdminForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"].strip()
            last_name = form.cleaned_data["last_name"].strip()
            email = (form.cleaned_data["email"] or "").strip()

            username = generate_unique_username(first_name, last_name)
            password = generate_password(10)

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role="ADMIN",
                is_active=True,
                created_by=request.user,
            )

            request.session["created_admin_creds"] = {
                "name": f"{user.first_name} {user.last_name}".strip(),
                "username": username,
                "password": password,
            }
            return redirect("superadmin_admin_list")
    else:
        form = CreateAdminForm()

    return render(request, "accounts/superadmin/admin_create.html", {"form": form})


@login_required
@user_passes_test(is_superadmin)
@require_POST
def superadmin_admin_toggle_block(request, user_id):
    admin_user = get_object_or_404(User, id=user_id, role="ADMIN")
    admin_user.is_active = not admin_user.is_active
    admin_user.save(update_fields=["is_active"])

    if admin_user.is_active:
        messages.success(request, f"{admin_user.username} qayta faollashtirildi.", extra_tags="sa")
    else:
        messages.warning(request, f"{admin_user.username} bloklandi.", extra_tags="sa")

    return redirect("superadmin_admin_list")


@login_required
@user_passes_test(is_superadmin)
@require_POST
def superadmin_admin_delete(request, user_id):
    admin_user = get_object_or_404(User, id=user_id, role="ADMIN")
    username = admin_user.username
    admin_user.delete()
    messages.error(request, f"{username} o‘chirildi.", extra_tags="sa")

    return redirect("superadmin_admin_list")


@login_required
def home_view(request):
    return render(request, "accounts/login.html")

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    qs = Project.objects.filter(author=request.user)

    stats = {
        "draft": qs.filter(status=Project.Status.DRAFT).count(),
        "pending": qs.filter(status=Project.Status.PENDING).count(),
        "reviewed": qs.filter(status=Project.Status.REVIEWED).count(),   # ✅ yangi
        "rejected": qs.filter(status=Project.Status.REJECTED).count(),
        "published": qs.filter(status=Project.Status.PUBLISHED).count(),
        "total": qs.count(),   # ✅ barcha loyihalar
    }

    return render(request, "accounts/admin/dashboard.html", {"stats": stats})