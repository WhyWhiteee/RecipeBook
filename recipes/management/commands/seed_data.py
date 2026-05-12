"""
Management command: python manage.py seed_data
Creates test data: 3 users, cuisines, ingredients, recipes (with steps and
recipe-ingredients) and favorites. Total well over 20 records.
Run multiple times safely — existing objects are skipped (get_or_create).
"""
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from recipes.models import (
    Cuisine,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeStatus,
    RecipeStep,
    UserProfile,
    UserRole,
)

User = get_user_model()

USERS = [
    {"username": "chef_anna", "email": "anna@example.com", "password": "Anna1234!", "display_name": "Анна"},
    {"username": "foodie_ivan", "email": "ivan@example.com", "password": "Ivan1234!", "display_name": "Иван"},
    {"username": "cook_maria", "email": "maria@example.com", "password": "Maria1234!", "display_name": "Мария"},
]

CUISINES = [
    ("Итальянская", "Паста, пицца, ризотто и прочие блюда солнечной Италии."),
    ("Японская", "Суши, рамен, темпура и минималистичные вкусы востока."),
    ("Грузинская", "Хачапури, хинкали, сациви — богатая кавказская кухня."),
    ("Французская", "Изысканные соусы, луковый суп и классические десерты."),
    ("Мексиканская", "Острые тако, гуакамоле, буррито и энчиладас."),
]

INGREDIENTS = [
    "Спагетти", "Яйцо", "Бекон", "Пармезан", "Чеснок",
    "Рис", "Нори", "Лосось", "Авокадо", "Имбирь",
    "Мука", "Сыр сулугуни", "Масло сливочное", "Молоко",
    "Помидор", "Лук", "Оливковое масло", "Базилик",
    "Куриное филе", "Соевый соус", "Лайм", "Кинза",
    "Шпинат", "Сливки", "Картофель", "Перец чили",
]

RECIPES = [
    ("Паста карбонара", 0, 10, 20, 2, "Классическая итальянская паста со сливочным соусом из яиц и бекона."),
    ("Паста болоньезе", 0, 15, 40, 4, "Густой мясной соус с томатами и пармезаном."),
    ("Маргарита", 0, 20, 15, 2, "Классическая пицца с томатным соусом, моцареллой и базиликом."),
    ("Ризотто с грибами", 0, 10, 30, 2, "Кремовое ризотто с лесными грибами и пармезаном."),
    ("Тирамису", 0, 30, 0, 6, "Нежный итальянский десерт с маскарпоне и кофе."),
    ("Суши с лососем", 1, 20, 0, 2, "Классические нигири с нежным лососем."),
    ("Рамен", 1, 15, 45, 2, "Наваристый японский суп с лапшой и яйцом."),
    ("Темпура с овощами", 1, 10, 15, 2, "Хрустящие овощи в лёгком кляре."),
    ("Гёдза", 1, 30, 15, 4, "Японские жареные пельмени с начинкой из свинины."),
    ("Хачапури по-аджарски", 2, 15, 20, 2, "Лодочка из теста с расплавленным сулугуни и яйцом."),
    ("Хинкали с мясом", 2, 40, 20, 4, "Грузинские хинкали с пряной говяжьей начинкой."),
    ("Сациви из курицы", 2, 20, 60, 4, "Куриные кусочки в ореховом соусе сациви."),
    ("Луковый суп", 3, 15, 45, 4, "Французский луковый суп с гренками и грюйером."),
    ("Киш лорен", 3, 20, 40, 6, "Открытый пирог с беконом, яйцами и сливками."),
    ("Тако с курицей", 4, 15, 20, 2, "Сочные тако с пряной курицей, гуакамоле и сальсой."),
    ("Буррито с фасолью", 4, 10, 25, 2, "Сытный буррито с чёрной фасолью, рисом и чили."),
]

STEP_TEMPLATES = [
    "Подготовить все ингредиенты: помыть, нарезать, отмерить.",
    "Разогреть сковороду на среднем огне с добавлением масла.",
    "Обжарить основные ингредиенты до золотистой корочки (5–7 минут).",
    "Добавить специи и перемешать. Готовить ещё 2 минуты.",
    "Соединить все компоненты блюда в одной ёмкости.",
    "Довести до вкуса: посолить, поперчить, добавить зелень.",
    "Подавать горячим, украсив зеленью и тёртым сыром.",
    "Дать настояться 5 минут перед подачей.",
]


