# Проект «Социальная сеть Yatube»
## Описание
### Социальная сеть Yatube для публикаций сообщений, с возможностью размещения картинок, комментирования и подписок на авторов.

## API для Yatube
### В рамках данного проекта реализуется REST API для работы со следующими сущностями:
* `Публикации` - Получение списка, Создание, Получение по id, Обновление, Частичное обновление, Удаление
* `Комментарии` - Получение списка, Добавление, Получение по id, Обновление, Частичное обновление, Удаление
* `Сообщества` - Получение списка, Получение по id
* `Подписки` - Получение списка по запросившему пользователю, Подписка на другого пользователя
* `JWT-токен` - Получить, Обновить, Проверить

## Использованные технологии/пакеты
* Python 3.7
* Django 2.2.28
* PyJWT 2.1.0
* django-filter 2.4.0
* djangorestframework 3.12.4
* djangorestframework-simplejwt 4.8.0
* django-debug-toolbar==3.2.4
* djoser 2.1.0
* Pillow 9.3.0
* pytils 0.3
* sorl-thumbnail 12.7.0
* requests 2.26.0
* psycopg2-binary 2.8.6
* python-dotenv 0.21.0
## Установка
* Клонировать проект
```
git clone https://github.com/GritsenkoSerge/yatube.git
```
* Перейти в директорию yatube/infra
```
cd yatube/infra
```
* Создать файл .env с переменными окружения (при необходимости изменить)
```
echo DB_ENGINE=django.db.backends.postgresql > .env
echo DB_NAME=postgres >> .env
echo POSTGRES_USER=postgres >> .env
echo POSTGRES_PASSWORD=postgres >> .env
echo DB_HOST=db >> .env
echo DB_PORT=5432 >> .env
echo -ne DJANGO_SECRET_KEY= >> .env
openssl rand -base64 33 >> .env
```
* Собрать и запустить контейнеры 
```
docker-compose up -d --build
```
* Произвести миграции
```
docker-compose exec web python3 manage.py migrate
```
* Создать суперпользователя
```
docker-compose exec web python3 manage.py createsuperuser
```
* Собрать статику
```
docker-compose exec web python3 manage.py collectstatic --noinput
```
### После запуска контейнеров проект доступен по адресам: [главная страница](http://localhost/), [спецификация API ReDoc](http://localhost/api/redoc/), [администрирование](http://localhost/admin/)

## Примеры запросов API
#### Регистрация нового пользователя:
```
(POST) /api/v1/auth/signup/
```
#### Ответ:
```
{ 
    "email": "string",
    "username": "string"
}
```
#### Получение JWT-token:
```
(POST) /api/v1/auth/token/
```
#### Ответ:
```
{
    "username": "string",
    "confirmation_code": "string"
}
```

## Проект выполнен студентом коготры №41 курса "Python-разработчик"
[Сергей Гриценко](https://github.com/GritsenkoSerge/)
