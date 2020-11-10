#### Старт 

```shell script
python run.py
```
По умолчанию `0.0.0.0:5000`

аргументы `--host` `--port`.

количество воркеров `-w` или `--workers`
#### Запрос

```
POST /api/
```
```json
{
   "count": 200,
   "delta": 2.4,
   "start": 1.56,
   "interval": 6
}
```
Статистика по задачам

```
GET /stats/
```

Ответ

```json
[
    {
        "count":200,
        "delta":2.4,
        "start":1.56,
        "interval":6,
        "number_task":1,
        "start_date":"2020-11-10 23:28:48.190207",
        "result":11.16,
        "status":"process"
    },
    {
        "count":20,
        "delta":2.4,
        "start":1.56,
        "interval":6,
        "number_task":11,
        "start_date":null,
        "status":"queue"
    }
]

```


