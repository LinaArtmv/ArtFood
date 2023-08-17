# ArtFood

### Cайт для размещения рецептов.
### Любой желающий может изучить опубликованные рецепты, а после авторизации - добавить свои.

### Запуск проекта
- Клонируйте репозиторий и перейдите в него
```
git clone https://github.com/linaartmv/ArtFood.git
cd ArtFood
```
- Установите и активируйте виртуальное окружение
```
python -m venv venv
source venv/bin/activate
``` 
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Выполните миграции:
```
python manage.py makemigrations
python manage.py migrate
```
- Загрузите в БД тестовые записи (опционально):
```
python manage.py load
```
- В папке с файлом manage.py выполните команду:
```
python manage.py runserver
```

### Технологии
- [Python 3.7](https://www.python.org/downloads/)
- [Django 2.2](https://www.djangoproject.com/)
- [SQLite3](https://www.sqlite.org/docs.html)

### Автор
- Ангелина Артемьева
github: [LinaArtmv](https://github.com/LinaArtmv)
