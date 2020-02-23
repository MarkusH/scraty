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
    delete_card,
    delete_story,
    index,
    save_card,
    save_story,
    move_card,
)

urlpatterns = [
    path("", index, name="index"),
    path("stories/", save_story, name="save_story"),
    path("stories/<id>/", delete_story, name="delete_story"),
    path("cards/", save_card, name="save_card"),
    path("cards/<id>/", delete_card, name="delete_card"),
    path("cards/<id>/story/<story>/move/<status>/", move_card, name="move_card"),
]
