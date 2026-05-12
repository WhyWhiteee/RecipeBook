from django.conf import settings
from django.db import models


class UserRole(models.TextChoices):
    USER = "user", "Пользователь"
    ADMIN = "admin", "Администратор"


class UserProfile(models.Model):
    """Расширение стандартного User: отображаемое имя, роль, фото."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="пользователь",
    )
    display_name = models.CharField("отображаемое имя", max_length=150, blank=True)
    role = models.CharField(
        "роль",
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.USER,
    )
    photo = models.ImageField(
        "фото профиля",
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField("обновлён", auto_now=True)

    class Meta:
        ordering = ["user__username"]
        verbose_name = "профиль пользователя"
        verbose_name_plural = "профили пользователей"

    def __str__(self) -> str:
        who = self.display_name or self.user.get_username()
        return f"{who} ({self.get_role_display()})"


class Cuisine(models.Model):
    name = models.CharField("название", max_length=100, unique=True)
    description = models.TextField("описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "кухня"
        verbose_name_plural = "кухни"

    def __str__(self) -> str:
        return self.name


class RecipeStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    PUBLISHED = "published", "Опубликован"
    ARCHIVED = "archived", "В архиве"


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_recipes",
        verbose_name="автор",
    )
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
        verbose_name="кухня",
    )
    title = models.CharField("название", max_length=255)
    description = models.TextField("описание", blank=True)
    prep_time_minutes = models.PositiveIntegerField("время подготовки, мин", default=0)
    cook_time_minutes = models.PositiveIntegerField("время приготовления, мин", default=0)
    servings = models.PositiveSmallIntegerField("порции", default=1)
    is_public = models.BooleanField("публичный", default=True)
    status = models.CharField(
        "статус",
        max_length=20,
        choices=RecipeStatus.choices,
        default=RecipeStatus.DRAFT,
    )
    photo = models.ImageField(
        "фото рецепта",
        upload_to="recipes/covers/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("обновлён", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"

    def __str__(self) -> str:
        return self.title


class Ingredient(models.Model):
    name = models.CharField("название", max_length=150, unique=True)
    created_at = models.DateTimeField("создан", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_usages",
        verbose_name="ингредиент",
    )
    quantity = models.DecimalField("количество", max_digits=10, decimal_places=2)
    unit = models.CharField("единица", max_length=32)
    note = models.CharField("примечание", max_length=255, blank=True)

    class Meta:
        ordering = ["recipe", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="uniq_recipe_ingredient",
            ),
        ]
        verbose_name = "ингредиент в рецепте"
        verbose_name_plural = "ингредиенты в рецепте"

    def __str__(self) -> str:
        return f"{self.recipe} — {self.ingredient}: {self.quantity} {self.unit}"


class RecipeStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name="рецепт",
    )
    step_number = models.PositiveSmallIntegerField("номер шага")
    instruction_text = models.TextField("инструкция")
    photo = models.ImageField(
        "фото шага",
        upload_to="recipes/steps/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("создан", auto_now_add=True)
    updated_at = models.DateTimeField("обновлён", auto_now=True)

    class Meta:
        ordering = ["recipe", "step_number"]
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "step_number"),
                name="uniq_recipe_step_number",
            ),
        ]
        verbose_name = "шаг приготовления"
        verbose_name_plural = "шаги приготовления"

    def __str__(self) -> str:
        return f"{self.recipe}: шаг {self.step_number}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="рецепт",
    )
    created_at = models.DateTimeField("добавлен", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="uniq_user_recipe_favorite",
            ),
        ]
        verbose_name = "избранное"
        verbose_name_plural = "избранное"

    def __str__(self) -> str:
        return f"{self.user} ♥ {self.recipe}"
