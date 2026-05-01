from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"

MAX_MESSAGE_LENGTH = 1000
MAX_UPLOAD_SIZE = 20 * 1024 * 1024

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/gif",
}

ALLOWED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "video/x-msvideo",
    "video/mpeg",
    "video/ogg",
}

ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".csv",
    ".json",
    ".zip",
    ".7z",
    ".rar",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".odt",
    ".ods",
    ".odp",
}

DANGEROUS_FILE_EXTENSIONS = {
    ".apk",
    ".app",
    ".bat",
    ".cmd",
    ".com",
    ".dll",
    ".exe",
    ".hta",
    ".html",
    ".htm",
    ".iso",
    ".jar",
    ".js",
    ".jse",
    ".mjs",
    ".msi",
    ".php",
    ".ps1",
    ".py",
    ".scr",
    ".sh",
    ".svg",
    ".vbs",
    ".xhtml",
}

DANGEROUS_MIME_TYPES = {
    "application/javascript",
    "application/x-msdownload",
    "text/html",
    "text/javascript",
    "image/svg+xml",
}

ALLOWED_REACTIONS = {"👍", "❤️", "😂", "😮", "😢", "🔥"}
