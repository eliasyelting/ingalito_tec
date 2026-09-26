from http.server import BaseHTTPRequestHandler
import psycopg2
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
            cur = conn.cursor()
            
            # Solo consulta productos activos (is_active = TRUE)
            cur.execute("SELECT title, price_final, in_stock FROM products WHERE is_active = TRUE ORDER BY title ASC;")
            rows = cur.fetchall()
            
            products = [
                {
                    "title": row[0],
                    "price": row[1],
                    "in_stock": row[2]
                }
                for row in rows
            ]
            
            cur.close()
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(products).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))