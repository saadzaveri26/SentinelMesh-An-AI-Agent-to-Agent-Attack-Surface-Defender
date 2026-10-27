Write-Host "Setting up SentinelMesh test database (sentinelmesh_test)..." -ForegroundColor Cyan

$dbExists = docker exec sentinelmesh-postgres-1 psql -U sentinel -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='sentinelmesh_test';"
if ($dbExists -ne "1") {
    Write-Host "Creating database sentinelmesh_test..." -ForegroundColor Yellow
    docker exec sentinelmesh-postgres-1 psql -U sentinel -d postgres -c "CREATE DATABASE sentinelmesh_test;"
} else {
    Write-Host "Database sentinelmesh_test already exists." -ForegroundColor Green
}

Write-Host "Applying database schema to sentinelmesh_test..." -ForegroundColor Cyan
python -c "import sys, os; sys.path.insert(0, r'app_build\backend'); from sqlalchemy import create_engine; from app.models import Base; eng = create_engine('postgresql+psycopg2://sentinel:sentinel_dev_2026@localhost:5432/sentinelmesh_test'); Base.metadata.create_all(bind=eng); print('Schema applied successfully.')"

Write-Host "Stamping alembic head on sentinelmesh_test..." -ForegroundColor Cyan
python -c "import os, sys; os.chdir(r'app_build\backend'); os.environ['DATABASE_URL']='postgresql+psycopg2://sentinel:sentinel_dev_2026@localhost:5432/sentinelmesh_test'; from alembic.config import Config; from alembic import command; cfg = Config('alembic.ini'); command.stamp(cfg, 'head'); print('Alembic stamped at head.')"

Write-Host "Test database setup complete." -ForegroundColor Green
