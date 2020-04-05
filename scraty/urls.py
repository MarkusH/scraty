"""scraty URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from story.views import (
    cards_detail_view,
    cards_move_view,
    cards_view,
    index,
    stories_detail_view,
    stories_view,
    users,
)

urlpatterns = [
    path("", index, name="index"),
    path("cards/", cards_view, name="cards"),
    path("cards/<id>/", cards_detail_view, name="cards_detail"),
    path("cards/<id>/move/", cards_move_view, name="cards_move"),
    path("stories/", stories_view, name="stories"),
    path("stories/<id>/", stories_detail_view, name="stories_detail"),
    path("users/", users, name="users"),
]
