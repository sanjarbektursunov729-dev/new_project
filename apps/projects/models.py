from django.conf import settings
from django.db import models
from django.utils import timezone


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        REVIEWED = "REVIEWED", "Reviewed"
        REJECTED = "REJECTED", "Rejected"
        PUBLISHED = "PUBLISHED", "Published"

    # ✅ Majburiy
    image = models.ImageField(upload_to="project_images/", null=True, blank=True)
  # majburiy
    title = models.CharField(max_length=200)               # majburiy
    short_desc = models.CharField(max_length=300)          # majburiy
    content = models.TextField()                           # majburiy

    # ⭕ Ixtiyoriy
    youtube_url = models.URLField(blank=True)
    code_zip = models.FileField(upload_to="project_zips/", blank=True, null=True)

    # Kod yozish muhiti (ixtiyoriy) — hozircha “yo‘riqnoma/muhit” tavsifi
    # Keyin real online editor qo‘shamiz
    coding_env_note = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    author_name = models.CharField(max_length=255, blank=True, default="")
    
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_projects",
    )
    review_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # === Visibility settings ===
    show_image = models.BooleanField(default=True)
    show_title = models.BooleanField(default=True)
    show_short_desc = models.BooleanField(default=True)
    show_content = models.BooleanField(default=True)
    show_youtube = models.BooleanField(default=True)
    show_zip = models.BooleanField(default=True)
    show_code = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def can_submit(self):
        return self.status in [self.Status.DRAFT, self.Status.REJECTED]

    def submit_for_review(self):
        self.status = self.Status.PENDING
        self.submitted_at = timezone.now()

        # qayta yuborilganda eski review natijalari aralashmasin:
        self.reviewed_at = None
        self.published_at = None
        self.review_note = ""  # eski izohni tozalaymiz (xohlasang qoldiramiz ham bo'ladi)

        self.save(update_fields=[
            "status", "submitted_at",
            "reviewed_at", "published_at",
            "review_note", "updated_at"
        ])


    def set_reviewed(self, note: str = ""):
        self.status = self.Status.REVIEWED
        self.review_note = note or ""
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "review_note", "reviewed_at", "updated_at"])

    def set_rejected(self, note: str = ""):
        self.status = self.Status.REJECTED
        self.review_note = note or ""
        self.reviewed_at = timezone.now()
        self.published_at = None
        self.save(update_fields=["status", "review_note", "reviewed_at", "published_at", "updated_at"])

    def publish(self):
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at", "updated_at"])

    def unpublish(self):
        self.status = self.Status.REVIEWED
        self.published_at = None
        self.save(update_fields=["status", "published_at", "updated_at"])

    def __str__(self):
        return f"{self.title} ({self.status})"
