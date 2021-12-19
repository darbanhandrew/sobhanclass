from .models import User, Profile
from django import forms


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date')
