from django import forms
from django.core.exceptions import ValidationError
from .models import OurUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()
    date_joined = forms.DateTimeField(required=False)
    class Meta:
        model = OurUser
        fields = ("username", "password", "is_active","is_superuser")



class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)
    is_superuser = forms.BooleanField(label="Superuser", required=False, initial=False)
    username = forms.CharField(label="Username", max_length=150, required=True)

    username.widget.attrs.update({"placeholder": "Username"})
    password1.widget.attrs.update({"placeholder": "Password"})
    password2.widget.attrs.update({"placeholder": "Confirm Password"})

    class Meta:
        model = OurUser
        fields = ("username", "password1", "password2", "is_superuser")

    def save(self, user=OurUser(), commit=True, new_username=None, update=False):
        user.set_password(self.cleaned_data["password1"])
        if new_username:
            user.username = new_username
        else:
            user.username = self.cleaned_data["username"]
        user.username = self.cleaned_data["username"]
        user.is_superuser = self.cleaned_data.get("is_superuser", False)
        if commit:
            user.save(force_update=update)
        return user
    
    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password doesn't match.")
        return password1
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if OurUser.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username
    

