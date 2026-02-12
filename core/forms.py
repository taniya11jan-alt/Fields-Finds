from django import forms
from django.contrib.auth.models import User
from .models import Tool


class RegistrationForm(forms.ModelForm):
    village = forms.CharField(max_length=100)
    district = forms.CharField(max_length=100)
    pincode = forms.CharField(max_length=6)

    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits")

        if len(username) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This mobile number is already registered")

        return username

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = [
            'name',
            'category',
            'description',
            'price_per_day',
            'image',
            'available_from',
            'available_to'
        ]
        widgets = {
            'available_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'available_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
