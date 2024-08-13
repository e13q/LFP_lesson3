# Парсер книг с сайта tululu.org

В данном проекте реализован парсинг страниц для скачивания книг и информации о них с сайта tululu.org

### Как установить

Python3 должен быть установлен. 
Используйте `pip` для установки зависимостей:
```
pip install -r requirements.txt
```

### Запуск скрипта

Запускать скрипт можно с помощью команды
```
python3 main.py
```
В таком случае скачаются книги с 1 по 10 книги.

Либо, указывая промежуток id книг на сайте
```
python3 main.py 10 20
```
В таком случае скачаются книги с 10 по 20 книги.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков dvmn.org.
