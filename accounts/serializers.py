from rest_framework import serializers
from django.contrib.auth import get_user_model


User=get_user_model()

#==================================================================================================================

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='STUDENT')
    class Meta:
        model=User
        fields=["username","email","password","first_name","last_name","role"]


    def create(self, validated_data):
        user=User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email',''),
            password=validated_data['password'],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=validated_data.get('role', 'STUDENT')
        )
        return user
    
#===================================================================================================================

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["username","email","password","first_name","last_name"]
         #چون کاربر همیشه نمی‌خواد رمز عوض کنه. اگه required=True باشه، همیشه باید رمز بفرسته
        extra_kwargs={'password':{'required':False, 'write_only': True}}  
         
    def update(self, instance, validated_data):
        password=validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr ,value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
       