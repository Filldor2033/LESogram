from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from core.config import STATIC_DIR
from core.lifespan import lifespan
from core.security_headers import add_security_headers

from api.auth_routes import router as auth_router
from api.room_routes import router as room_router
from api.message_routes import router as message_router
from api.attachment_routes import router as attachment_router
from ws.routes import router as websocket_router


app = FastAPI(title="Realtime Chat", lifespan=lifespan)

app.middleware("http")(add_security_headers)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router)
app.include_router(room_router)
app.include_router(message_router)
app.include_router(attachment_router)
app.include_router(websocket_router)


@app.get("/")
async def get_index():
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
