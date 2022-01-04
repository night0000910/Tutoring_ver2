from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework import validators

import tutoringapp.models


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type" : "password"})

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(request=self.context.get("request"), username=username, password=password)

            if user is None or not user.is_active:
                raise serializers.ValidationError("ログインに失敗しました")
            data["user"] = user
        
        return data

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "first_name", "last_name", "profile_image", "rank", "self_introduction", "spent_time", "user_type", "account_start_datetime", "class_start_datetime", "class_ending_datetime"]
    
class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = "__all__"
        extra_kwargs = {
            "username" : {
                "validators" : [
                    validators.UniqueValidator(queryset=get_user_model().objects.all())
                    ],
            }
        }

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = tutoringapp.models.StudentModel
        fields = "__all__"

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = tutoringapp.models.TeacherModel
        fields = "__all__"

class ClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = tutoringapp.models.ClassModel
        fields = "__all__"
