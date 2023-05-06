## Запуск сервиса

В корневой папке необходимо создать .env с переменными окружения. 
Переменные и значения можно взять из [.env.example](https://github.com/peroovy/currency-converter/blob/master/.env.example)

Запустить сервис можно с помощью make:
```shell
make up
```
либо выполнить следующую команду:
```shell
docker-compose up --build -d
```

После запуска будет доступна докумантация по ссылке http://localhost/docs/

## Тестирование

Запустить тесты:
```shell
make test
```
или
```shell
docker-compose build
docker-compose run app pytest tests
docker-compose down
```