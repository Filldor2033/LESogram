from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from api.attachment_routes import router as attachment_router
from api.profile_routes import router as profile_router
from api.auth_routes import router as auth_router
from api.message_routes import router as message_router
from api.room_routes import router as room_router
from core.config import STATIC_DIR, WEB_DIR
from core.lifespan import lifespan
from core.security_headers import add_security_headers
from ws.routes import router as websocket_router

app = FastAPI(title="Realtime Chat", lifespan=lifespan)

# First-party native app (Capacitor WebView) origins — the Android app
# talks to the API cross-origin by design.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost",
        "http://localhost",
        "capacitor://localhost",
        "ionic://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(add_security_headers)

# Old (legacy) frontend assets stay at /static.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# New Svelte frontend calls REST under /api/*; media_url values returned by
# the API point at /attachments/* (no prefix), so both spellings must work.
app.include_router(auth_router, prefix="/api")
app.include_router(room_router, prefix="/api")
app.include_router(message_router, prefix="/api")
app.include_router(attachment_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

app.include_router(auth_router)
app.include_router(room_router)
app.include_router(message_router)
app.include_router(attachment_router)
app.include_router(profile_router)
app.include_router(websocket_router)

# New Svelte frontend build (frontend/dist): assets under /assets, root serves
# the SPA, the legacy UI remains reachable at /legacy.
WEB_BUILT = (WEB_DIR / "index.html").is_file()

if WEB_DIR.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(WEB_DIR / "assets")),
        name="web-assets",
    )

    @app.get("/favicon.svg", include_in_schema=False)
    async def favicon():
        path = WEB_DIR / "favicon.svg"
        if path.is_file():
            return FileResponse(path, media_type="image/svg+xml")
        return HTMLResponse("not found", status_code=404)


    @app.get("/favicon-{size}.png", include_in_schema=False)
    async def favicon_png(size: int):
        path = WEB_DIR / f"favicon-{size}.png"
        if path.is_file():
            return FileResponse(path, media_type="image/png")
        return HTMLResponse("not found", status_code=404)


    @app.get("/apple-touch-icon.png", include_in_schema=False)
    async def apple_touch_icon():
        path = WEB_DIR / "apple-touch-icon.png"
        if path.is_file():
            return FileResponse(path, media_type="image/png")
        return HTMLResponse("not found", status_code=404)


    @app.get("/og-image.png", include_in_schema=False)
    async def og_image():
        path = WEB_DIR / "og-image.png"
        if path.is_file():
            return FileResponse(path, media_type="image/png")
        return HTMLResponse("not found", status_code=404)

    @app.get("/icons.svg", include_in_schema=False)
    async def icons():
        path = WEB_DIR / "icons.svg"
        if path.is_file():
            return FileResponse(path, media_type="image/svg+xml")
        return HTMLResponse("not found", status_code=404)


@app.get("/legacy", include_in_schema=False)
async def get_legacy_index():
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/")
async def get_index():
    if WEB_BUILT:
        return HTMLResponse((WEB_DIR / "index.html").read_text(encoding="utf-8"))
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
