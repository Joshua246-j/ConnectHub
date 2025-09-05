from django.db import models
from django.contrib.auth.models import User

# Profile model for extra user info
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=10, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True, default=None)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.user.username


# Friend request model
class FriendRequest(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"


# Post model with multiple media support
class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    caption = models.TextField()  # ✅ caption is REQUIRED now
    likes = models.ManyToManyField(Profile, blank=True, related_name='liked_posts')
    timestamp = models.DateTimeField(auto_now_add=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Post by {self.user}"


# Media model for images/videos (supports multiple files per post)
class PostMedia(models.Model):
    post = models.ForeignKey(Post, related_name="media", on_delete=models.CASCADE)
    file = models.FileField(upload_to="posts/")
    is_video = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Simple check for video file
        if self.file and self.file.name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            self.is_video = True
        super().save(*args, **kwargs)


# Story model remains unchanged
class Story(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='stories/', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Story by {self.user}"
