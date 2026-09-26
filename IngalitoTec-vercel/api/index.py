import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend

DATABASE_URL = os.environ.get('DATABASE_URL')


def get_db_connection():
  return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@app.route('/api/products', methods=['GET'])
def get_products():
  search_query = request.args.get('search', '')

  try:
    conn = get_db_connection()
    cur = conn.cursor()

    if search_query:
      cur.execute(
          'SELECT * FROM products WHERE title ILIKE %s ORDER BY created_at'
          ' DESC LIMIT 50;',
          (f'%{search_query}%',),
      )
    else:
      cur.execute(
          'SELECT * FROM products ORDER BY created_at DESC LIMIT 50;'
      )

    products = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(products)
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Para desarrollo local
if __name__ == '__main__':
  app.run(debug=True)