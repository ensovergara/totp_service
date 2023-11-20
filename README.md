#TOTP Service with Python

Ejemplo de implementacion TOTP con lib [Pytotp](https://github.com/pyauth/pyotp) y [FastApi](https://fastapi.tiangolo.com/)

###Requerimientos:
------------

<ul>
  <li>Python 3.11</li>
  <li>Docker</li>
</ul>

###install requirements
------------

```
pip3 install requirements.tx
```

###Correr una instancia de Redis
------------

```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

###Correr una instancia de Redis con password
------------

```
docker run -e REDIS_ARGS="--requirepass pass-redis-stack" -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```


###start service
```
uvicorn main:app --reload
```


###Para levantar un docker puedes ejecutar el siguiente comando
```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest --requirepass "SUPER_SECRET_PASSWORD"
```