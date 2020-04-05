import uuid

from django.db import models


class User(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    color = models.CharField(max_length=6, blank=True)


class Story(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.TextField()
    link = models.URLField(blank=True)
    done = models.BooleanField(default=False)


class Card(models.Model):
    class Status(models.TextChoices):
        TODO = "TODO"
        IN_PROGRESS = "IN_PROGRESS"
        VERIFY = "VERIFY"
        DONE = "DONE"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    text = models.TextField()
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="cards")
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL, related_name="cards"
    )
    status = models.CharField(
        max_length=11, choices=Status.choices, default=Status.TODO
    )
    done = models.BooleanField(default=False)
