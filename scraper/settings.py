BOT_NAME = "ingalito_catalog"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 0.2
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False

ITEM_PIPELINES = {
    "scraper.pipelines.KoiProductPipeline": 300,
}

FEED_EXPORT_ENCODING = "utf-8"

# The current KOI HTML is server-rendered, so Playwright is not used on the
# normal path. The spider opts into this handler only after a zero-item page.
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30_000
USE_PLAYWRIGHT_FALLBACK = True