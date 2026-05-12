from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CuisineViewSet,
    FavoriteViewSet,
    HealthCheckView,
    IngredientViewSet,
    RecipeIngredientViewSet,
    RecipeStepViewSet,
    RecipeViewSet,
    UserProfileViewSet,
)

router = DefaultRouter()
router.register(r"profiles", UserProfileViewSet, basename="userprofile")
router.register(r"cuisines", CuisineViewSet, basename="cuisine")
router.register(r"recipes", RecipeViewSet, basename="recipe")
router.register(r"ingredients", IngredientViewSet, basename="ingredient")
router.register(
    r"recipe-ingredients",
    RecipeIngredientViewSet,
    basename="recipeingredient",
)
router.register(r"recipe-steps", RecipeStepViewSet, basename="recipestep")
router.register(r"favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/", include("recipes.auth_urls")),
    path("", include(router.urls)),
]
