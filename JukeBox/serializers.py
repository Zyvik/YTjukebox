from rest_framework import serializers
from .models import CurrentState, Room, Video


class StateSerializer(serializers.ModelSerializer):
    video = serializers.StringRelatedField(many=False)

    class Meta:
        model = CurrentState
        fields = ('video', 'paused', 'time', 'play_pause_count', 'rewind_count')
