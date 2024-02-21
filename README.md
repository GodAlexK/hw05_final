# **Проект "Cоциальная сеть с для публикации личных дневников"**

## ****Описание****
Yatube - cоциальная сеть для публикации личных дневников. Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи. Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи. 
Проект разработан по MVT архитектуре, используется пагинация постов и кэширование,
написаны тесты с использованием библиотеки Unittest, регистрация и аутентификация.
## ****Использованные технологии****
- [Python](https://www.python.org/) - язык программирования;
- [Django](https://django.fun/ru/docs/django/4.1/)- cвободный фреймворк для веб-приложений на языке Python, использующий шаблон проектирования MVC;
- [Django REST framework](https://www.django-rest-framework.org/) - это мощный и гибкий набор инструментов для создания Web API;
- [Django Rest framework-Simple JWT(JSON WEB Token)](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) - это открытый стандарт для создания токенов доступа, основанный на формате JSON;
- [Requests](https://requests.readthedocs.io/en/latest/index.html) - данная библиотека упрощает генерацию HTTP-запросов к другим сервисам, помогает писать их очень просто и быстро;
- [Postman](https://www.postman.com/) - cервис для создания, тестирования, документирования, публикации и обслуживания API. Он позволяет создавать коллекции запросов к любому API, применять к ним разные окружения
Инструменты и стек: Python , HTML , CSS , Django, Bootstrap, Unittest , Pythonanywhere.
## **Установка проекта**
 - [ ] Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone git@github.com:GodAlexK/api_final_yatube.git
```
```
cd api_final_yatube
```
 - [ ] Создайте и активируйте виртуальное окружение
```
python -m venv venv
```
```
source venv/Scripts/activate
```
 - [ ] Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
 - [ ] В папке с файлом manage.py выполните миграции:
```
python manage.py migrate
```
 - [ ] Запустите сервер:
 ```
python manage.py runserver
```
