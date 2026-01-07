# crm-fastapi-light

запустить

```git clone https://github.com/cojode/crm-fastapi-light.git```

```cd crm-fastapi-light```

```git checkout develop```

```cp .env.example .env```

```docker compose up --build -d```

```http://localhost:8000/api/health/``` <---- 200

```docker compose exec crm-fastapi-light alembic upgrade head```

посмотреть

```localhost:8000```

```localhost:8000/api/docs```

```localhost:8000/admin```
