from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import (
    Cuisine,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    UserProfile,
    UserRole,
)

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})
    display_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        validate_password(attrs["password"])
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Пользователь с таким логином уже есть."})
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже есть."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        display_name = validated_data.pop("display_name", "") or ""
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        UserProfile.objects.create(
            user=user,
            display_name=display_name,
            role=UserRole.USER,
        )
        token, _ = Token.objects.get_or_create(user=user)
        return {"user": user, "token": token}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        from django.contrib.auth import authenticate

        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Неверный логин или пароль.")
        if not user.is_active:
            raise serializers.ValidationError("Учётная запись отключена.")
        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Профиль: логин связанного User через source."""

    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "user_username",
            "display_name",
            "role",
            "photo",
            "updated_at",
        )
        read_only_fields = ("id", "user", "updated_at", "user_username")


class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ("id", "name", "description")
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    """Имя автора (логин) через source к связанному User."""

    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "author_name",
            "cuisine",
            "title",
            "description",
            "prep_time_minutes",
            "cook_time_minutes",
            "servings",
            "is_public",
            "status",
            "photo",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "created_at",
            "updated_at",
            "author_name",
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "created_at")
        read_only_fields = ("id", "created_at")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    recipe_title = serializers.CharField(source="recipe.title", read_only=True)
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "recipe",
            "recipe_title",
            "ingredient",
            "ingredient_name",
            "quantity",
            "unit",
            "note",
        )
        read_only_fields = ("id", "recipe_title", "ingredient_name")


class RecipeStepSerializer(serializers.ModelSerializer):
    recipe_title = serializers.CharField(source="recipe.title", read_only=True)

    class Meta:
        model = RecipeStep
        fields = (
            "id",
            "recipe",
            "recipe_title",
            "step_number",
            "instruction_text",
            "photo",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "recipe_title",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    recipe_title = serializers.CharField(source="recipe.title", read_only=True)

    class Meta:
        model = Favorite
        fields = (
            "id",
            "user",
            "user_username",
            "recipe",
            "recipe_title",
            "created_at",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "user_username",
            "recipe_title",
        )
