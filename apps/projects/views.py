from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Q
from apps.accounts.models import User
from .forms import ProjectForm, ReviewForm
from .models import Project
from django.contrib import messages


def is_superadmin(user):
    return user.is_authenticated and getattr(user, "role", None) == "SUPERADMIN"


def is_admin(user):
    return user.is_authenticated and getattr(user, "role", None) == "ADMIN"


# -------------------------
# KICHIK ADMIN (ADMIN)
# -------------------------

@login_required
@user_passes_test(is_admin)
def admin_project_list(request):
    projects = Project.objects.filter(author=request.user)
    return render(request, "projects/admin/project_list.html", {"projects": projects})


@login_required
@user_passes_test(is_admin)
def admin_project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.author = request.user
            p.status = Project.Status.DRAFT
            p.save()

            messages.success(request,f'"{p.title}" loyihasi muvaffaqiyatli yaratildi', extra_tags='ad')
            return redirect("admin_project_list")
    else:
        form = ProjectForm()
    return render(request,"projects/admin/project_form.html",{"form": form, "mode": "create"}
    )


@login_required
@user_passes_test(is_admin)
def admin_project_edit(request, project_id):
    p = get_object_or_404(Project, id=project_id, author=request.user)
    if p.status in [Project.Status.PENDING, Project.Status.REVIEWED, Project.Status.PUBLISHED]:
        return redirect("admin_project_list")

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{p.title}" loyihasi muvaffaqiyatli tahrirlandi', extra_tags='ad')
            return redirect("admin_project_list")
    else:
        form = ProjectForm(instance=p)

    return render(request, "projects/admin/project_form.html", {"form": form, "mode": "edit", "project": p})


@login_required
@user_passes_test(is_admin)
def admin_project_submit(request, project_id: int):
    p = get_object_or_404(Project, id=project_id, author=request.user)

    if p.status not in [Project.Status.DRAFT, Project.Status.REJECTED]:
        messages.error(request, f'"{p.title}" loyihani hozir tekshiruvga yuborib bo‘lmaydi.', extra_tags='ad')
        return redirect("admin_project_list")

    if request.method == "POST":
        p.submit_for_review()
        messages.success(request, f'"{p.title}" Loyiha tekshiruvga yuborildi (PENDING).', extra_tags='ad')

    return redirect("admin_project_list")


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_project_delete(request, project_id):
    p = get_object_or_404(Project, id=project_id, author=request.user)
    # publish bo'lganini o'chirmaymiz (keyin ruxsat beramiz)
    if p.status != Project.Status.PUBLISHED:
        p.delete()
        messages.error(request, f'"{p.title}" loyihasi o‘chirildi.', extra_tags='ad')
    return redirect("admin_project_list")

@login_required
@user_passes_test(is_admin)
def admin_project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, author=request.user)

    env_list = []
    if project.coding_env_note:
        env_list = [x.strip() for x in project.coding_env_note.split(",") if x.strip()]

    return render(
        request,
        "projects/admin/project_detail.html",
        {
            "project": project,
            "env_list": env_list
        }
    )
# -------------------------
# SUPERADMIN REVIEW
# -------------------------

@login_required
@user_passes_test(is_superadmin)
def superadmin_pending_list(request):
    projects = Project.objects.filter(status=Project.Status.PENDING)
    return render(request, "projects/superadmin/pending_list.html", {"projects": projects})

@login_required
@user_passes_test(is_superadmin)
def superadmin_reviewed_list(request):
    projects = Project.objects.filter(status=Project.Status.REVIEWED)
    return render(request, "projects/superadmin/reviewed_list.html", {"projects": projects})


@login_required
@user_passes_test(is_superadmin)
def superadmin_published_list(request):
    projects = Project.objects.filter(status=Project.Status.PUBLISHED)
    return render(request, "projects/superadmin/published_list.html", {"projects": projects})


