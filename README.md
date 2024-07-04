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

## Установка проекта
- Сделайте fork репозитория, затем клонируйте его:
```
git clone https://github.com/ZebraHr/grocery_helper
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
- На удаленном сервере создайте папку foodgram/
- На удаленном сервере в папке проекта cоздайте файл .env:
```
POSTGRES_DB=<Желаемое_имя_базы_данных>
POSTGRES_USER=<Желаемое_имя_пользователя_базы_данных>
POSTGRES_PASSWORD=<Желаемый_пароль_пользователя_базы_данных>
DB_HOST=db
DB_PORT=5432

SECRET_KEY = 'ваш_secret_key'
ALLOWED_HOSTS = ip_удаленного сервера, доменное имя, 127.0.0.1, localhost
DEBUG = False
```
- Установка Nginx. Находясь на удалённом сервере, из любой директории выполните команду, затем запустите Nginx:
```
sudo apt install nginx -y 
sudo systemctl start nginx
```
- Перейдите в файл конфигурации nginx и измените его настройки на следующие:
```
nano /etc/nginx/sites-enabled/default
```
```
server {
    server_name server_name <публичный-IP-адрес> <доменное-имя>;
    server_tokens_off;
    client_max_body_size 30M;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }

}
```
- Перезарузите Nginx:
```
sudo nginx -t
sudo systemctl reload nginx
```
- Откройте порты для фаервола и активируйте его:
```
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```
- (Опционально) Получите SSL-сертификат для вашего доменного имени с помощью Certbot:
```
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot 
sudo certbot --nginx
```
- Пуш в любую ветку запускает тестирование и деплой Foodgram на ваш удаленный сервер, а после успешного деплоя вам приходит оповещение в телеграм.

#
Автор: Стеблев Константин
