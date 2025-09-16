from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

User=get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,validators=[validate_password])
    password_confirm =serializers.CharField(write_only=True)

    class Meta:
         model = User
         fields = ('gender','email', 'first_name', 'last_name', 
                 'phone_number', 'password', 'password_confirm')
    
    def validate(self, attrs):
         if attrs['password'] != attrs['password_confirm']:
              raise serializers.ValidationError("Paswwrod don't match")
         return attrs
    def create(self, validated_data):
         validated_data.pop("password_confirm")
         user = User.objects.create_user(**validated_data)
         return user
    
class UserLoginSerializer(serializers.Serializer):
     email=serializers.EmailField()
     password = serializers.CharField(write_only=True)

     def validate(self,attrs):
          email =attrs.get('email')
          password= attrs.get('password')

          if email and password:
               user = authenticate(email=email , password=password)
               if not user:
                    raise serializers.ValidationError("Inavlid email or password")
                    if not user.is_active:
                         raise serializers.ValidationError("User account is disabled")
                    attrs['user']=user
                    return attrs
               else:
                    raise serializers.ValidationError("Must include email and password")

class UserProfileSerializer(serializers.ModelSerializer):
     class Meta:
          model = User
          fields = ('gender','email', 'first_name', 'last_name', 
                 'phone_number')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
                     