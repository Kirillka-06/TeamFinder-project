# TeamFinder — Вариант 3

## Описание

Веб-приложение TeamFinder на Django. Реализован **Вариант 3**: «Необходимые навыки» проектов, фильтрация проектов по навыкам.

## Структура

- `users/` — приложение пользователей (модель User, регистрация, авторизация, профиль)
- `projects/` — приложение проектов (модели Project и Skill, CRUD проектов, навыки)
- `team_finder/` — настройки Django
- `templates_var3/` — HTML-шаблоны для варианта 3
- `static/` — CSS, JS, шрифты, картинки

## Запуск

### С Docker

```bash
cp .env_example .env
# Заполните .env переменными, установите TASK_VERSION=3
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Без Docker

```bash
pip install -r requirements.txt
cp .env_example .env
# Заполните .env, убедитесь что PostgreSQL запущен
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Переменные окружения (.env)

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
TASK_VERSION=3
```

## URL-маршруты

| URL | Описание |
|-----|----------|
| `/` | Редирект на `/projects/list/` |
| `/projects/list/` | Список проектов (фильтрация по навыку `?skill=`) |
| `/projects/<id>/` | Страница проекта |
| `/projects/create-project/` | Создание проекта |
| `/projects/<id>/edit/` | Редактирование проекта |
| `/projects/<id>/complete/` | Завершить проект (POST, JSON) |
| `/projects/<id>/toggle-participate/` | Присоединиться/выйти (POST, JSON) |
| `/projects/skills/?q=` | Автодополнение навыков (GET, JSON) |
| `/projects/<id>/skills/add/` | Добавить навык к проекту (POST, JSON) |
| `/projects/<id>/skills/<sid>/remove/` | Удалить навык из проекта (POST, JSON) |
| `/users/list/` | Список пользователей |
| `/users/<id>/` | Профиль пользователя |
| `/users/<id>/edit/` | Редактирование профиля |
| `/users/register/` | Регистрация |
| `/users/login/` | Вход |
| `/users/logout/` | Выход |
| `/users/change-password/` | Смена пароля |

## Особенности реализации

- Кастомная модель `User` с авторизацией по email (`USERNAME_FIELD = "email"`)
- При создании пользователя автоматически генерируется аватар с первой буквой имени
- Телефон нормализуется к формату `+7XXXXXXXXXX`
- Валидация GitHub-ссылки (должна вести на github.com)
- Модель `Skill` — отдельная сущность, связанная с `Project` через ManyToMany (`skill.projects`)
