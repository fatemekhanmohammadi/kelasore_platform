from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ClassRoom, MemberShip

User = get_user_model()

class ClassroomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = ['id','title', 'description', 'max_members', 'classtype', 'securitytype', 'password', 'start_date', 'end_date']

    def validate(self, data):
        securitytype = data.get('securitytype')
        password = data.get('password')

        if securitytype == 'PASSWORD' and not password:
            raise serializers.ValidationError({'error': 'برای کلاس خصوصی با گذرواژه، پسورد لازم است'})

        if securitytype != 'PASSWORD':
            data['password'] = ''

        return data

class ClassroomSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassRoom
        fields = ['id', 'title', 'description', 'max_members', 'classtype', 
                  'securitytype', 'start_date', 'end_date', 'owner', 'owner_name', 
                  'member_count',  'created_date']
    
    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username
    
    def get_member_count(self, obj):
        return obj.members.count()


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberShip
        fields = ['user', 'classroom', 'role', 'joined_at']



