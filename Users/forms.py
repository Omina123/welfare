import email

from django import forms
from django.contrib.auth.forms import UserCreationForm

from home.models import Loan
from .models import *
class UserRoleForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['user_type', 'is_active', 'is_staff']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
        }
# Member registration form
class MemberRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')  # user_type removed



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'phone_number', 'id_number', 'membership_number', 'pf_number',
            'gender', 'address', 'date_of_birth', 'next_of_kin', 'Next_of_kin_phone'
        )
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',  # This enables the calendar picker
                    'class': 'form-control',
                }
            ),
            'gender': forms.Select(attrs={'class': 'form-select'}),  # Keep your select styling
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'phone_number': 'e.g. 254712345678',
            'id_number': 'Enter National ID Number',
            'membership_number': 'e.g. 1-1000',
            'pf_number': 'e.g. 1999N00000',
            'address': 'Enter your physical address',
            'next_of_kin': 'Enter next of kin name',
            'Next_of_kin_phone': 'e.g. 254712345678',
        }

        for field_name, placeholder_text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'placeholder': placeholder_text,
                    'class': 'form-control'
                })
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username','first_name', 'last_name','email'] # The "remaining" fields
# forms.py
class LoginForm(forms.Form):
    # Change label to be more descriptive
    Email = forms.CharField(label="Email or PF Number", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'e.g. 2024N001 or email@example.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class UpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'user_type']  # Include user_type and password for admin editing

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            # 'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     qs = CustomUser.objects.filter(email=email)
    #     if self.instance.pk:
    #         qs = qs.exclude(pk=self.instance.pk)
    #         if qs.exists():
    #             raise forms.ValidationError("This email is already taken by another user.")
    #     return email

    

       
class PUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'phone_number', 'id_number', 'membership_number',
            'pf_number', 'date_of_birth', 'gender', 'address'
        ]

        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'membership_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pf_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_pf_number(self):
        pf = self.cleaned_data.get('pf_number')

        if pf and Profile.objects.filter(pf_number=pf).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This PF Number is already assigned.")

        return pf

    def clean_membership_number(self):
        mem = self.cleaned_data.get('membership_number')

        if mem and Profile.objects.filter(membership_number=mem).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This Membership Number is already in use.")

        return mem

class EditSalaryForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['gross_salary', 'net_salary', 'month']
        widgets = {
            'month': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'  # This triggers the browser date picker
            }),
            'gross_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_salary': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class MembershipSetupForm(forms.Form):
    monthly_contribution = forms.DecimalField(
        min_value=100,
        max_value=100000
    )