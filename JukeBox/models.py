from django.db import models
import uuid
from django.contrib.auth.models import User


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)


class Video(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return self.url


class CurrentState(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)  # Room object (not included in API)
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, blank=True, null=True)  # Youtube video ID
    paused = models.BooleanField(default=True)  # true - pause video, false - play video
    time = models.PositiveIntegerField(default=0)  # time in seconds (skip to specified fragment of video)
    # no. of play / pause commands issued - js checks it to see if the most recent command has been executed already
    play_pause_count = models.PositiveIntegerField(default=1)
    # same as play / pause, but with rewind
    rewind_count = models.PositiveIntegerField(default=1)

