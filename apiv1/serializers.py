from django.contrib.auth import authenticate
from rest_framework import serializers

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

class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = tutoringapp.models.TeacherModel
        fields = "__all__"

class TeachersClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = tutoringapp.models.ClassModel
        fields = "__all__"
