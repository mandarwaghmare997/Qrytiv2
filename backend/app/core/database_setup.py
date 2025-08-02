"""
Database Setup and Migration Utilities
Handles PostgreSQL setup, migrations, and data seeding

Developed by: Qryti Dev Team
"""

import logging
import asyncio
from typing import Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models import *  # Import all models

logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Database setup and migration utilities"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def check_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def create_database_if_not_exists(self) -> bool:
        """Create database if it doesn't exist (PostgreSQL only)"""
        if not settings.DATABASE_URL.startswith("postgresql"):
            logger.info("Using SQLite - database will be created automatically")
            return True
        
        try:
            # Extract database name from URL
            db_url_parts = settings.DATABASE_URL.split("/")
            db_name = db_url_parts[-1].split("?")[0]  # Remove query params
            base_url = "/".join(db_url_parts[:-1]) + "/postgres"
            
            # Connect to postgres database to create our database
            temp_engine = create_engine(base_url.replace("postgresql://", "postgresql+psycopg2://"))
            
            with temp_engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
                )
                
                if not result.fetchone():
                    # Create database
                    conn.execute(text("COMMIT"))  # End any transaction
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    logger.info(f"✅ Created database: {db_name}")
                else:
                    logger.info(f"✅ Database already exists: {db_name}")
            
            temp_engine.dispose()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create database: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            # Import all models to ensure they're registered
            from app.models import (
                user, organization, assessment, stage, 
                control, evidence, audit_log
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created successfully")
            
            # Verify tables were created
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"✅ Created tables: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def seed_initial_data(self) -> bool:
        """Seed database with initial data"""
        try:
            db = self.SessionLocal()
            
            # Check if data already exists
            from app.models.user import User
            if db.query(User).first():
                logger.info("✅ Database already has data - skipping seed")
                db.close()
                return True
            
            # Create default admin user
            from app.models.user import User, UserRole
            from app.models.organization import Organization
            from passlib.context import CryptContext
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Create default organization
            default_org = Organization(
                name="Qryti Demo Organization",
                domain="demo.qryti.com",
                industry="Technology",
                size_category="medium",
                is_active=True
            )
            db.add(default_org)
            db.flush()  # Get the ID
            
            # Create admin user
            admin_user = User(
                email="admin@demo.qryti.com",
                full_name="Admin User",
                hashed_password=pwd_context.hash("admin123"),
                role=UserRole.ADMIN,
                organization_id=default_org.id,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            
            # Create regular user
            regular_user = User(
                email="user@demo.qryti.com",
                full_name="Demo User",
                hashed_password=pwd_context.hash("user123"),
                role=UserRole.USER,
                organization_id=default_org.id,
                is_active=True,
                is_verified=True
            )
            db.add(regular_user)
            
            db.commit()
            logger.info("✅ Initial data seeded successfully")
            logger.info("   Admin: admin@demo.qryti.com / admin123")
            logger.info("   User:  user@demo.qryti.com / user123")
            
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to seed initial data: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return False
    
    def setup_database(self) -> bool:
        """Complete database setup process"""
        logger.info("🚀 Starting database setup...")
        
        # Step 1: Create database if needed
        if not self.create_database_if_not_exists():
            return False
        
        # Step 2: Check connection
        if not self.check_connection():
            return False
        
        # Step 3: Create tables
        if not self.create_tables():
            return False
        
        # Step 4: Seed initial data
        if not self.seed_initial_data():
            return False
        
        logger.info("✅ Database setup completed successfully!")
        return True
    
    def reset_database(self) -> bool:
        """Reset database (drop and recreate all tables)"""
        try:
            logger.warning("🔄 Resetting database - all data will be lost!")
            
            # Drop all tables
            Base.metadata.drop_all(bind=self.engine)
            logger.info("✅ Dropped all tables")
            
            # Recreate tables
            if not self.create_tables():
                return False
            
            # Seed initial data
            if not self.seed_initial_data():
                return False
            
            logger.info("✅ Database reset completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reset database: {e}")
            return False

# Global database setup instance
db_setup = DatabaseSetup()

def setup_database():
    """Setup database - can be called from main.py or CLI"""
    return db_setup.setup_database()

def reset_database():
    """Reset database - can be called from CLI"""
    return db_setup.reset_database()

if __name__ == "__main__":
    # CLI interface for database operations
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "setup":
            success = setup_database()
            sys.exit(0 if success else 1)
        elif command == "reset":
            success = reset_database()
            sys.exit(0 if success else 1)
        else:
            print("Usage: python database_setup.py [setup|reset]")
            sys.exit(1)
    else:
        # Default action
        success = setup_database()
        sys.exit(0 if success else 1)