class Command(BaseCommand):
    help = "Seed database with test data (3 users, 16 recipes, ingredients, steps, favorites)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Seeding database ==="))

        users = self._create_users()
        cuisines = self._create_cuisines()
        ingredients = self._create_ingredients()
        recipes = self._create_recipes(users, cuisines, ingredients)
        self._create_favorites(users, recipes)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Users: {len(users)}, Cuisines: {len(cuisines)}, "
            f"Ingredients: {len(ingredients)}, Recipes: {len(recipes)}."
        ))

    def _create_users(self):
        users = []
        for data in USERS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={"email": data["email"]},
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(f"  Created user: {user.username}")
            else:
                self.stdout.write(f"  Skipped user (exists): {user.username}")

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "display_name": data["display_name"],
                    "role": UserRole.USER,
                },
            )
            Token.objects.get_or_create(user=user)
            users.append(user)
        return users

    def _create_cuisines(self):
        cuisines = []
        for name, desc in CUISINES:
            obj, created = Cuisine.objects.get_or_create(
                name=name,
                defaults={"description": desc},
            )
            if created:
                self.stdout.write(f"  Created cuisine: {name}")
            cuisines.append(obj)
        return cuisines

    def _create_ingredients(self):
        ingredients = []
        for name in INGREDIENTS:
            obj, created = Ingredient.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f"  Created ingredient: {name}")
            ingredients.append(obj)
        return ingredients

    def _create_recipes(self, users, cuisines, ingredients):
        recipes = []
        statuses = [RecipeStatus.PUBLISHED, RecipeStatus.PUBLISHED, RecipeStatus.DRAFT]

        for idx, (title, cuisine_idx, prep, cook, servings, desc) in enumerate(RECIPES):
            author = users[idx % len(users)]
            cuisine = cuisines[cuisine_idx]
            status = random.choice(statuses)

            recipe, created = Recipe.objects.get_or_create(
                title=title,
                author=author,
                defaults={
                    "cuisine": cuisine,
                    "description": desc,
                    "prep_time_minutes": max(0, prep + random.randint(-5, 5)),
                    "cook_time_minutes": max(0, cook + random.randint(-5, 10)),
                    "servings": servings,
                    "is_public": status == RecipeStatus.PUBLISHED,
                    "status": status,
                },
            )
            if created:
                self.stdout.write(f"  Created recipe: {title} (author: {author.username})")
                self._create_steps(recipe)
                self._create_recipe_ingredients(recipe, ingredients)
            else:
                self.stdout.write(f"  Skipped recipe (exists): {title}")

            recipes.append(recipe)
        return recipes

    def _create_steps(self, recipe):
        step_count = random.randint(3, len(STEP_TEMPLATES))
        chosen = random.sample(STEP_TEMPLATES, step_count)
        for number, text in enumerate(chosen, start=1):
            RecipeStep.objects.get_or_create(
                recipe=recipe,
                step_number=number,
                defaults={"instruction_text": text},
            )

    def _create_recipe_ingredients(self, recipe, all_ingredients):
        units = ["г", "мл", "шт", "ст.л.", "ч.л.", "кг", "л"]
        chosen = random.sample(all_ingredients, random.randint(3, 6))
        for ingredient in chosen:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                defaults={
                    "quantity": round(random.uniform(10, 400), 1),
                    "unit": random.choice(units),
                    "note": random.choice(["", "", "нарезать кубиками", "мелко нарубить", "по вкусу"]),
                },
            )

    def _create_favorites(self, users, recipes):
        public_recipes = [r for r in recipes if r.is_public]
        for user in users:
            candidates = [r for r in public_recipes if r.author != user]
            if not candidates:
                continue
            chosen = random.sample(candidates, min(4, len(candidates)))
            for recipe in chosen:
                _, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
                if created:
                    self.stdout.write(f"  Favorite: {user.username} ♥ {recipe.title}")
