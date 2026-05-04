param(
    [string]$PgUser = "postgres",
    [string]$PgHost = "localhost",
    [int]$PgPort = 5432,
    [string]$DbName = "posparto_db"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    throw "No se encontro psql en PATH. Instala PostgreSQL y vuelve a ejecutar."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$initSqlPath = Join-Path $repoRoot "infra\postgres\init.sql"

if (-not (Test-Path $initSqlPath)) {
    throw "No se encontro el archivo de inicializacion: $initSqlPath"
}

Write-Host "Creando base de datos si no existe: $DbName"
$createDbQuery = "SELECT 'CREATE DATABASE $DbName' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DbName')\gexec"
psql -U $PgUser -h $PgHost -p $PgPort -d postgres -v ON_ERROR_STOP=1 -c $createDbQuery

Write-Host "Aplicando esquema inicial..."
psql -U $PgUser -h $PgHost -p $PgPort -d $DbName -v ON_ERROR_STOP=1 -f $initSqlPath

Write-Host "Bootstrap PostgreSQL completado."