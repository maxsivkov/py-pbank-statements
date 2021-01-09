
## Получение баланса

Необходимо настроить [автоклиент](https://www.google.com/url?q=https://docs.google.com/document/d/e/2PACX-1vTion-fu1RzMCQgZXOYKKWAmvi-QAAxZ7AKnAZESGY5lF2j3nX61RBsa5kXzpu7t5gacl6TgztonrIE/pub&sa=D&ust=1609754137862000&usg=AOvVaw2575WmEHG8jTB-lZq5aTz9)  - получить **ir/token** и прописать их в конфиге

Dыполнить 
  ```
  python main.py balance
  ```
  
В результирующей таблице будут приведены ненулевые счета в банке и в таксере, например
```
Номер счета                               Банк           Taxer Валюта
UA113206490000026000032605432         10000.00        10000.00 UAH
UA673206490000026001057653231          1000.00         1000.00 EUR
Готівковий                                0.00        12122.18 UAH
```

