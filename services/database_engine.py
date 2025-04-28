class DatabaseEngine:
    def __init__(self, database_connection_parameters: str):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.declarative import declarative_base
        from constants.configuration import Configuration
        import urllib.parse

        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(database_connection_parameters)}"
        )

        self.base = Configuration.BASE

        from models import user, user_auth, student, teacher, grade, study_session

        self.base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
