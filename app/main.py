from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.config import get_settings
from app.api import urls_router, redirect_router, analytics_router
from app.core.cache import cache
from app.core.exceptions import setup_exception_handlers
from app.core.logging import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await cache.connect()
    yield
    await cache.disconnect()
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urls_router, prefix=settings.API_V1_PREFIX)
app.include_router(redirect_router)
app.include_router(analytics_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>URL Shortener Dashboard</title>
      <style>
        body { font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f4f6fb; color: #111827; }
        .page { max-width: 1100px; margin: 0 auto; padding: 28px 20px 40px; }
        .panel { background: #ffffff; border-radius: 20px; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08); padding: 30px; margin-bottom: 24px; }
        .hero { display: grid; gap: 24px; grid-template-columns: 1.4fr 1fr; align-items: start; }
        h1 { margin: 0 0 8px; font-size: 2.3rem; }
        p.lead { margin: 0; color: #4b5563; max-width: 680px; }
        .field { display: grid; gap: 8px; margin-top: 18px; }
        .field label { font-weight: 600; color: #374151; }
        .field input { width: 100%; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 16px; font-size: 1rem; }
        .buttons { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 18px; }
        .button-primary, .button-secondary { border: none; border-radius: 12px; padding: 14px 18px; font-weight: 700; cursor: pointer; }
        .button-primary { background: #2563eb; color: white; }
        .button-secondary { background: #e5e7eb; color: #111827; }
        .button-primary:hover { background: #1d4ed8; }
        .button-secondary:hover { background: #d1d5db; }
        .message { display: none; margin-top: 18px; padding: 18px; border-radius: 14px; }
        .message.success { background: #eff6ff; color: #1d4ed8; }
        .message.error { background: #fee2e2; color: #991b1b; }
        .grid-two { display: grid; gap: 20px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .card { background: #f8fafc; border-radius: 18px; padding: 22px; }
        .card h2 { margin-top: 0; font-size: 1.05rem; color: #1f2937; }
        .card p { margin: 0.8rem 0 0; color: #4b5563; }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 14px; }
        th, td { padding: 14px 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        th { font-weight: 700; color: #111827; }
        a { color: #2563eb; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .search-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 18px; margin-top: 14px; }
        .stats-grid { display: grid; gap: 16px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 18px; }
        .stat { background: #ffffff; border-radius: 16px; padding: 18px; }
        .stat strong { display: block; font-size: 1.45rem; margin-bottom: 6px; }
        .hidden { display: none !important; }
      </style>
    </head>
    <body>
      <div class="page">
        <div class="panel hero">
          <div>
            <h1>URL Shortener Dashboard</h1>
            <p class="lead">Create, manage, and monitor shortened links from a single app-style dashboard. Use custom codes, review top shortened URLs, and search your link history.</p>
            <div class="field">
              <label for="original_url">Original URL</label>
              <input id="original_url" placeholder="https://example.com" />
            </div>
            <div class="field">
              <label for="custom_code">Custom short code (optional)</label>
              <input id="custom_code" placeholder="custom-code" />
            </div>
            <div class="buttons">
              <button id="shorten" class="button-primary">Create Short URL</button>
              <button id="reset" class="button-secondary" type="button">Clear</button>
            </div>
            <div id="feedback" class="message success"></div>
            <div id="error" class="message error"></div>
          </div>
          <div class="card">
            <h2>Search URLs</h2>
            <div class="field">
              <label for="search_query">Search by original link or short code</label>
              <input id="search_query" placeholder="Search term" />
            </div>
            <button id="search_button" class="button-primary">Search</button>
            <div id="search_error" class="message error" style="display:none"></div>
            <div id="search_results"></div>
          </div>
        </div>

        <div class="panel hidden" id="result_section">
          <h2>Last Created Short URL</h2>
          <div class="grid-two">
            <div class="card">
              <p><strong id="result_short_url"></strong></p>
              <p id="result_original_url"></p>
              <div class="buttons">
                <button id="copy_button" class="button-primary" type="button">Copy Link</button>
                <button id="open_button" class="button-secondary" type="button">Open Link</button>
              </div>
            </div>
            <div class="card">
              <p><strong>Clicks</strong> <span id="result_clicks"></span></p>
              <p><strong>Created</strong> <span id="result_created"></span></p>
              <p><strong>Updated</strong> <span id="result_updated"></span></p>
              <img id="qr_image" src="" alt="QR code" style="margin-top:16px; width:180px; height:180px; border-radius:16px;" />
            </div>
          </div>
        </div>

        <div class="panel grid-two">
          <div class="card">
            <h2>Recent URLs</h2>
            <div class="table-container">
              <table>
                <thead>
                  <tr><th>Original URL</th><th>Short URL</th><th>Clicks</th></tr>
                </thead>
                <tbody id="recent_body"></tbody>
              </table>
            </div>
          </div>
          <div class="card">
            <h2>Top URLs</h2>
            <div class="table-container">
              <table>
                <thead>
                  <tr><th>Code</th><th>Original URL</th><th>Clicks</th></tr>
                </thead>
                <tbody id="top_body"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <script>
        const shortenButton = document.getElementById('shorten');
        const resetButton = document.getElementById('reset');
        const originalUrlInput = document.getElementById('original_url');
        const customCodeInput = document.getElementById('custom_code');
        const feedback = document.getElementById('feedback');
        const errorBox = document.getElementById('error');
        const resultSection = document.getElementById('result_section');
        const resultShortUrl = document.getElementById('result_short_url');
        const resultOriginalUrl = document.getElementById('result_original_url');
        const resultClicks = document.getElementById('result_clicks');
        const resultCreated = document.getElementById('result_created');
        const resultUpdated = document.getElementById('result_updated');
        const qrImage = document.getElementById('qr_image');
        const copyButton = document.getElementById('copy_button');
        const openButton = document.getElementById('open_button');
        const searchQuery = document.getElementById('search_query');
        const searchButton = document.getElementById('search_button');
        const searchError = document.getElementById('search_error');
        const searchResults = document.getElementById('search_results');
        const recentBody = document.getElementById('recent_body');
        const topBody = document.getElementById('top_body');

        const resetForm = () => {
          originalUrlInput.value = '';
          customCodeInput.value = '';
          feedback.style.display = 'none';
          errorBox.style.display = 'none';
        };

        resetButton.addEventListener('click', resetForm);

        shortenButton.addEventListener('click', async () => {
          feedback.style.display = 'none';
          errorBox.style.display = 'none';

          const originalUrl = originalUrlInput.value.trim();
          const customCode = customCodeInput.value.trim();
          if (!originalUrl) {
            errorBox.textContent = 'Original URL is required.';
            errorBox.style.display = 'block';
            return;
          }

          const body = { original_url: originalUrl };
          if (customCode) body.custom_code = customCode;

          try {
            const response = await fetch('/api/v1/urls/', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(body),
            });
            const data = await response.json();

            if (!response.ok) {
              throw new Error(data.detail || data.message || JSON.stringify(data));
            }

            const shortUrl = data.short_url;
            feedback.innerHTML = `Short URL created: <a href="${shortUrl}" target="_blank">${shortUrl}</a>`;
            feedback.style.display = 'block';
            resultShortUrl.textContent = shortUrl;
            resultOriginalUrl.textContent = data.original_url;
            resultClicks.textContent = data.clicks;
            resultCreated.textContent = new Date(data.created_at).toLocaleString();
            resultUpdated.textContent = new Date(data.updated_at).toLocaleString();
            resultSection.style.display = 'block';
            qrImage.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(shortUrl)}`;
            loadRecentUrls();
            loadTopUrls();
          } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            errorBox.textContent = message;
            errorBox.style.display = 'block';
            console.error('Shorten error:', err);
          }
        });

        async function loadRecentUrls() {
          const response = await fetch('/api/v1/urls/?limit=5');
          const data = await response.json();
          recentBody.innerHTML = '';
          for (const item of data.urls) {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${item.original_url}</td>
              <td><a href="${item.short_url}" target="_blank">${item.short_url}</a></td>
              <td>${item.clicks}</td>
            `;
            recentBody.appendChild(row);
          }
        }

        async function loadTopUrls() {
          const response = await fetch('/api/v1/analytics/top/urls?limit=5');
          const data = await response.json();
          topBody.innerHTML = '';
          for (const item of data) {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td><a href="${item.short_url ?? `${window.location.origin}/${item.short_code}`}" target="_blank">${item.short_code}</a></td>
              <td>${item.original_url}</td>
              <td>${item.click_count}</td>
            `;
            topBody.appendChild(row);
          }
        }

        async function doSearch() {
          const query = searchQuery.value.trim();
          if (!query) {
            searchError.textContent = 'Please enter a search term.';
            searchError.style.display = 'block';
            return;
          }
          searchError.style.display = 'none';
          const response = await fetch(`/api/v1/urls/search?q=${encodeURIComponent(query)}`);
          const data = await response.json();
          searchResults.innerHTML = '';
          if (!Array.isArray(data) || !data.length) {
            searchResults.innerHTML = '<p>No results found.</p>';
            return;
          }
          for (const item of data) {
            const card = document.createElement('div');
            card.className = 'search-card';
            card.innerHTML = `
              <div><strong>${item.short_code}</strong> - <a href="${item.short_url}" target="_blank">${item.short_url}</a></div>
              <div>Original: ${item.original_url}</div>
              <div>Clicks: ${item.clicks}</div>
              <div>Created: ${new Date(item.created_at).toLocaleString()}</div>
            `;
            searchResults.appendChild(card);
          }
        }

        copyButton.addEventListener('click', () => {
          const text = resultShortUrl.textContent;
          if (text) {
            navigator.clipboard.writeText(text);
          }
        });

        openButton.addEventListener('click', () => {
          const text = resultShortUrl.textContent;
          if (text) {
            window.open(text, '_blank');
          }
        });

        searchButton.addEventListener('click', doSearch);
        window.addEventListener('load', () => {
          loadRecentUrls();
          loadTopUrls();
        });
      </script>
    </body>
    </html>
    """
