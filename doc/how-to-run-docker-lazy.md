## Запуск с использованием Docker для ленивых

- Скачать [docker-compose.,yml](https://raw.githubusercontent.com/maxsivkov/py-pbank-statements/master/bundle/docker-compose.yml)

  ```
  curl -o docker-compose.yml https://raw.githubusercontent.com/maxsivkov/py-pbank-statements/master/bundle/docker-compose.yml
  ```

- Создать каталог `data-folder`
  ```
  MD data-folder
  ```

- Получить [taxer cookies](https://github.com/maxsivkov/py-taxer-api/blob/master/doc/howto-run.md#%D0%BA%D0%B0%D0%BA-%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-cookies)
- Создать файл `.env` и поместить туда taxer cookies, должно получиться примерно такое
  ```
  TAXER_COOKIES=_ga=GA1.2.167.......d467a83b53
  ```
  
- Запустить
  ```
  docker-compose run statements test
  ```
  В результате в выводе должно появиться чтото типа `Action test` со списком аккаунтов и пользователей
  

Теперь можно выполнять комманды
```
docker-compose run statements <COMMAND>
```
  
**NOTE**  
После того как работы с данным аккаунтом завершены, необходить застопить все что связано с сервисом `statements`:
```
docker-compose stop
```

