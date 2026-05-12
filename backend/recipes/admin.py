from django.contrib import admin

from .models import (
    Cuisine,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    UserProfile,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "display_name", "role", "updated_at"]
    list_filter = ["role"]
    search_fields = [
        "display_name",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]
    list_editable = ["role", "display_name"]
    autocomplete_fields = ["user"]


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "short_description"]
    list_display_links = ["id"]
    search_fields = ["name", "description"]
    list_editable = ["name"]

    @admin.display(description="описание")
    def short_description(self, obj: Cuisine) -> str:
        if not obj.description:
            return ""
        return (obj.description[:80] + "…") if len(obj.description) > 80 else obj.description


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "cuisine",
        "status",
        "is_public",
        "servings",
        "created_at",
    ]
    list_filter = ["status", "is_public", "cuisine", "created_at", "updated_at"]
    search_fields = [
        "title",
        "description",
        "author__username",
        "author__email",
    ]
    list_editable = ["status", "is_public", "servings"]
    autocomplete_fields = ["author", "cuisine"]
    date_hierarchy = "created_at"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "created_at"]
    list_display_links = ["id"]
    list_editable = ["name"]
    list_filter = ["created_at"]
    search_fields = ["name"]
    date_hierarchy = "created_at"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["recipe", "ingredient", "quantity", "unit", "note"]
    list_filter = ["unit", "ingredient", "recipe"]
    search_fields = [
        "note",
        "ingredient__name",
        "recipe__title",
    ]
    list_editable = ["quantity", "unit", "note"]
    autocomplete_fields = ["recipe", "ingredient"]


@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ["recipe", "step_number", "instruction_preview", "updated_at"]
    list_filter = ["recipe", "created_at"]
    search_fields = ["instruction_text", "recipe__title"]
    list_editable = ["step_number"]
    autocomplete_fields = ["recipe"]

    @admin.display(description="инструкция")
    def instruction_preview(self, obj: RecipeStep) -> str:
        text = obj.instruction_text.strip()
        if not text:
            return ""
        return (text[:72] + "…") if len(text) > 72 else text


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "recipe", "created_at"]
    list_filter = ["created_at"]
    search_fields = [
        "user__username",
        "user__email",
        "recipe__title",
    ]
    autocomplete_fields = ["user", "recipe"]
