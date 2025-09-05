from django import forms
from django.contrib.auth.models import User
from .models import Profile, Post, PostMedia, Story

# -----------------------------
# User Registration Form
# -----------------------------
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Re-enter password"}), label="Confirm Password")
    bio = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Tell us about yourself"}), required=False)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=False)
    age = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"placeholder": "Your age"}))
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Passwords do not match!")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists!")
        return email


# -----------------------------
# Post Form (Images Only)
# -----------------------------
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["caption"]  # Only caption here
        widgets = {
            "caption": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "What's on your mind?",
                "class": "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none text-sm transition dark:bg-gray-700 dark:text-gray-100"
            })
        }

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["image"]



# -----------------------------
# Story Form
# -----------------------------
class StoryForm(forms.ModelForm):
    image = forms.ImageField(required=True)

    class Meta:
        model = Story
        fields = ["image"]


# -----------------------------
# Profile Edit Form
# -----------------------------
class ProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Tell us about yourself"}), required=False)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=False)
    age = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"placeholder": "Your age"}))
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ["bio", "gender", "age", "profile_pic"]
