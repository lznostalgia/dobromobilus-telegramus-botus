from sqlalchemy import create_engine

def create_engine():
    """
    Initializes an in-memory SQLite DB with pysqlite backend #TODO 
    """
    engine = create_engine("sqlite+pysqlite:///:memory:")
