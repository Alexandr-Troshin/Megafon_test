# Megafon_test
В репозитории содержится py-файл к тестовому заданию BigData.Мегафон.   
Скрипт генерирует пользователей и события (звонок, смс, трафик), списывает с баланса с учетом тарифа, формирует ежедневные отчеты и уведомления об окончаниях лимита.  
Начиная со стартовой даты (установлена 01.01.2022) генерируется 5 стартовых пользователей. 
Для каждого пользователя случайным образом выбирается возраст, город, баланс и тариф (список тарифов задан датафреймом в скрипте, состоит их 3 тарфиов, каждому из которых соответствует определенное количество минут, смс и мегабайт трафика).  

Далее запускается генерация внутридневных событий. Через произвольное количество минут с начала дня создается произвольное событие (в 2% случаев - появление нового пользователя, в остальных - расходная операция одного из существующих). Выбирается случайный пользователь, случайный тип события (звонок, трафик или смс) со случайным количеством потребленного ресурса (кроме смс, где расходуется одна единица).   
В случае, если баланс пользователя в процессе события уменьшается до 0 - срабатывает оповещение о расходовании лимита (на экран или в телеграмм-чат при указании токена и id чата). Если выбрано событие у пользователя, по которому балансм уже отрицательный, даннаяч операция не проводится.  
По итогам дня генерируется сводная таблица.
По умолчанию предусмотрено 10 дней, переход между днями по нажатию Enter.
