BOT_NAME = "ingalitoTEC_scrapy"
SPIDER_MODULES = ["ingalitoTEC_scrapy.spiders"]
NEWSPIDER_MODULE = "ingalitoTEC_scrapy.spiders"

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
   'ingalitoTEC_scrapy.pipelines.DatabasePipeline': 300,
}

# Reemplazá con tu cadena de conexión real de Supabase
DATABASE_URL = 'postgresql://postgres.ghvznwhnsebxduyusmyf:[$vUzWT-Z7WXtydfpostgresql://postgres.ghvznwhnsebxduyusmyf:%24vUzWT-Z7WXtydf@aws-0-sa-east-1.pooler.supabase.com:6543/postgres'

ITEM_PIPELINES = {
    'IngalitoTEC.pipelines.SupabasePipeline': 300,
}