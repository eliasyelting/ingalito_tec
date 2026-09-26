from http.server import BaseHTTPRequestHandler
import json
import os
import psycopg2

class handler(BaseHTTPRequestHandler):
    """
    Función Serverless para Vercel.
    Conecta con Supabase (PostgreSQL) usando SSL y devuelve la lista de productos en formato JSON.
    """

    def do_GET(self):
        conn = None
        cursor = None
        try:
            db_url = os.environ.get('DATABASE_URL')

            if not db_url:
                raise ValueError("La variable de entorno DATABASE_URL no está configurada en Vercel.")

            # Asegurar parámetros SSL requeridos por Supabase
            if 'sslmode=' not in db_url:
                if '?' in db_url:
                    db_url += '&sslmode=require'
                else:
                    db_url += '?sslmode=require'

            conn = psycopg2.connect(db_url, connect_timeout=10)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT title, price, in_stock 
                FROM products 
                ORDER BY id DESC;
            """)
            rows = cursor.fetchall()

            products = []
            for row in rows:
                products.append({
                    "title": str(row[0]) if row[0] is not None else "Producto sin nombre",
                    "price": float(row[1]) if row[1] is not None else 0.0,
                    "in_stock": bool(row[2]) if row[2] is not None else False
                })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 's-maxage=60, stale-while-revalidate=300')
            self.end_headers()
            self.wfile.write(json.dumps(products, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                "error": "Error de conexión o consulta a Supabase",
                "details": str(e)
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass