# Веб-приложение ToDo list

Курсовая работа по предмету "Разработка клиент-серверных приложений"

**Автор: Кузнецов Ярослав**

**Тема**: «Разработка клиент-серверного приложения для управления списком дел.»

**Исходные данные**: Git, Flask, Postgre SQL, Docker.

**Перечень вопросов, подлежащих разработке, и обязательного графического материала**: 
1. ✅ Провести анализ предметной области для выбранной темы. 
2. ✅ Выбрать клиент-серверную архитектуру для разрабатываемого приложения и дать её детальное описание с помощью UML. 
3. ✅ Выбрать программный стек для реализации фуллстек CRUD приложения. 
4. ✅ Разработать клиентскую и серверную части приложения, реализовать авторизацию и аутентификацию пользователя, обеспечить работу с базой данных, заполнить тестовыми данными, валидировать ролевую модель на некорректные данные. 
5. ✅ Провести фаззинг-тестирование. 
6. ✅ Разместить исходный код клиент-серверного приложения в репозитории GitHub с наличием Dockerfile и описанием структуры проекта в readme файле. 
7. ✅ Развернуть клиент-серверное приложение в облаке. 
8. ✅ Разработать презентацию с графическими материалами.

## Используемые технологии:
* Python3
* Flask
  * Flask-login
  * flask-imiter
  * flask-wtf
* SQLAlchemy

Доступные базы данных:
* sqlite
* MariaDB
* PostgreSQL (используется по умолчанию в контейнеризованной версии)


## Как запустить

### Очень быстро

1. Скачайте конфигурацию для docker-compose
2. Скачайте пример файла .env
3. Запустите docker-compose (если запуск первый, подождите 15-30 секунд и перезапустите контейнер backend или все контейнеры)

```bash
wget https://raw.githubusercontent.com/I-love-linux-12-31/ToDoListWebApp/refs/heads/main/docs/docker-compose-fast-deploy.yaml -O docker-compose.yaml
wget https://raw.githubusercontent.com/I-love-linux-12-31/ToDoListWebApp/refs/heads/main/example.env -O .env
docker-compose up
```

##Структура проекта
### Модули
* backend 
  * api - модуль API
  * ORM - модели ORM
  * tasks - функции для работы с задачами
  * utils - Утилиты для управления сервером (создание администраторов и т.д.)
  * webapp - модуль веб-приложения

### Структура файлов
```
.
├── backend
│   ├── api
│   │   ├── auth.py
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── app.py
│   ├── db.py
│   ├── decorators.py
│   ├── Dockerfile
│   ├── ORM
│   │   ├── __all_models.py
│   │   ├── authtokens.py
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── users.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── run_server.sh
│   ├── static
│   │   ├── csrf.js
│   │   ├── main.css
│   │   └── openapi.yaml
│   ├── tasks
│   │   ├── __init__.py
│   │   └── tasks_list.py
│   ├── templates
│   │   ├── base.html
│   │   ├── errors
│   │   │   ├── 401.html
│   │   │   ├── 403.html
│   │   │   ├── 404.html
│   │   │   ├── 500.html
│   │   │   └── csrf_error.html
│   │   └── webapp
│   │       ├── add_task.html
│   │       ├── login.html
│   │       ├── profile.html
│   │       ├── register.html
│   │       ├── share_task.html
│   │       ├── todo.html
│   │       └── token.html
│   ├── utils
│   │   ├── add_user.py
│   │   └── common.py
│   ├── utils_cmd.py
│   ├── uWSGI.ini
│   └── webapp
│       ├── __init__.py
│       ├── routes_auth.py
│       ├── routes_profile.py
│       ├── routes_todo.py
│       └── routes_token.py
├── CSRF_EXEMPTION.md
├── DEMO_AUTH.md
├── docker-compose.yml
├── docs
│   ├── deployment_diagram.png
│   ├── deployment_diagram.puml
│   ├── docker-compose-fast-deploy.yaml
│   ├── openapi.yaml -> ../backend/static/openapi.yaml
│   ├── README_RU.md
│   ├── use_case.puml
│   └── РКСП_Курсовая.pdf
├── example.env
├── LICENSE
├── nginx
│   ├── 00-to-do-list.conf
│   └── Dockerfile
├── pytest.ini
├── README.md
├── run_fuzz_tests.sh
├── test_api_csrf.py
├── tests
│   ├── conftest.py
│   ├── fuzz
│   │   ├── test_api_auth_fuzz.py
│   │   ├── test_api_tasks_fuzz.py
│   │   └── test_webapp_csrf_fuzz.py
│   └── README.md
└── tests_requirements.txt
```

## Документация

OpenAPI документация:
* файл - ``backend/static/openapi.yaml``
* веб-страница - ``{URL_PREFIX}/api/v1/docs``

## О приложении

### Веб-страницы

#### API
* Документация OpenAPI 
* Управление токенами API

### Управление учетной записью
* Вход
* Регистрация
* Управление профилем

### To-do список
* Главная страница
* Страница добавления задачи
* Страница обмена задачами

### Модели

#### 1. Задачи
#### 2. Пользователи
#### 3. AuthTokens
#### Контроль доступа

В проекте используется модель контроля доступа на основе ролей пользователей.

Для модели User:

1. Пользователь может видеть только свои данные.
2. Администраторы могут изменять данные пользователей.

Для модели Task:
1. Анонимные пользователи могут видеть только общедоступные задачи (только для чтения).
2. Пользователь может редактировать свои задачи и общедоступные задачи (если имеет разрешение на запись).
3. Администратор может работать со всеми задачами.
