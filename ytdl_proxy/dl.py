import uuid
from data import DownloadRequest
import aiofiles
import asyncio
import os
from yt_dlp import YoutubeDL

class AsyncDownloadManager:
    def __init__(self, req: DownloadRequest = None, path: str = None):
        if (req and path) or (not req and not path):
            raise ValueError("specify req or path")
        self._req = req
        self._path = path

    async def __aenter__(self):
        if self._path is None:
            self._path = await download(self._req, rand_fid())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await delete(self._path)

    async def data(self) -> bytes:
        async with aiofiles.open(self._path, "rb") as f:
            return await f.read()

def rand_fid() -> str:
    return str(uuid.uuid4())

async def download(req: DownloadRequest, fid: str) -> str:
    return await asyncio.to_thread(_download_sync, req, fid)

async def delete(path: str) -> None:
    await asyncio.to_thread(os.remove, path)
    
def _download_sync(req: DownloadRequest, fid: str) -> str:
    if req.format == "mp3":
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': f"out/{fid}",
            'noplaylist': True
        }
        if req.postprocessor_args is not None and len(req.postprocessor_args) > 0:
            opts["postprocessor_args"] = req.postprocessor_args
    elif req.format == "mp4":
        opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f"out/{fid}",
            'noplaylist': True
        }
        
        if req.postprocessor_args:
            raise ValueError("postprocessor doesn't run on videos, emit postprocessor_args")
    else:
        raise ValueError("unsupported format")
    
    with YoutubeDL(opts) as ydl:
        ydl.download([req.video])
    
    return f"out/{fid}.{req.format}"