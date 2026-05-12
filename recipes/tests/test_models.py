"""Unit-тесты моделей: создание, __str__, значения по умолчанию, связи."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from recipes.models import (
    Cuisine,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeStep,
    RecipeStatus,
    UserProfile,
    UserRole,
)

User = get_user_model()


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="TestPass123!",
        )

    def test_create_user_profile(self):
        profile = UserProfile.objects.create(user=self.user, display_name="Алиса")
        self.assertEqual(profile.user_id, self.user.pk)
        self.assertEqual(profile.display_name, "Алиса")

    def test_str(self):
        p = UserProfile.objects.create(user=self.user, display_name="Алиса")
        self.assertIn("Алиса", str(p))
        self.assertIn("Пользователь", str(p))

    def test_default_role(self):
        p = UserProfile.objects.create(user=self.user)
        self.assertEqual(p.role, UserRole.USER)

    def test_one_to_one_user_relation(self):
        p = UserProfile.objects.create(user=self.user)
        self.assertEqual(self.user.profile.pk, p.pk)
        self.assertEqual(p.user, self.user)


class CuisineModelTests(TestCase):
    def test_create_cuisine(self):
        c = Cuisine.objects.create(name="Итальянская", description="Паста и пицца")
        self.assertEqual(c.name, "Итальянская")

    def test_str(self):
        c = Cuisine.objects.create(name="Французская")
        self.assertEqual(str(c), "Французская")

    def test_default_blank_description(self):
        c = Cuisine.objects.create(name="Греческая")
        self.assertEqual(c.description, "")

    def test_recipes_reverse_relation(self):
        user = User.objects.create_user("u1", "u1@example.com", "TestPass123!")
        cuisine = Cuisine.objects.create(name="Кухня")
        recipe = Recipe.objects.create(author=user, cuisine=cuisine, title="Борщ")
        self.assertIn(recipe, cuisine.recipes.all())


class RecipeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("chef", "chef@example.com", "TestPass123!")

    def test_create_recipe(self):
        r = Recipe.objects.create(author=self.user, title="Суп")
        self.assertEqual(r.author, self.user)

    def test_str(self):
        r = Recipe.objects.create(author=self.user, title="Окрошка")
        self.assertEqual(str(r), "Окрошка")

    def test_defaults(self):
        r = Recipe.objects.create(author=self.user, title="Тест")
        self.assertEqual(r.status, RecipeStatus.DRAFT)
        self.assertTrue(r.is_public)
        self.assertEqual(r.servings, 1)
        self.assertEqual(r.prep_time_minutes, 0)
        self.assertEqual(r.cook_time_minutes, 0)
        self.assertIsNone(r.cuisine_id)

    def test_foreign_keys_author_and_cuisine(self):
        cuisine = Cuisine.objects.create(name="RU")
        r = Recipe.objects.create(author=self.user, cuisine=cuisine, title="Щи")
        self.assertEqual(r.author_id, self.user.pk)
        self.assertEqual(r.cuisine_id, cuisine.pk)


class IngredientModelTests(TestCase):
    def test_create_ingredient(self):
        ing = Ingredient.objects.create(name="Мука")
        self.assertEqual(ing.name, "Мука")

    def test_str(self):
        ing = Ingredient.objects.create(name="Соль")
        self.assertEqual(str(ing), "Соль")

    def test_created_at_auto(self):
        ing = Ingredient.objects.create(name="Перец")
        self.assertIsNotNone(ing.created_at)

    def test_recipe_usages_reverse_empty(self):
        ing = Ingredient.objects.create(name="Вода")
        self.assertEqual(ing.recipe_usages.count(), 0)


class RecipeIngredientModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("cook", "c@example.com", "TestPass123!")
        self.recipe = Recipe.objects.create(author=self.user, title="Каша")
        self.ingredient = Ingredient.objects.create(name="Гречка")

    def test_create_recipe_ingredient(self):
        ri = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity=Decimal("200.50"),
            unit="г",
        )
        self.assertEqual(ri.quantity, Decimal("200.50"))

    def test_str(self):
        ri = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity=Decimal("1"),
            unit="стакан",
        )
        s = str(ri)
        self.assertIn("Каша", s)
        self.assertIn("Гречка", s)

    def test_default_blank_note(self):
        ri = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity=Decimal("1"),
            unit="шт",
        )
        self.assertEqual(ri.note, "")

    def test_foreign_keys_recipe_and_ingredient(self):
        ri = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity=Decimal("10"),
            unit="г",
        )
        self.assertEqual(ri.recipe_id, self.recipe.pk)
        self.assertEqual(ri.ingredient_id, self.ingredient.pk)
        self.assertIn(ri, self.recipe.recipe_ingredients.all())


class RecipeStepModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("s", "s@example.com", "TestPass123!")
        self.recipe = Recipe.objects.create(author=self.user, title="Плов")

    def test_create_step(self):
        st = RecipeStep.objects.create(
            recipe=self.recipe,
            step_number=1,
            instruction_text="Обжарить лук",
        )
        self.assertEqual(st.step_number, 1)

    def test_str(self):
        st = RecipeStep.objects.create(
            recipe=self.recipe,
            step_number=2,
            instruction_text="Добавить рис",
        )
        self.assertIn("Плов", str(st))
        self.assertIn("2", str(st))

    def test_photo_null_by_default(self):
        st = RecipeStep.objects.create(
            recipe=self.recipe,
            step_number=1,
            instruction_text="Шаг",
        )
        self.assertFalse(st.photo)

    def test_foreign_key_recipe_and_steps_reverse(self):
        st = RecipeStep.objects.create(
            recipe=self.recipe,
            step_number=1,
            instruction_text="Начало",
        )
        self.assertEqual(st.recipe_id, self.recipe.pk)
        self.assertIn(st, self.recipe.steps.all())


class FavoriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("fan", "fan@example.com", "TestPass123!")
        self.recipe = Recipe.objects.create(author=self.user, title="Салат")

    def test_create_favorite(self):
        fav = Favorite.objects.create(user=self.user, recipe=self.recipe)
        self.assertEqual(fav.user, self.user)

    def test_str(self):
        fav = Favorite.objects.create(user=self.user, recipe=self.recipe)
        self.assertIn("fan", str(fav))
        self.assertIn("Салат", str(fav))

    def test_created_at_auto(self):
        fav = Favorite.objects.create(user=self.user, recipe=self.recipe)
        self.assertIsNotNone(fav.created_at)

    def test_foreign_keys_user_and_recipe(self):
        fav = Favorite.objects.create(user=self.user, recipe=self.recipe)
        self.assertEqual(fav.user_id, self.user.pk)
        self.assertEqual(fav.recipe_id, self.recipe.pk)
        self.assertIn(fav, self.user.favorites.all())
        self.assertIn(fav, self.recipe.favorited_by.all())
