from pydantic import BaseModel, Field
from typing import Optional, Literal

class DownloadRequest(BaseModel):
    video: str = Field(..., description = "link to the video")
    format: str = Field(..., description = "resulting file format (mp4, mp3, etc)")
    postprocessor_args: Optional[dict[str, str]] = Field(..., description = "ffmpeg args")

class AsyncDownloadResponse(BaseModel):
    id: str = Field(..., description = "ID to check on results")

class AsyncStatusResponse(BaseModel):
    status: Literal["PENDING", "DONE", "FAILED"] = Field(..., description = "status of the async download")
    error: Optional[str] = Field(None, description = "error message if status is FAILED")

class AsyncContentRequest(BaseModel):
    id: str = Field(..., description = "ID to download")

class ErrorResponse(BaseModel):
    error: str = Field(..., description = "what went wrong")
