from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import OurUser

class UserChangeForm(forms.ModelForm):
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=False)
    class Meta:
        model = OurUser
        fields = ("username", "new_password1", "new_password2")

    def clean_username(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        user_id = self.instance.id
        if OurUser.objects.filter(username=username).exclude(id=user_id).exists():
            raise ValidationError("Username already exists.")
        return username
    
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("The new passwords do not match.")
        return new_password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password1 = self.cleaned_data.get("new_password1")
        if new_password1:
            user.set_password(new_password1)
        if commit:
            user.save()
        return user

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)
    username = forms.CharField(label="Username", max_length=150, required=True)

    username.widget.attrs.update({"placeholder": "Username"})
    password1.widget.attrs.update({"placeholder": "Password"})
    password2.widget.attrs.update({"placeholder": "Confirm Password"})

    class Meta:
        model = OurUser
        fields = ("username", "password1", "password2")

    def clean_password2(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if OurUser.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data["username"]
        if commit:
            user.save()
        return user
    

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    username.widget.attrs.update({"placeholder": "Username"})
    password.widget.attrs.update({"placeholder": "Password"})
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not OurUser.objects.filter(username=username).exists():
            raise ValidationError("Username does not exist.")
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        username = self.cleaned_data.get("username")
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Invalid password.")
            self.user = user
        return password
