# Food_assistant project
## Проект Продуктовый помощник

## Описание:
Проект «Продуктовый помощник» представляет собой онлайн-сервис и API для него. На этом сервисе пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Пользователям сайта также будет доступен сервис «Список покупок». 
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии:
- Python 3.9
- Django 3.2
- djangorestframework 3.12
- Djoser 2.2
- gunicorn 20.1
- PostgreSQL 13.0
- nginx

## Установка и запуск проекта:
Клонировать репозиторий:
```
https://github.com/KonstantinSKS/food_assistant.git
```
- Для адаптации проекта на своем удаленном сервере добавьте секреты в GitHub Actions:
```
DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # ip_address сервера
USER                           # имя пользователя
SSH_KEY                        # приватный ssh-ключ (cat ~/.ssh/id_rsa)
SSH_PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа

TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
```
- В корне проекта cоздайте файл .env по следующему образцу:
```
POSTGRES_DB=<database name>
POSTGRES_USER=<database username>
POSTGRES_PASSWORD=<database password>
DB_HOST=db
DB_PORT=5432

SECRET_KEY = 'your_secret_key'
DEBUG = False
```

## Запуск проекта на удаленном сервере:
Каждый раз при пуше в ваш репозиторий GitHub Actions автоматически выполнит следующие шаги:

- Протестирует ваш код с помощью Flake8.
- Соберет и запушит Docker-образ в Docker Hub.
- Выполнит деплой на удаленный сервер с использованием SSH.
- Отправит уведомление в Telegram о успешном деплое.

#
Автор: Стеблев Константин
