"""
Интеграционные тесты ViewSet: CRUD, 401/403 без токена, 404, фильтрация.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

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


class AuthenticatedAPITestCase(APITestCase):
    """Пользователь с токеном и типичными связанными объектами."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="apiuser",
            email="apiuser@example.com",
            password="SecurePass123!",
        )
        self.profile, _ = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={"display_name": "API User", "role": UserRole.USER},
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        self.cuisine = Cuisine.objects.create(name="ФильтрКухня", description="")
        self.recipe = Recipe.objects.create(
            author=self.user,
            cuisine=self.cuisine,
            title="Мой рецепт",
            status=RecipeStatus.DRAFT,
            is_public=True,
        )
        self.ingredient = Ingredient.objects.create(name="ФильтрИнгредиент")


def assert_unauthenticated_list(client, url):
    """Без токена DRF с IsAuthenticated обычно отдаёт 403; реже 401."""
    client.credentials()
    response = client.get(url)
    client.credentials()  # reset for caller if they re-set in setUp
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ), response.status_code


class UserProfileViewSetTests(AuthenticatedAPITestCase):
    def test_list_get_200(self):
        response = self.client.get("/api/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        ids = [r["id"] for r in response.data["results"]]
        self.assertIn(self.profile.pk, ids)

    def test_create_post_201(self):
        u = User.objects.create_user("prof_only", "po@example.com", "SecurePass123!")
        tok, _ = Token.objects.get_or_create(user=u)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {tok.key}")
        response = self.client.post(
            "/api/profiles/",
            {"display_name": "Новый профиль", "role": UserRole.USER},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserProfile.objects.filter(user=u).exists())

    def test_patch_update_200(self):
        response = self.client.patch(
            f"/api/profiles/{self.profile.pk}/",
            {"display_name": "Обновлено"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, "Обновлено")

    def test_delete_204(self):
        p = UserProfile.objects.create(
            user=User.objects.create_user("todel", "td@example.com", "SecurePass123!"),
            display_name="X",
        )
        tok, _ = Token.objects.get_or_create(user=p.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {tok.key}")
        response = self.client.delete(f"/api/profiles/{p.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_rejected(self):
        assert_unauthenticated_list(self.client, "/api/profiles/")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_detail_not_found_404(self):
        response = self.client.get("/api/profiles/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_role(self):
        response = self.client.get("/api/profiles/", {"role": UserRole.USER})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.data["results"]:
            self.assertEqual(row["role"], UserRole.USER)


class CuisineViewSetTests(AuthenticatedAPITestCase):
    def test_list_get_200(self):
        response = self.client.get("/api/cuisines/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_create_post_201(self):
        response = self.client.post(
            "/api/cuisines/",
            {"name": "УникальнаяКухняXYZ", "description": "описание"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Cuisine.objects.filter(name="УникальнаяКухняXYZ").exists())

    def test_patch_update_200(self):
        c = Cuisine.objects.create(name="ПатчКухня", description="old")
        response = self.client.patch(
            f"/api/cuisines/{c.pk}/",
            {"description": "new"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        c.refresh_from_db()
        self.assertEqual(c.description, "new")

    def test_delete_204(self):
        c = Cuisine.objects.create(name="УдалитьКухню", description="")
        response = self.client.delete(f"/api/cuisines/{c.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cuisine.objects.filter(pk=c.pk).exists())

    def test_list_without_token_rejected(self):
        assert_unauthenticated_list(self.client, "/api/cuisines/")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_detail_not_found_404(self):
        response = self.client.get("/api/cuisines/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_name(self):
        Cuisine.objects.create(name="ТочноеИмяФильтр", description="")
        response = self.client.get("/api/cuisines/", {"name": "ТочноеИмяФильтр"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r["name"] for r in response.data["results"]]
        self.assertIn("ТочноеИмяФильтр", names)
        self.assertTrue(all(n == "ТочноеИмяФильтр" for n in names))


class RecipeViewSetTests(AuthenticatedAPITestCase):
    def test_list_get_200(self):
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_create_post_201(self):
        response = self.client.post(
            "/api/recipes/",
            {"title": "Новый суп", "status": RecipeStatus.PUBLISHED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        r = Recipe.objects.get(title="Новый суп")
        self.assertEqual(r.author, self.user)

    def test_patch_update_200(self):
        response = self.client.patch(
            f"/api/recipes/{self.recipe.pk}/",
            {"title": "Переименовано"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, "Переименовано")

    def test_delete_204(self):
        r = Recipe.objects.create(author=self.user, title="УдалитьРецепт")
        response = self.client.delete(f"/api/recipes/{r.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_rejected(self):
        assert_unauthenticated_list(self.client, "/api/recipes/")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_detail_not_found_404(self):
        response = self.client.get("/api/recipes/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_status(self):
        Recipe.objects.create(
            author=self.user,
            title="ЧерновикФильтр",
            status=RecipeStatus.DRAFT,
        )
        Recipe.objects.create(
            author=self.user,
            title="ПаблишФильтр",
            status=RecipeStatus.PUBLISHED,
        )
        response = self.client.get("/api/recipes/", {"status": RecipeStatus.DRAFT})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.data["results"]:
            self.assertEqual(row["status"], RecipeStatus.DRAFT)


class IngredientViewSetTests(AuthenticatedAPITestCase):
    def test_list_get_200(self):
        response = self.client.get("/api/ingredients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_201(self):
        response = self.client.post(
            "/api/ingredients/",
            {"name": "УникальныйИнгредиентXYZ"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_update_200(self):
        ing = Ingredient.objects.create(name="ПатчИнгредиент")
        response = self.client.patch(
            f"/api/ingredients/{ing.pk}/",
            {"name": "ПатчИнгредиент2"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_204(self):
        ing = Ingredient.objects.create(name="УдалитьИнгредиент")
        response = self.client.delete(f"/api/ingredients/{ing.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_rejected(self):
        assert_unauthenticated_list(self.client, "/api/ingredients/")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_detail_not_found_404(self):
        response = self.client.get("/api/ingredients/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_name(self):
        Ingredient.objects.create(name="СольФильтр")
        response = self.client.get("/api/ingredients/", {"name": "СольФильтр"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(r["name"] == "СольФильтр" for r in response.data["results"]))


class RecipeIngredientViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.ri = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity=Decimal("100"),
            unit="г",
        )

    def test_list_get_200(self):
        response = self.client.get("/api/recipe-ingredients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_201(self):
        ing2 = Ingredient.objects.create(name="ДругойИнгредиент")
        response = self.client.post(
            "/api/recipe-ingredients/",
            {
                "recipe": self.recipe.pk,
                "ingredient": ing2.pk,
                "quantity": "2",
                "unit": "шт",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_update_200(self):
        response = self.client.patch(
            f"/api/recipe-ingredients/{self.ri.pk}/",
            {"quantity": "150.00", "note": "примечание"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_204(self):
        response = self.client.delete(f"/api/recipe-ingredients/{self.ri.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_rejected(self):
        assert_unauthenticated_list(self.client, "/api/recipe-ingredients/")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_detail_not_found_404(self):
        response = self.client.get("/api/recipe-ingredients/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_recipe(self):
        other = Recipe.objects.create(author=self.user, title="Другой рецепт")
        RecipeIngredient.objects.create(
            recipe=other,
            ingredient=Ingredient.objects.create(name="Инг2"),
            quantity=Decimal("1"),
            unit="л",
        )
        response = self.client.get(
            "/api/recipe-ingredients/",
            {"recipe": self.recipe.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.data["results"]:
            self.assertEqual(row["recipe"], self.recipe.pk)


class RecipeStepViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.step = RecipeStep.objects.create(
            recipe=self.recipe,
            step_number=1,
            instruction_text="Нарезать",
        )

    def test_list_get_200(self):
        response = self.client.get("/api/recipe-steps/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_201(self):
        response = self.client.post(
            "/api/recipe-steps/",
            {
                "recipe": self.recipe.pk,
                "step_number": 2,
                "instruction_text": "Варить",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_update_200(self):
        response = self.client.patch(
            f"/api/recipe-steps/{self.step.pk}/",
            {"instruction_text": "Мелко нарезать"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_204(self):
        response = self.client.delete(f"/api/recipe-steps/{self.step.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_rejected(self):
        assert_unauthenticated_list(self.client, "/api/recipe-steps/")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_detail_not_found_404(self):
        response = self.client.get("/api/recipe-steps/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_step_number(self):
        RecipeStep.objects.create(
            recipe=self.recipe,
            step_number=3,
            instruction_text="Третий",
        )
        response = self.client.get("/api/recipe-steps/", {"step_number": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.data["results"]:
            self.assertEqual(row["step_number"], 3)


class FavoriteViewSetTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.fav = Favorite.objects.create(user=self.user, recipe=self.recipe)

    def test_list_get_200(self):
        response = self.client.get("/api/favorites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_201(self):
        r2 = Recipe.objects.create(author=self.user, title="Второй для избранного")
        response = self.client.post(
            "/api/favorites/",
            {"recipe": r2.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch_update_200(self):
        r2 = Recipe.objects.create(author=self.user, title="Замена избранного")
        response = self.client.patch(
            f"/api/favorites/{self.fav.pk}/",
            {"recipe": r2.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_204(self):
        response = self.client.delete(f"/api/favorites/{self.fav.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_without_token_rejected(self):
        assert_unauthenticated_list(self.client, "/api/favorites/")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_detail_not_found_404(self):
        response = self.client.get("/api/favorites/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_recipe(self):
        response = self.client.get("/api/favorites/", {"recipe": self.recipe.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for row in response.data["results"]:
            self.assertEqual(row["recipe"], self.recipe.pk)
