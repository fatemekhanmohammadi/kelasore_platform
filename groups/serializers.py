from rest_framework import serializers
from .models import Group


#============================================================================================


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']


#============================================================================================