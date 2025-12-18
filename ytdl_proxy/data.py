"""Data structures for ytdl-proxy API."""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class DownloadRequest(BaseModel):
    """Request body for POST / and POST /async endpoints."""
    video: str = Field(..., description="Link to the video")
    format: str = Field(..., description="Resulting file format (mp4, mp3, etc)")


class AsyncDownloadResponse(BaseModel):
    """Response body for POST /async endpoint."""
    id: str = Field(..., description="ID to check on results")


class AsyncStatusResponse(BaseModel):
    """Response body for GET /async endpoint."""
    status: Literal["PENDING", "DONE", "FAILED"] = Field(..., description="Status of the async download")
    error: Optional[str] = Field(None, description="Error message if status is FAILED")


class AsyncContentRequest(BaseModel):
    """Request body for POST /async/content endpoint."""
    id: str = Field(..., description="ID to download")


class ErrorResponse(BaseModel):
    """Error response body for 4xx/5xx status codes."""
    error: str = Field(..., description="What went wrong")
