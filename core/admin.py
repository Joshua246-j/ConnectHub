from django.contrib import admin
from .models import Profile, FriendRequest, Post, Story

admin.site.register(Profile)
admin.site.register(FriendRequest)
admin.site.register(Post)
admin.site.register(Story)
