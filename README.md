# TOTP Service with Python

Ejemplo de implementacion TOTP con lib [Pytotp](https://github.com/pyauth/pyotp) y [FastApi](https://fastapi.tiangolo.com/)

### Requerimientos:
------------

<ul>
  <li>Python 3.11</li>
  <li>Docker</li>
</ul>

### Install requirements
------------

```
pip3 install requirements.tx
```

### Correr una instancia de Redis
------------

```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### Correr una instancia de Redis con password
------------

```
docker run -e REDIS_ARGS="--requirepass pass-redis-stack" -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```


### Start service
```
uvicorn main:app --reload
```


### Levantar contenedor Redis con password y admin web
```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest --requirepass "SUPER_SECRET_PASSWORD"
```

## Levantar todos los servicios con docker-compose
### Build
```
docker-compose build
```

### Start
```
docker-compose up
```

### Stop
```
docker-compose down
```
