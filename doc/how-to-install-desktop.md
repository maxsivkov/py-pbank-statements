## Установка на десктоп

- Устанавливаем [Java](https://www.java.com/ru/) - необходимо для [swagger codegen](https://swagger.io/tools/swagger-codegen/) для создания SDK, потом можно удалить.
- ОПЦИОНАЛЬНО Устанавливаем [Git](https://git-scm.com/) (я рекомендую использовать [chocolatey](https://chocolatey.org/))
- Установить Python 3.7 or later (я рекомендую использовать [chocolatey](https://chocolatey.org/))
- Запустить АПИ сервер [Taxer API](https://github.com/maxsivkov/py-taxer-api)
- Открыть коммандную строку `cmd`
- Склонировать прект
  ```
  git clone https://github.com/maxsivkov/py-pbank-statements
  ```
  Либо скачать и распаковать архив с проектом
- Перейти в папку с проектом
- Сгенерировать [SDK Taxer API](https://github.com/maxsivkov/py-taxer-api)
  ```
  .\generate-sdk.bat
  ```
  В результате будет создан каталог `api-src`, внутри будет сгенерирован SDK для [Taxer API](https://github.com/maxsivkov/py-taxer-api)
- Устанавливаем venv
  ```
  python -m venv venv
  ```
- Активируем venv
  ```
  venv\Scripts\activate
  ```
- Устанавливаем зависимости
  ```
  pip install .
  ```
- Устанавливаем taxerapi
  ```
  python -m pip install ./api-src
  ```
- Проверяем что все работает
  ```
  python main.py test
  ```
  В результате в выводе должно появиться чтото типа `Action test`
