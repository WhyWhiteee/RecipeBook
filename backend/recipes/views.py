from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Cuisine,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    UserProfile,
)
from .serializers import (
    CuisineSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    LoginSerializer,
    RecipeIngredientSerializer,
    RecipeSerializer,
    RecipeStepSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)


class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})


class StatisticsView(APIView):
    """Сводка для дашборда: счётчики, рецепты по кухням, последние записи."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        recipe_qs = Recipe.objects.filter(author=user)

        counts = {
            "recipes": recipe_qs.count(),
            "ingredients": Ingredient.objects.count(),
            "cuisines": Cuisine.objects.count(),
            "favorites": Favorite.objects.filter(user=user).count(),
            "recipe_steps": RecipeStep.objects.filter(recipe__author=user).count(),
            "recipe_ingredients": RecipeIngredient.objects.filter(recipe__author=user).count(),
        }

        by_cuisine = (
            recipe_qs.values("cuisine_id", "cuisine__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        recipes_by_cuisine = [
            {
                "cuisine_id": row["cuisine_id"],
                "cuisine_name": row["cuisine__name"] or "Без кухни",
                "count": row["count"],
            }
            for row in by_cuisine
        ]

        recent_recipes = list(
            recipe_qs.select_related("cuisine")
            .order_by("-created_at")[:10]
            .values("id", "title", "status", "created_at", "cuisine__name")
        )
        recent_recipes_out = [
            {
                "id": r["id"],
                "title": r["title"],
                "status": r["status"],
                "created_at": r["created_at"],
                "cuisine_name": r["cuisine__name"],
            }
            for r in recent_recipes
        ]

        recent_favorites = list(
            Favorite.objects.filter(user=user)
            .select_related("recipe")
            .order_by("-created_at")[:10]
            .values("id", "created_at", "recipe__title", "recipe_id")
        )
        recent_favorites_out = [
            {
                "id": x["id"],
                "created_at": x["created_at"],
                "recipe_title": x["recipe__title"],
                "recipe_id": x["recipe_id"],
            }
            for x in recent_favorites
        ]

        return Response(
            {
                "counts": counts,
                "recipes_by_cuisine": recipes_by_cuisine,
                "recent_recipes": recent_recipes_out,
                "recent_favorites": recent_favorites_out,
            }
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result["user"]
        token = result["token"]
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
                "email": user.email,
            },
            status=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
                "email": user.email,
            },
            status=200,
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("role",)
    search_fields = ("display_name", "user__username", "user__email")
    ordering_fields = ("id", "updated_at", "user__username")
    ordering = ("user__username",)

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CuisineViewSet(viewsets.ModelViewSet):
    """Справочник кухонь: без владельца в модели — доступен всем аутентифицированным."""

    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("name",)
    search_fields = ("name", "description")
    ordering_fields = ("id", "name")
    ordering = ("name",)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("cuisine", "status", "is_public")
    search_fields = ("title", "description")
    ordering_fields = (
        "id",
        "created_at",
        "updated_at",
        "title",
        "prep_time_minutes",
        "cook_time_minutes",
        "servings",
    )
    ordering = ("-created_at",)

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("id", "name", "created_at")
    ordering = ("name",)


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeIngredientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("recipe", "ingredient", "unit")
    search_fields = ("note", "ingredient__name", "recipe__title")
    ordering_fields = ("id", "recipe", "ingredient", "quantity")
    ordering = ("recipe", "id")

    def get_queryset(self):
        return RecipeIngredient.objects.filter(recipe__author=self.request.user)

    def perform_create(self, serializer):
        recipe = serializer.validated_data["recipe"]
        if recipe.author_id != self.request.user.pk:
            raise PermissionDenied("Можно добавлять ингредиенты только к своим рецептам.")
        serializer.save()


class RecipeStepViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeStepSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("recipe", "step_number")
    search_fields = ("instruction_text", "recipe__title")
    ordering_fields = ("id", "recipe", "step_number", "created_at", "updated_at")
    ordering = ("recipe", "step_number")

    def get_queryset(self):
        return RecipeStep.objects.filter(recipe__author=self.request.user)

    def perform_create(self, serializer):
        recipe = serializer.validated_data["recipe"]
        if recipe.author_id != self.request.user.pk:
            raise PermissionDenied("Можно добавлять шаги только к своим рецептам.")
        serializer.save()


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ("recipe",)
    search_fields = ("recipe__title", "user__username")
    ordering_fields = ("id", "created_at")
    ordering = ("-created_at",)

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        recipe = serializer.validated_data["recipe"]
        if not recipe.is_public and recipe.author_id != self.request.user.pk:
            raise PermissionDenied("Нельзя добавить в избранное приватный чужой рецепт.")
        serializer.save(user=self.request.user)
