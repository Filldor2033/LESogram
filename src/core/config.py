from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"

MAX_MESSAGE_LENGTH = 1000
MAX_UPLOAD_SIZE = 20 * 1024 * 1024

MAX_IMAGE_PIXELS = 20_000_000

ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
}

ALLOWED_FILE_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/json",
    "application/zip",
    "application/x-7z-compressed",
    "application/vnd.rar",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
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
    "application/x-msdos-program",
    "application/x-executable",
    "text/html",
    "text/javascript",
    "image/svg+xml",
}

ALLOWED_REACTIONS = {"👍", "❤️", "😂", "😮", "😢", "🔥"}

HEARTBEAT_INTERVAL = 25
HEARTBEAT_TIMEOUT = 75
