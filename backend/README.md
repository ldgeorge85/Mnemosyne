# Mnemosyne Backend

This directory contains the backend API server for the Mnemosyne project, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Setup and Installation

1. Ensure Docker and Docker Compose are installed on your system
2. Run the following command from the project root:
   ```
   docker compose up -d
   ```

## Key Components

- **FastAPI Application**: Located in `/app/main.py`
- **Database Models**: Located in `/app/db/models/`
- **API Endpoints**: Located in `/app/api/v1/endpoints/`
- **Database Repositories**: Located in `/app/db/repositories/`

## Database Management

### Table Creation

The backend provides multiple ways to initialize and manage database tables:

1. **Automatic Initialization**: The `app/db/init_db.py` script runs during application startup to create essential tables.

2. **Manual Table Creation**: Use the `create_tables.py` script to manually create missing tables:
   ```
   docker compose exec backend python create_tables.py
   ```

   This script will:
   - Check for existing tables in the PostgreSQL database
   - Create any missing tables with proper foreign key constraints
   - Create appropriate indexes for performance
   - Show detailed logging of actions taken

3. **Alembic Migrations**: For more complex schema changes, use Alembic migrations:
   ```
   docker compose exec backend python migrate.py create "migration description"
   docker compose exec backend python migrate.py upgrade
   ```

### Common Database Issues

If you encounter database-related errors:

1. **Missing Tables**: Use `create_tables.py` to create missing tables.
2. **Foreign Key Errors**: Ensure models reference the correct table names (plural vs. singular).
3. **SQLAlchemy Errors**: Check the `debugging_guide.md` for solutions to common SQLAlchemy issues.

## API Documentation

Once the server is running, visit http://localhost:8000/docs for the interactive API documentation.

## Testing

Run tests with:
```
docker compose exec backend pytest
```

For API testing, refer to the testing guide in `/docs/phase2_testing_guide.md`.
