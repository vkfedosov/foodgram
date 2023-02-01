# Проект продуктовый помощник Foodgram

[![](https://github.com/vkfedosov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/vkfedosov/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

Foodgram - продуктовый помощник, позволяет публиковать рецепты,
подписываться на публикации других пользователей, добавлять понравившиеся
рецепты в «Избранное» и «Список покупок». Доступно скачивание сводного
списка продуктов в формате txt, необходимых для приготовления одного или
нескольких выбранных блюд.
Для приложения настроен Continuous Integration (CI) и Continuous Deployment (CD).

Реализован:
* автоматический запуск теста;
* обновление образов на DockerHub;
* автоматический деплой на боевой сервер при push-е в главную ветку main.

## Описание проекта:
### Главная страница
На странице - cписок первых шести рецептов, отсортированных по дате публикации
(от новых к старым). Остальные рецепты доступны на следующих страницах: внизу
страницы есть пагинация.

### Страница рецепта
На странице - полное описание рецепта. Для авторизованных пользователей -
возможность добавить рецепт в избранное и в список покупок, возможность
подписаться на автора рецепта.

### Страница пользователя
На странице - имя пользователя, все рецепты, опубликованные пользователем и
возможность подписаться на пользователя.

### Подписка на авторов
Подписка на публикации доступна только авторизованному пользователю. Страница
подписок доступна только владельцу.

Сценарий поведения пользователя:
1. Пользователь переходит на страницу другого пользователя или на страницу 
   рецепта и подписывается на публикации автора кликом по кнопке «Подписаться
   на автора».
2. Пользователь переходит на страницу «Мои подписки» и просматривает
   список рецептов, опубликованных теми авторами, на которых он подписался.
   Сортировка записей - по дате публикации (от новых к старым). 
3. При необходимости пользователь может отказаться от подписки на автора:
   переходит на страницу автора или на страницу его рецепта и нажимает
   «Отписаться от автора».

### Список избранного
Список избранного может просматривать только его владелец. Сценарий поведения пользователя:
1. Пользователь отмечает один или несколько рецептов кликом по кнопке
   «Добавить в избранное».
2. Переходит на страницу «Список избранного» и просматривает
   персональный список избранных рецептов. При необходимости пользователь может 
   удалить рецепт из избранного.

### Список покупок
Список покупок может просматривать только его владелец.
Сценарий поведения пользователя:
1. Пользователь отмечает один или несколько рецептов кликом по кнопке
   «Добавить в покупки».
2. Пользователь переходит на страницу Список покупок, там доступны все
   добавленные в список рецепты. Пользователь нажимает кнопку «Скачать список»
   и получает файл с суммированным перечнем и количеством необходимых
   ингредиентов для всех рецептов, сохранённых в «Списке покупок».
3. При необходимости пользователь может удалить рецепт из списка покупок.

Список покупок скачивается в формате txt. При скачивании списка покупок
ингредиенты в результирующем списке не дублируются;
если в двух рецептах есть сахар (в одном рецепте - 5 г, в другом - 10 г),
то в списке будет один пункт: Сахар - 15 г.
В результате список покупок выглядит так:
* Фарш (баранина и говядина) - 600 г
* Сыр плавленый - 200 г
* Лук репчатый - 50 г

### Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом.
Фильтрация может проводится по нескольким тегам. При фильтрации на странице
пользователя фильтруются только рецепты выбранного пользователя. Такой же
принцип соблюдается при фильтрации списка избранного.

### Дизайн-макеты проекта можно посмотреть на:
[Figma.com](https://www.figma.com/file/HHEJ68zF1bCa7Dx8ZsGxFh/Продуктовый-помощник-Final?node-id=0%3A)

## Стек технологий:
* [Python 3.9+](https://www.python.org/downloads/)
* [Django 3.2.16](https://www.djangoproject.com/download/)
* [django_filter 22.1](https://pypi.org/project/django-filter/#files)
* [djangorestframework-simplejwt 4.8.0](https://pypi.org/project/djangorestframework-simplejwt/)
* [djangorestframework 3.14.0](https://pypi.org/project/djangorestframework/#files)
* [djoser 2.1.0](https://pypi.org/project/djoser/#files)
* [flake8-broken-line 0.6.0](https://pypi.org/project/flake8-broken-line/#files)
* [flake8-isort 6.0.0](https://pypi.org/project/flake8-isort/#files)
* [flake8-return 1.2.0](https://pypi.org/project/flake8-return/#files)
* [flake8 5.0.4](https://pypi.org/project/flake8/#files)
* [gunicorn 20.1.0](https://pypi.org/project/gunicorn/#files)
* [isort 5.11.4](https://pypi.org/project/isort/#files)
* [pep8-naming 0.13.3](https://pypi.org/project/pep8-naming/#files)
* [psycopg2-binary 2.9.5](https://pypi.org/project/psycopg2-binary/#files)
* [python-dotenv 0.21.1](https://pypi.org/project/python-dotenv/#files)

## Начало работы
* Клонировать репозиторий, перейти в директорию с проектом:
```bash
git clone git@github.com:vkfedosov/foodgram-project-react.git
```
```bash
cd foodgram-project-react
```

* Установить виртуальное окружение, активировать его:
```bash
python -m venv venv
. venv/scripts/activate
```

* Перейти в директорию ```backend```, установить зависимости:
```bash
pip install -r requirements.txt
```

* В директории ```backend/foodgram```, создать файл ```.env``` с переменными
окружения:
```
# settings.py
SECRET_KEY='<secret_key>'    # стандартный ключ, который создается при старте проекта
DEBUG=False                  # опция отладчика True/False
ALLOWED_HOSTS                # список хостов/доменов, для которых дотсупен текущий проект

ENGINE=django.db.backends.postgresql
DB_NAME                      # имя БД - postgres (по умолчанию)
POSTGRES_USER                # логин для подключения к БД - postgres (по умолчанию)
POSTGRES_PASSWORD            # пароль для подключения к БД (установите свой)
DB_HOST=db                   # название сервиса (контейнера)
DB_PORT=5432                 # порт для подключения к БД

# default.conf.template
SERVERHOST                   # имя хоста/домена
PORT                         # порт для подключения
UPSTREAM                     # название сервиса (контейнера) в формате: <название сервиса>:<порт>
```

* Скопировать файл ```.env``` в  ```infra```.

* В директории ```infra``` отредактировать файл ```default.conf.template```.
Изменить server_name (вписать IP-адрес виртуальной машины (сервера), добавить
хост, если потребуется), проверить порты.

## Workflow
Для использования Continuous Integration (CI) и Continuous Deployment (CD): в
репозитории GitHub Actions ```Settings/Secrets/Actions``` прописать Secrets -
переменные окружения для доступа к сервисам:

```
SECRET_KEY='<secret_key>'    # стандартный ключ, который создается при старте проекта,
                             # ключ должен быть заключен в '...'
DEBUG=False                  # опция отладчика True/False
ALLOWED_HOSTS                # список хостов/доменов, для которых дотсупен текущий проект
                             # изменить IP-адрес сервера и/или добавить имя хоста

ENGINE=django.db.backends.postgresql
DB_NAME                      # имя БД - postgres (по умолчанию)
POSTGRES_USER                # логин для подключения к БД - postgres (по умолчанию)
POSTGRES_PASSWORD            # пароль для подключения к БД (установите свой)
DB_HOST=db                   # название сервиса (контейнера)
DB_PORT=5432                 # порт для подключения к БД

SERVERHOST                   # имя хоста/домена
PORT                         # порт для подключения
UPSTREAM                     # название сервиса (контейнера) в формате: <название сервиса>:<порт>

DOCKER_USERNAME              # имя пользователя в DockerHub
DOCKER_PASSWORD              # пароль пользователя в DockerHub
HOST                         # ip_address сервера
USER                         # имя пользователя
SSH_KEY                      # приватный ssh-ключ локального ПК имеющего доступ к серверу (cat ~/.ssh/id_rsa)
                             # ключ вводится полностью, начиная с -----BEGIN OPENSSH PRIVATE KEY-----
                             # до -----END OPENSSH PRIVATE KEY-----

PASSPHRASE                   # кодовая фраза (пароль) для ssh-ключа

TELEGRAM_TO                  # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN               # токен бота (получить токен можно у @BotFather, /token, имя бота)
```

При push в ветку main автоматически отрабатывают сценарии:
* *tests* - проверка кода на соответствие стандарту PEP8.
Дальнейшие шаги выполняются только если push был в ветку main;
* *build_and_push_to_docker_hub* - сборка и доставка докер-образов на DockerHub
* *deploy* - автоматический деплой проекта на боевой сервер. Выполняется
копирование файлов из DockerHub на сервер;
* *send_message* - отправка уведомления в Telegram.

## Подготовка удалённого сервера
* Войти на удалённый сервер, для этого необходимо знать адрес сервера, имя
пользователя и пароль. Адрес сервера указывается по IP-адресу или по доменному
имени:
```bash
ssh <username>@<ip_address>
```

* Остановить службу ```nginx```:
```bash
sudo systemctl stop nginx
```

* Установить Docker и Docker-compose:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install docker.io
sudo apt install docker-compose -y
```

* Проверить корректность установки Docker-compose:
```bash
sudo docker-compose --version
```
* На сервере создать директорию ```nginx/templates/``` :
```bash
mkdir -p nginx/templates/
```

* Скопировать файлы ```docker-compose.yaml```, ```.env``` и
```default.conf.template``` из проекта (локально) на сервер:
  * перейти в директорию ```infra``` и выполните:
  ```bash
  scp docker-compose.yml <username>@<ip_address>:/home/<username>/docker-compose.yml
  scp .env <username>@<ip_address>:/home/<username>/.env
  ```
  * перейти в директорию ```infra/nginx/templates``` и выполните:
  ```bash
  scp default.conf.template <username>@<ip_address>:/home/<username>/nginx/templates/default.conf.template
  ```

## После успешного деплоя
* Создать суперпользователя:
```bash
sudo docker-compose exec backend python manage.py createsuperuser
```

## Набор доступных эндпоинтов для API Foodgram:
- ```api/docs/redoc``` - подробная документация по работе API Foodgram;
- ```api/tags/``` - получение, списка тегов (GET);
- ```api/ingredients/``` - получение, списка ингредиентов (GET);
- ```api/ingredients/``` - получение ингредиента с соответствующим id (GET);
- ```api/tags/{id}``` - получение, тега с соответствующим id (GET);
- ```api/recipes/``` - получение списка с рецептами и публикация рецептов
     (GET, POST);
- ```api/recipes/{id}``` - получение, изменение, удаление рецепта с
     соответствующим id (GET, PUT, PATCH, DELETE);
- ```api/recipes/{id}/shopping_cart/``` - добавление рецепта с соответствующим
     id в список покупок и удаление из списка (GET, DELETE);
- ```api/recipes/download_shopping_cart/``` - скачать файл со списком покупок
     shopping_cart.txt (GET);
- ```api/recipes/{id}/favorite/``` - добавление рецепта с соответствующим id в
     список избранного и его удаление (GET, DELETE).

### Операции с пользователями:
- ```api/users/``` - получение информации о пользователе и регистрация новых
     пользователей (GET, POST);
- ```api/users/{id}/``` - получение информации о пользователе (GET);
- ```api/users/me/``` - получение и изменение данных своей учётной записи.
     Доступна любым авторизованными пользователям (GET);
- ```api/users/set_password/``` - изменение собственного пароля (PATCH);
- ```api/users/{id}/subscribe/``` - подписаться на пользователя с
     соответствующим id или отписаться от него (GET, DELETE);
- ```api/users/subscribe/subscriptions/``` - просмотр пользователей на которых
     подписан текущий пользователь (GET).

### Аутентификация и создание новых пользователей:
- ```api/auth/token/login/``` - получение токена (POST);
- ```api/auth/token/logout/``` - удаление токена (POST).

## Тестирование API Foodgram
Провести тестирование API Foodgram можно с помощью Postman.
Для этого необходимо [импортировать](https://learning.postman.com/docs/integrations/available-integrations/working-with-openAPI/)
коллекции с вышеперечисленными эндпоинтами из файла ```docs/openapi-schema.yml``` в Postman.

### Алгоритм регистрации пользователей
* Пользователь отправляет POST-запрос для регистрации нового пользователя 
на эндпойнт ```/api/users/```с параметрами:
```json
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```
* Пользователь отправляет POST-запрос на на эндпоинт ```/api/token/login/``` 
c данными указанными при регистрации:
```json
{
    "email": "vpupkin@yandex.ru",
    "password": "Qwerty123"
}
```
в ответе на запрос ему приходит:
```json
{
    "auth-token": "8c02a1..."
}
```
Полученный токен добавляем в ```Postman/Collections/Foodgram/Headers/api```:

```Key:```
Authorization
```Value:```
Token 8c02a1...

И далее тестируем API Foodgram согласно документации ```api/docs/redoc```.

## Авторы
[vkfedosov](https://github.com/vkfedosov) - бэкенд и CI/CD для Foodgram;

[Яндекс.Практикум](https://github.com/yandex-praktikum) - фронтенд
для Foodgram.