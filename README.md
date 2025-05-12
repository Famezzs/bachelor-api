# Інструкція з запуску Python-додатку

## Підготовка

1. Переконайтесь, що встановлено Python 3.8 або новіший.
2. Встановіть необхідні залежності вручну:

```bash
pip install fastapi uvicorn openai python-jose passlib[bcrypt] sqlalchemy pydantic
```

## Змінні середовища

Встановіть відповідні значення змінним середовища Вашої системи 

```
AUTH_SECRET=your_secret_key
OPENAI_API_KEY=your_openai_key
```

## Запуск

Перейдіть у директорію з файлом `main.py` і виконайте:

```bash
uvicorn main:app --host 0.0.0.0 --port 4444
```

Після запуску додаток буде доступний за адресою:

```
http://localhost:4444
```
