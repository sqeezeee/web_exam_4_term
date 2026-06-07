# АИС «Электронная библиотека»

**Автор:** Набиуллин Артур Фанилевич, группа 241-326  
**Вариант:** 3 (поиск книг)

## Стек

- Python 3, Flask, SQLAlchemy
- PostgreSQL 16 (Docker)
- Jinja2, Bootstrap 5, EasyMDE, Bleach, Markdown


## Тестовые учётные записи

| Логин     | Пароль   | Роль          |
|-----------|----------|---------------|
| admin     | admin123 | Администратор |
| moderator | mod123   | Модератор     |
| user      | user123  | Пользователь  |

## Структура проекта

```
app/
  blueprints/   — маршруты (auth, main, books, reviews)
  models/       — модели SQLAlchemy
  services/     — бизнес-логика (поиск, обложки, markdown)
  decorators.py — проверка ролей
templates/      — шаблоны Jinja2
static/         — CSS и загруженные обложки
```
