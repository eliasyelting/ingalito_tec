import psycopg2


class SupabasePipeline:

  def __init__(self, db_url):
    self.db_url = db_url
    self.conn = None
    self.cursor = None

  @classmethod
  def from_crawler(cls, crawler):
    # Toma la URL de base de datos desde settings.py
    return cls(db_url=crawler.settings.get('DATABASE_URL'))

  def open_spider(self, spider):
    # Nos conectamos a Supabase al iniciar el spider
    self.conn = psycopg2.connect(self.db_url)
    self.cursor = self.conn.cursor()

  def close_spider(self, spider):
    # Cerramos la conexión al terminar
    if self.cursor:
      self.cursor.close()
    if self.conn:
      self.conn.close()

  def process_item(self, item, spider):
    # Inserción o actualización basada en la URL (UPSERT)
    query = """
        INSERT INTO products (title, price, url, image_url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (url) DO UPDATE SET
            title = EXCLUDED.title,
            price = EXCLUDED.price,
            image_url = EXCLUDED.image_url,
            created_at = NOW();
        """
    self.cursor.execute(
        query,
        (
            item.get('title'),
            item.get('price'),
            item.get('url'),
            item.get('image_url'),
        ),
    )
    self.conn.commit()
    return item