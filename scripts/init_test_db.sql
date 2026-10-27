SELECT 'CREATE DATABASE sentinelmesh_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sentinelmesh_test')\gexec
