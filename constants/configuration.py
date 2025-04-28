class Configuration:
    import os
    from sqlalchemy.ext.declarative import declarative_base

    BASE = declarative_base()
    SECRET_KEY = os.getenv("AUTH_SECRET")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    CRYPT_SCHEME = "pbkdf2_sha256"
    OPENAI_AI_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_CONNECTION_PARAMETERS = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost\\BACHELOR;"
        "Database=BACHELOR;"
        "Trusted_Connection=yes;"
    )
    
