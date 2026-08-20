-- OpenClinica database role
-- Source: OpenClinica/ws/src/main/config/database/PostgreSQL/install/create_role.sql
CREATE ROLE clinica LOGIN
  ENCRYPTED PASSWORD 'clinica'
  SUPERUSER NOINHERIT NOCREATEDB NOCREATEROLE;
