from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, PostForm, StoryForm, ProfileForm
from .models import Profile, FriendRequest, Post, Story, PostMedia
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

# -------------------------------
# User Registration & Auth Views
# -------------------------------
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered. Try logging in or use a different email.")
                return render(request, "core/register.html", {"form": form})

            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "bio": form.cleaned_data.get("bio"),
                    "gender": form.cleaned_data.get("gender"),
                    "age": form.cleaned_data.get("age") or None,
                    "profile_pic": form.cleaned_data.get("profile_pic")
                }
            )

            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("feed")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, "core/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')


# -------------------------------
# Feed View (Posts + Stories)
# -------------------------------
@login_required
def feed_view(request):
    user_profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST" and "submit_post" in request.POST:
        caption = request.POST.get("caption", "")
        files = request.FILES.getlist("media")
        if caption or files:
            post = Post.objects.create(user=user_profile, caption=caption)
            for f in files:
                is_video = f.name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
                PostMedia.objects.create(post=post, file=f, is_video=is_video)

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "success",
                    "post_id": post.id,
                    "caption": post.caption,
                    "likes": post.likes.count(),
                })
            messages.success(request, "Post created successfully!")
            return redirect("feed")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "Add caption or media!"})
            messages.error(request, "You must add a caption or media!")

    posts = Post.objects.all().order_by("-timestamp")
    stories = Story.objects.filter(is_active=True).order_by("-timestamp")
    return render(request, "core/feed.html", {"posts": posts, "stories": stories})


@login_required
def send_friend_request(request, profile_id):
    sender = request.user.profile
    receiver = get_object_or_404(Profile, id=profile_id)
    if not FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
        FriendRequest.objects.create(sender=sender, receiver=receiver)
    return redirect("feed")


@login_required
def accept_friend_request(request, request_id):
    if request.method == "POST":
        fr = get_object_or_404(FriendRequest, id=request_id)
        if fr.receiver == request.user.profile:
            fr.receiver.friends.add(fr.sender)
            fr.sender.friends.add(fr.receiver)
            fr.delete()
    return redirect("friends")


@login_required
def decline_friend_request(request, request_id):
    if request.method == "POST":
        fr = get_object_or_404(FriendRequest, id=request_id)
        if fr.receiver == request.user.profile:
            fr.delete()
    return redirect("friends")


@login_required
def unfriend(request, profile_id):
    if request.method == "POST":
        user_profile = request.user.profile
        other_profile = get_object_or_404(Profile, id=profile_id)
        user_profile.friends.remove(other_profile)
        other_profile.friends.remove(user_profile)
    return redirect("friends")


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = request.user.profile
    if profile in post.likes.all():
        post.likes.remove(profile)
        liked = False
    else:
        post.likes.add(profile)
        liked = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"likes": post.likes.count(), "liked": liked})

    return redirect("feed")


@login_required
def profile_view(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    posts = Post.objects.filter(user=profile).order_by("-timestamp")
    return render(request, "core/profile.html", {"profile": profile, "posts": posts})


@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            age_value = form.cleaned_data.get("age")
            if age_value == "" or age_value is None:
                form.instance.age = None
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile", user_id=request.user.id)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/edit_profile.html", {"form": form})


@login_required
def add_story_view(request):
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user.profile
            story.is_active = True
            story.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "success",
                    "story_id": story.id,
                    "story_image": story.image.url
                })
    return redirect("feed")


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.user.user:
        post.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})

    return redirect("feed")


@login_required
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.user == story.user.user:
        story.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": "success"})

    return redirect("feed")


@login_required
def friends_view(request):
    friends = request.user.profile.friends.all()
    return render(request, "core/friends.html", {"friends": friends})


@login_required
def search_users(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        results = Profile.objects.filter(
            Q(user__username__icontains=query) | Q(bio__icontains=query)
        ).exclude(id=request.user.profile.id)
    return render(request, "core/search.html", {"query": query, "results": results})


def notifications_view(request):
    if request.user.is_authenticated:
        friend_requests = FriendRequest.objects.filter(receiver=request.user.profile)
    else:
        friend_requests = []
    return render(request, "core/notifications.html", {"friend_requests": friend_requests})
