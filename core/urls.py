from django.urls import path
from . import views

urlpatterns = [
    # 🔑 Authentication
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # 🏠 Main feed
    path("", views.feed_view, name="feed"),  # Handles both displaying feed AND creating posts

    # 📸 Posts & Stories
    # ✅ Removed the separate create_post URL because feed_view handles it
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle_like"),

    # 👥 Friends system
    path("friends/", views.friends_view, name="friends"),
    path("friend-request/send/<int:profile_id>/", views.send_friend_request, name="send_friend_request"),
    path("friend-request/accept/<int:request_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("friend-request/decline/<int:request_id>/", views.decline_friend_request, name="decline_friend_request"),
    path("unfriend/<int:profile_id>/", views.unfriend, name="unfriend"),

    # 👤 Profile & Search
    path("profile/<int:user_id>/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path("search/", views.search_users, name="search_users"),
    path("story/add/", views.add_story_view, name="add_story"),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete_story/<int:story_id>/', views.delete_story, name='delete_story'),
    path('notifications/', views.notifications_view, name='notifications'),
]
