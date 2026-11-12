"""Verificación de un comando: la URI del Transaction pooler de Supabase conecta y ve el inventario de 021.

Uso, en tu máquina (no en la caja, que bloquea el protocolo Postgres):
    export SUPABASE_DB_PASSWORD='...'   # o define DATABASE_URL completa
    uv run --with "psycopg[binary]" python check_db.py
Sale 0 si conecta y el stock coincide con la semilla. Nunca imprime la contraseña.
"""
import os, sys, urllib.parse
import psycopg

EXPECTED = {"NXV-IT-001": 12, "NXV-IT-002": 6, "NXV-PER-001": 20, "NXV-PER-002": 0, "NXV-OFF-001": 18, "NXV-TRN-001": 15}
url = os.environ.get("DATABASE_URL", "").strip()
if not url:
    pw = os.environ.get("SUPABASE_DB_PASSWORD", "")
    if not pw:
        sys.exit("Falta SUPABASE_DB_PASSWORD o DATABASE_URL.")
    url = ("postgresql://postgres.atraotgdztnrqystnujh:" + urllib.parse.quote(pw, safe="")
           + "@aws-0-us-east-2.pooler.supabase.com:6543/postgres?sslmode=require")
url = url.replace("postgresql+psycopg2://", "postgresql://").replace("pgbouncer=true", "").rstrip("?&")
host = urllib.parse.urlsplit(url).hostname
port = urllib.parse.urlsplit(url).port
try:
    with psycopg.connect(url, connect_timeout=15, prepare_threshold=None) as c:
        print("conectado a", host, port, "como", c.execute("select current_user").fetchone()[0],
              "| postgres", c.execute("show server_version").fetchone()[0])
        rows = c.execute(
            "select a.sku, coalesce((select sum(quantity) from assetentry e where e.asset_id=a.id),0)"
            " - coalesce((select sum(quantity) from assetexit x where x.asset_id=a.id),0) from asset a order by a.sku"
        ).fetchall()
except Exception as exc:
    msg = str(exc)
    pw = os.environ.get("SUPABASE_DB_PASSWORD", "")
    if pw:
        msg = msg.replace(pw, "***")
    sys.exit(f"FALLO {type(exc).__name__}: {msg[:300]}")
got = {sku: int(n) for sku, n in rows}
print("stock:", got)
ok = got == EXPECTED and port == 6543 and host.endswith("pooler.supabase.com")
print("RESULTADO:", "PASS" if ok else "NO COINCIDE")
sys.exit(0 if ok else 1)
