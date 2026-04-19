#!/usr/bin/env python3
"""WAN video keeper web — browse, star, download ComfyUI output videos."""
import json
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from flask import Flask, jsonify, request, send_file, send_from_directory

OUTPUT_ROOT = Path(os.environ.get("OUTPUT_ROOT", "/workspace/ComfyUI/output"))
DATA_DIR    = Path(os.environ.get("DATA_DIR", "/workspace/comfyui2/data"))
COMFY_URL   = os.environ.get("COMFY_URL", "http://localhost:8188")
PORT        = int(os.environ.get("PORT", "8189"))

DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "thumbs").mkdir(exist_ok=True)

app = Flask(__name__, static_folder="static")


def _safe_key(folder_key: str) -> str:
    return folder_key.replace("/", "__").replace("\\", "__") or "__root__"


def marks_file(folder_key: str) -> Path:
    return DATA_DIR / f"{_safe_key(folder_key)}.json"


def load_marks(folder_key: str) -> dict:
    f = marks_file(folder_key)
    return json.loads(f.read_text()) if f.exists() else {}


def save_marks(folder_key: str, marks: dict) -> None:
    marks_file(folder_key).write_text(json.dumps(marks, indent=2, sort_keys=True))


def get_folder_key(path: Path) -> str:
    rel = path.parent.relative_to(OUTPUT_ROOT)
    return str(rel) if str(rel) != "." else ""


def scan_videos() -> list[Path]:
    if not OUTPUT_ROOT.exists():
        return []
    files = [f for f in OUTPUT_ROOT.rglob("*.mp4") if f.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/animate")
def animate_page():
    return send_from_directory("static", "animate.html")


@app.get("/api/folders")
def folders():
    seen: dict[str, int] = {}
    for f in scan_videos():
        fk = get_folder_key(f)
        seen[fk] = seen.get(fk, 0) + 1
    total = sum(seen.values())
    result = [{"folder": "", "label": "All Videos", "count": total}]
    result += [{"folder": k, "label": k, "count": v} for k, v in sorted(seen.items())]
    return jsonify(result)


@app.get("/api/videos")
def videos():
    folder = request.args.get("folder")
    sort = request.args.get("sort", "newest")
    keepers_only = request.args.get("filter") == "keepers"

    files = scan_videos()

    if folder:
        target = OUTPUT_ROOT / folder
        files = [f for f in files if f == target or str(f).startswith(str(target) + "/") or f.parent == target]

    if sort == "oldest":
        files.sort(key=lambda p: p.stat().st_mtime)
    elif sort == "name":
        files.sort(key=lambda p: p.name)

    marks_cache: dict[str, dict] = {}
    out = []
    for f in files:
        fk = get_folder_key(f)
        if fk not in marks_cache:
            marks_cache[fk] = load_marks(fk)
        mark = marks_cache[fk].get(f.stem, {})
        if keepers_only and not mark.get("keep"):
            continue
        st = f.stat()
        out.append({
            "path": str(f.relative_to(OUTPUT_ROOT)),
            "name": f.stem,
            "filename": f.name,
            "folder": fk,
            "mtime": st.st_mtime,
            "size": st.st_size,
            "keep": mark.get("keep", False),
            "stars": mark.get("stars", 0),
            "note": mark.get("note", ""),
        })
    return jsonify(out)


@app.get("/video/<path:filepath>")
def serve_video(filepath: str):
    path = OUTPUT_ROOT / filepath
    if not path.is_file():
        return "not found", 404
    return send_file(path, mimetype="video/mp4", conditional=True)


@app.get("/thumb/<path:filepath>")
def thumbnail(filepath: str):
    path = OUTPUT_ROOT / filepath
    if not path.is_file():
        return "not found", 404
    safe = filepath.replace("/", "__") + ".jpg"
    thumb = DATA_DIR / "thumbs" / safe
    if not thumb.exists():
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(path), "-vframes", "1", "-q:v", "3", str(thumb)],
                capture_output=True, timeout=30,
            )
        except Exception:
            pass
    if not thumb.exists():
        return "no thumbnail", 404
    return send_file(thumb, mimetype="image/jpeg")


@app.get("/download/<path:filepath>")
def download_video(filepath: str):
    path = OUTPUT_ROOT / filepath
    if not path.is_file():
        return "not found", 404
    return send_file(path, as_attachment=True, download_name=path.name)


@app.post("/api/mark/<path:filepath>")
def mark(filepath: str):
    p = Path(filepath)
    fk = str(p.parent) if str(p.parent) != "." else ""
    body = request.get_json(force=True) or {}
    marks = load_marks(fk)
    entry = marks.get(p.stem, {})
    for k in ("keep", "stars", "note"):
        if k in body:
            entry[k] = body[k]
    entry = {k: v for k, v in entry.items() if v not in (False, None, "", 0)}
    if entry:
        marks[p.stem] = entry
    else:
        marks.pop(p.stem, None)
    save_marks(fk, marks)
    return jsonify({"ok": True, "entry": entry})


# ── Animate endpoints ────────────────────────────────────────────────────────

