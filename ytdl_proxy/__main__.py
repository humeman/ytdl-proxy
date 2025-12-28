"""Main entry point for ytdl-proxy API server."""

from quart import Quart, jsonify, request
from .data import *
from .dl import AsyncDownloadManager, download, rand_fid, delete
import traceback
import asyncio
import time
import threading

app = Quart(__name__)

async_downloads_lock = threading.Lock()
async_downloads = {}

@app.before_serving
async def start_background_task():
    async def background_task():
        while True:
            t = time.time()
            
            to_delete = []
            with async_downloads_lock:
                for fid, dl in async_downloads.items():
                    if dl["time"] < t - 1800:
                        if dl["path"]:
                            await delete(dl["path"])
                        to_delete.append(fid)
                
                for fid in to_delete:
                    del async_downloads[fid]
            
            await asyncio.sleep(60)

    asyncio.create_task(background_task())

@app.route("/", methods=["POST"])
async def post():
    data = await request.get_json()
    try:
        req = DownloadRequest(**data)
        async with AsyncDownloadManager(req = req) as dl:
            return await dl.data(), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(ErrorResponse(error = str(e)).model_dump()), 501

async def dl_async(req: DownloadRequest, fid: str) -> None:
    with async_downloads_lock:
        async_downloads[fid] = {
            "error": None,
            "path": None,
            "time": time.time()
        }
    try:
        path = await download(req, fid)
        with async_downloads_lock:
            async_downloads[fid]["path"] = path
    except Exception as e:
        with async_downloads_lock:
            async_downloads[fid]["error"] = str(e)

@app.route("/async", methods=["POST"])
async def post_async():
    data = await request.get_json()
    req = DownloadRequest(**data)
    fid = rand_fid()
    asyncio.create_task(dl_async(req, fid))
    return jsonify(AsyncDownloadResponse(id=fid).model_dump()), 200

@app.route("/async", methods=["GET"])
async def get_async():
    download_id = request.args.get("id")
    if not download_id:
        return jsonify({"error": "Missing id parameter"}), 400
    with async_downloads_lock:
        status = async_downloads.get(download_id)
    if status is None:
        return jsonify(ErrorResponse(error = "no such download").model_dump()), 400
    return jsonify(AsyncStatusResponse(
        status = "DONE" if status["path"] is not None else ("FAILED" if status["error"] is not None else "PENDING"),
        error = status["error"]
    ).model_dump()), 200

@app.route("/async/content", methods=["POST"])
async def post_async_content():
    data = await request.get_json()
    req = AsyncContentRequest(**data)
    with async_downloads_lock:
        status = async_downloads.get(req.id)
    if status is None:
        return jsonify(ErrorResponse(error = "no such download").model_dump()), 400
    if not status["path"]:
        return jsonify(ErrorResponse(error = "download isn't finished").model_dump()), 400
    with async_downloads_lock:
        del async_downloads[req.id]
    async with AsyncDownloadManager(path = status["path"]) as dl:
        return await dl.data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
