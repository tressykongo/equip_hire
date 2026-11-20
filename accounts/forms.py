
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class RegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label="Account Type",
        widget=forms.Select()
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'role',
            'password1',
            'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )

        return user