@login_required
@user_passes_test(is_superadmin)
def superadmin_review(request, project_id):
    p = get_object_or_404(Project.objects.select_related("author"), id=project_id)

    if request.method == "POST":
        action = request.POST.get("action")
        note = (request.POST.get("note") or "").strip()

        # ===== PENDING bosqich =====
        if p.status == Project.Status.PENDING:
            if action == "reviewed":
                p.set_reviewed(note=note)
                messages.success(request, "Loyiha tasdiqlandi, Public qilishdan oldin tahrirlashingiz mumkin.", extra_tags="sd")
                return redirect("superadmin_review", project_id=p.id)  # endi REVIEWED sahifa ochiladi

            if action == "rejected":
                if not note:
                    messages.error(request, "Bekor qilish uchun izoh yozish majburiy.", extra_tags = "sb")
                    return redirect("superadmin_review", project_id=p.id)
                p.set_rejected(note=note)
                messages.error(request, "Loyiha tasdiqlanmadi va junior adminga loyiha qaytarildi.", extra_tags="sb")
                return redirect("superadmin_pending_list")

            messages.error(request, "Noto‘g‘ri amal.", extra_tags="sd")
            return redirect("superadmin_review", project_id=p.id)

        # ===== REVIEWED bosqich =====
        if p.status == Project.Status.REVIEWED:

            if action == "publish":
                # visibility checkboxlar
                p.show_image = bool(request.POST.get("show_image"))
                p.show_title = bool(request.POST.get("show_title"))
                p.show_short_desc = bool(request.POST.get("show_short_desc"))
                p.show_content = bool(request.POST.get("show_content"))
                p.show_youtube = bool(request.POST.get("show_youtube"))
                p.show_zip = bool(request.POST.get("show_zip"))
                p.show_code = bool(request.POST.get("show_code"))

                # Kamida 1 ta element tanlangan bo‘lishi kerak
                if not any([
                    p.show_image,
                    p.show_title,
                    p.show_short_desc,
                    p.show_content,
                    p.show_youtube,
                    p.show_zip,
                    p.show_code
                ]):

                    return redirect("superadmin_review", project_id=p.id)

                # izohni saqlash
                p.review_note = note
                p.save(update_fields=[
                    "show_image", "show_title", "show_short_desc",
                    "show_content", "show_youtube", "show_zip",
                    "show_code", "review_note", "updated_at"
                ])

                p.publish()
                messages.success(request, f"“{p.title}” loyihasi foydalanuvchilarga ko'rinadigan holatda yuklandi",extra_tags="sc")
                return redirect("superadmin_published_list")

            messages.error(request, "Faqat publish qilish mumkin.", extra_tags="sd")
            return redirect("superadmin_review", project_id=p.id)

        # ===== boshqa statuslar =====
        messages.error(request, f"Bu holatda ko‘rib chiqib bo‘lmaydi: {p.status}", extra_tags="sd")
        return redirect("superadmin_projects_all")

    # GET: statusga qarab template tanlaymiz
    if p.status == Project.Status.PENDING:
        return render(request, "projects/superadmin/review_pending.html", {"p": p})

    if p.status == Project.Status.REVIEWED:
        return render(request, "projects/superadmin/review_form.html", {"p": p})

    # PUBLISHED bo'lsa review emas, detailga yuboramiz
    return redirect("superadmin_project_detail", project_id=p.id)


@login_required
@user_passes_test(is_superadmin)
@require_POST
def superadmin_publish(request, project_id):
    p = get_object_or_404(Project, id=project_id)
    p.publish()
    messages.success(request, f"“{p.title}” loyihasi foydalanuvchilarga ko'rinadigan holatda yuklandi", extra_tags="sc")
    return redirect("superadmin_published_list")


# -------------------------
# USER (PUBLISHED)
# -------------------------

def public_project_list(request):
    projects = Project.objects.filter(status=Project.Status.PUBLISHED).order_by("-published_at")
    return render(request, "projects/public/project_list.html", {"projects": projects})


def public_project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, status=Project.Status.PUBLISHED)
    return render(request, "projects/public/project_detail.html", {"project": project})

@login_required
@user_passes_test(is_superadmin)
def superadmin_projects_all(request):
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()

    qs = Project.objects.all().select_related("author").order_by("-updated_at")

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(short_desc__icontains=q) |
            Q(author__username__icontains=q) |
            Q(author__first_name__icontains=q) |
            Q(author__last_name__icontains=q)
        )

    if status:
        qs = qs.filter(status=status)

    return render(request, "projects/superadmin/projects_all.html", {
        "projects": qs,
        "q": q,
        "status": status,
        "status_choices": Project.Status.choices,  # Django enum choices
    })


@login_required
@user_passes_test(is_superadmin)
def superadmin_project_detail(request, project_id: int):
    p = get_object_or_404(Project.objects.select_related("author"), id=project_id)
    return render(request, "projects/superadmin/project_detail.html", {"p": p})


@login_required
@user_passes_test(is_superadmin)
def superadmin_project_edit(request, project_id: int):
    p = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, f"Tahrirlash saqlandi", extra_tags="as")
            return redirect("superadmin_project_detail", project_id=p.id)
    else:
        form = ProjectForm(instance=p)

    return render(request, "projects/superadmin/project_edit.html", {"form": form, "p": p})


@login_required
@user_passes_test(is_superadmin)
def superadmin_unpublish(request, project_id):
    p = get_object_or_404(Project, id=project_id)
    title = p.title
    p.unpublish()
    messages.success(request, f"“{title}” ushbu loyiha umumiy foydalanuvchilar ro‘yxatdan olib tashlandi.", extra_tags="sc")
    return redirect("superadmin_published_list")

@require_POST
@login_required
@user_passes_test(is_superadmin)
def superadmin_projects_bulk_delete(request):
    ids = request.POST.getlist("ids")
    ids = [i for i in ids if str(i).isdigit()]
    if not ids:
        messages.error(request, "Hech narsa tanlanmadi.", extra_tags="sb")
        return redirect("superadmin_projects_all")
    qs = Project.objects.filter(id__in=ids)
    if not qs.exists():
        messages.error(request, "Tanlangan loyihalar topilmadi.", extra_tags="sb")
        return redirect("superadmin_projects_all")
    # 🔹 TITLE’larni oldindan olib olamiz
    titles = list(qs.values_list("title", flat=True))
    count = qs.count()

    qs.delete()

    # 🔹 Juda ko‘p bo‘lsa qisqartiramiz
    if count <= 5:
        title_text = ", ".join(f"“{t}”" for t in titles)
    else:
        title_text = ", ".join(f"“{t}”" for t in titles[:5]) + f" va yana {count-5} ta"

    messages.success(request,f"{count} ta loyiha o‘chirildi: Loyiha nomi {title_text}.", extra_tags="sj"
    )
    return redirect("superadmin_projects_all")