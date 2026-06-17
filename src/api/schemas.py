"""API schemas for video generation service."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """Request schema for video generation."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text description of the video to generate",
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Text to discourage in generation",
    )
    num_inference_steps: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Number of denoising steps",
    )
    guidance_scale: Optional[float] = Field(
        default=None,
        ge=1.0,
        le=20.0,
        description="Classifier-free guidance scale",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility",
    )
    num_frames: Optional[int] = Field(
        default=None,
        ge=8,
        le=64,
        description="Number of frames to generate",
    )


class GenerationResponse(BaseModel):
    """Response schema for video generation."""

    job_id: str = Field(description="Unique job identifier")
    status: str = Field(description="Job status (pending, processing, completed, failed)")
    video_url: Optional[str] = Field(default=None, description="URL to download the video")
    message: Optional[str] = Field(default=None, description="Status message or error")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class JobStatus(BaseModel):
    """Schema for job status check."""

    job_id: str
    status: str
    progress: Optional[float] = None
    video_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    model_name: str
    device: str
    version: str