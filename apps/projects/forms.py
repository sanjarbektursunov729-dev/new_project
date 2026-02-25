from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "image",
            "title",
            "short_desc",
            "content",
            "youtube_url",
            "code_zip",
            "coding_env_note",
        ]
        labels = {
            "image": "Loyiha rasmi",
            "title": "Sarlavha",
            "short_desc": "Qisqacha izoh",
            "content": "Batafsil ma'lumot",
            "youtube_url": "YouTube havolasi",
            "code_zip": "Kod (ZIP fayl)",
            "coding_env_note": "Kod muhiti / yo‘riqnoma",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Loyiha nomi"}),
            "short_desc": forms.TextInput(attrs={"placeholder": "Qisqacha izoh (300 belgi)"}),
            "content": forms.Textarea(attrs={"rows": 10, "placeholder": "Batafsil ma’lumot..."}),
            "youtube_url": forms.URLInput(attrs={"placeholder": "YouTube link (ixtiyoriy)"}),
            "coding_env_note": forms.Textarea(attrs={"rows": 6, "placeholder": "Kod yozish muhiti bo‘yicha izoh (ixtiyoriy)"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise forms.ValidationError("Rasm majburiy.")
        return image


    def clean_youtube_url(self):
        url = (self.cleaned_data.get("youtube_url") or "").strip()
        if not url:
            return ""
        # juda qattiq tekshirmaymiz, keyin validator qo‘shamiz
        return url


class ReviewForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[("REVIEWED", "REVIEWED"), ("REJECTED", "REJECTED")],
        label="Qaror",
    )
    note = forms.CharField(
        label="Izoh (majburiy emas)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Izoh yozing..."}),
    )
