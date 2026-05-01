export function setStatus(id, text, isError = false) {
    const el = document.getElementById(id);
    if (!el) return;

    el.textContent = text || "";
    el.className = "status" + (isError ? " error" : "");
}

export function setComposerStatus(text, isError = false) {
    setStatus("composerStatus", text, isError);
}