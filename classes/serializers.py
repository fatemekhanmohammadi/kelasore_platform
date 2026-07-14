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

        extra_kwargs = {
            'owner': {'read_only': True},  # ← این رو اضافه کن
        }
    
    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username
    
    def get_member_count(self, obj):
        return obj.members.count()

class MembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = MemberShip
        fields = [
            'id',
            'user',
            'user_id',
            'user_name',
            'classroom',
            'role',
            'joined_at'
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
   # در نتیجه این تابع می‌گوید:
#اگر کاربر اسم و فامیل دارد → همان را نمایش بده.
#اگر اسم و فامیل ندارد → نام کاربری را نمایش بده.