def _comfy_post(path: str, data: dict) -> dict:
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{COMFY_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _comfy_get(path: str) -> dict:
    with urllib.request.urlopen(f"{COMFY_URL}{path}", timeout=10) as r:
        return json.loads(r.read())


def _upload_image_to_comfy(image_path: Path) -> str:
    """Upload image to ComfyUI input folder, return the filename."""
    import urllib.parse
    import mimetypes

    suffix = image_path.suffix.lower()
    mt = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(suffix, "application/octet-stream")

    # multipart/form-data upload
    boundary = "----WanKeeperBoundary"
    body_parts = []
    body_parts.append(f"--{boundary}".encode())
    body_parts.append(f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"'.encode())
    body_parts.append(f"Content-Type: {mt}".encode())
    body_parts.append(b"")
    body_parts.append(image_path.read_bytes())
    body_parts.append(f"--{boundary}--".encode())
    body = b"\r\n".join(body_parts)

    req = urllib.request.Request(
        f"{COMFY_URL}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
    return result["name"]


@app.post("/api/animate")
def animate():
    """
    Body: { "prompt": "...", "width": 640, "height": 640,
            "length": 81, "fps": 24, "fast_mode": true,
            "use_ai_planner": true }
    Plus either:
      - multipart file upload (field "image")
      - or JSON field "image_path" (relative to OUTPUT_ROOT)
    """
    from wan_workflow import build_wan_i2v_workflow

    # ── get image ────────────────────────────────────────────
    image_file = request.files.get("image")
    if image_file:
        suffix = Path(image_file.filename).suffix or ".jpg"
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        image_file.save(tmp.name)
        tmp_path = Path(tmp.name)
    else:
        body = request.get_json(force=True) or {}
        rel = body.get("image_path", "")
        if not rel:
            return jsonify({"error": "no image provided"}), 400
        tmp_path = OUTPUT_ROOT / rel
        if not tmp_path.is_file():
            return jsonify({"error": "image not found"}), 404

    if image_file:
        body = request.form.to_dict()
        # content_loras sent as JSON string from the form; always present (may be [])
        raw_loras = body.pop("content_loras_json", None)
        body["content_loras"] = json.loads(raw_loras) if raw_loras is not None else None
    else:
        body = request.get_json(force=True) or {}

    user_prompt = body.get("prompt", "")
    use_planner = str(body.get("use_ai_planner", "true")).lower() != "false"

    # ── plan workflow params ──────────────────────────────────
    if use_planner and user_prompt and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            from planner import plan_workflow
            params = plan_workflow(tmp_path, user_prompt)
        except Exception as e:
            params = {}
    else:
        params = {}

    positive_prompt = params.get("positive_prompt") or user_prompt or "cinematic motion, smooth movement"
    negative_prompt = params.get("negative_prompt") or None
    width   = int(body.get("width",  params.get("width",  640)))
    height  = int(body.get("height", params.get("height", 640)))
    length  = int(body.get("length", params.get("length", 81)))
    fps     = int(body.get("fps",    params.get("fps",    24)))
    fast    = str(body.get("fast_mode", params.get("fast_mode", True))).lower() != "false"
    # User's explicit selection wins; None means not provided → fall back to AI suggestions
    user_loras = body.get("content_loras")
    content_loras = user_loras if user_loras is not None else params.get("content_loras", [])

    # ── upload image to ComfyUI ───────────────────────────────
    try:
        comfy_filename = _upload_image_to_comfy(tmp_path)
    except Exception as e:
        return jsonify({"error": f"image upload failed: {e}"}), 500
    finally:
        if image_file and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    # ── build and submit workflow ─────────────────────────────
    kw = dict(
        image_filename=comfy_filename,
        positive_prompt=positive_prompt,
        width=width, height=height, length=length, fps=fps,
        fast_mode=fast, content_loras=content_loras,
    )
    if negative_prompt:
        kw["negative_prompt"] = negative_prompt

    workflow = build_wan_i2v_workflow(**kw)

    try:
        result = _comfy_post("/prompt", {"prompt": workflow})
    except Exception as e:
        return jsonify({"error": f"ComfyUI unreachable: {e}"}), 502

    return jsonify({
        "ok": True,
        "prompt_id": result.get("prompt_id"),
        "positive_prompt": positive_prompt,
    })


@app.get("/api/animate/status/<prompt_id>")
def animate_status(prompt_id: str):
    """Poll ComfyUI for job status. Returns {status, videos} when done."""
    try:
        history = _comfy_get(f"/history/{prompt_id}")
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    if prompt_id not in history:
        # check queue
        try:
            queue = _comfy_get("/queue")
            running = [item[1] for item in queue.get("queue_running", [])]
            pending = [item[1] for item in queue.get("queue_pending", [])]
            if prompt_id in running:
                return jsonify({"status": "running"})
            if prompt_id in pending:
                return jsonify({"status": "queued"})
        except Exception:
            pass
        return jsonify({"status": "queued"})

    entry = history[prompt_id]
    status_info = entry.get("status", {})
    if status_info.get("status_str") == "error":
        msgs = [m.get("details", "") for m in status_info.get("messages", []) if m.get("type") == "error"]
        return jsonify({"status": "error", "error": "; ".join(msgs)})

    # collect output video paths
    videos = []
    for node_output in entry.get("outputs", {}).values():
        for vinfo in node_output.get("videos", []):
            fname = vinfo.get("filename", "")
            subfolder = vinfo.get("subfolder", "")
            rel = f"{subfolder}/{fname}".lstrip("/")
            videos.append(rel)

    return jsonify({"status": "done", "videos": videos})


if __name__ == "__main__":
    print(f"[keeperweb] output: {OUTPUT_ROOT}")
    print(f"[keeperweb] data:   {DATA_DIR}")
    print(f"[keeperweb] port:   {PORT}")
    print(f"[keeperweb] comfy:  {COMFY_URL}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
