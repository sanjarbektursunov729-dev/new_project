from django import forms


class CreateAdminForm(forms.Form):
    first_name = forms.CharField(label="Ism", max_length=150)
    last_name = forms.CharField(label="Familiya", max_length=150)
    email = forms.EmailField(label="Email (ixtiyoriy)", required=False)
