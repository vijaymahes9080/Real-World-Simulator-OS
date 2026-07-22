import os
import sqlite3
import duckdb
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Paths for SQLite & DuckDB files (all local, relative to workspace/data directory)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

SQLITE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'simulator.db')}"
DUCKDB_PATH = os.path.join(DATA_DIR, "analytics.duckdb")

# SQLAlchemy setup
engine = create_engine(
    SQLITE_URL, 
    connect_args={"check_same_thread": False}  # Safe for SQLite multithreaded uvicorn
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    SQLAlchemy session generator dependency for REST endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DuckDBManager:
    @staticmethod
    def get_connection():
        """
        Returns a DuckDB connection.
        """
        return duckdb.connect(DUCKDB_PATH)

    @classmethod
    def initialize_schema(cls):
        """
        Sets up the DuckDB analytical tables for time-series simulation runs if not exists.
        """
        conn = cls.get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sim_telemetry (
                    run_id VARCHAR,
                    tick INTEGER,
                    time DOUBLE,
                    metric_name VARCHAR,
                    metric_value DOUBLE,
                    entity_id VARCHAR,
                    entity_type VARCHAR
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    run_id VARCHAR,
                    tick INTEGER,
                    agent_id VARCHAR,
                    agent_name VARCHAR,
                    role VARCHAR,
                    agent_type VARCHAR,
                    resource_name VARCHAR,
                    resource_value DOUBLE
                );
            """)
        finally:
            conn.close()

# Initialize directories & analytical schema on import
DuckDBManager.initialize_schema()
