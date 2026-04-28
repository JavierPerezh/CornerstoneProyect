# Setup Local Unificado (Un Solo Computador)

Este flujo deja Frontend + Backend + PostgreSQL corriendo en una sola máquina.

## 1) PostgreSQL

1. Verifica que PostgreSQL esté instalado y que el servicio esté iniciado.
2. Si necesitas instalar en Windows con winget:

```powershell
winget install --id PostgreSQL.PostgreSQL.17 -e
```

3. Crea la base de datos:

```powershell
createdb -U postgres posparto_db
```

4. Ejecuta el esquema/base inicial:

```powershell
psql -U postgres -d posparto_db -f infra/postgres/init.sql
```

Si `createdb` o `psql` no existen en tu terminal, agrega PostgreSQL al PATH o usa la consola SQL de pgAdmin.

Alternativa recomendada (automatizada) desde la raíz de backend-api:

```powershell
./scripts/bootstrap_postgres.ps1
```

## 2) Variables de entorno del backend

En `.env` usa una URL real de PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:TU_CONTRASENA@localhost:5432/posparto_db
```

Nota: si la contraseña contiene caracteres como `@`, `:`, `/`, `?`, `#`, `%`, debes usar URL encoding.

## 3) Levantar backend

Desde la carpeta `backend-api`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health check esperado:

```text
http://127.0.0.1:8000/health
```

## 4) Levantar frontend

En `neocare-frontend`:

```powershell
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1
```

Frontend esperado:

```text
http://127.0.0.1:5173
```

## 5) Credenciales demo iniciales

- Código de registro para login web: `123456`
- Device ID para endpoints de voz: `device-demo-001`

Ambos se generan en `infra/postgres/init.sql`.