"""Job management for async video generation."""

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from src.models.video_generator import VideoGenerator
from src.utils.config import get_config


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Video generation job."""

    job_id: str
    prompt: str
    status: JobStatus = JobStatus.PENDING
    negative_prompt: Optional[str] = None
    num_inference_steps: Optional[int] = None
    guidance_scale: Optional[float] = None
    seed: Optional[int] = None
    num_frames: Optional[int] = None
    video_path: Optional[str] = None
    error: Optional[str] = None
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class JobManager:
    """Manages video generation jobs."""

    def __init__(self, max_workers: int = 3):
        """Initialize job manager.

        Args:
            max_workers: Maximum number of concurrent jobs
        """
        self._jobs: dict[str, Job] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = asyncio.Lock()

    def create_job(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        num_frames: Optional[int] = None,
    ) -> Job:
        """Create a new generation job.

        Args:
            prompt: Text prompt for generation
            negative_prompt: Negative prompt
            num_inference_steps: Inference steps
            guidance_scale: Guidance scale
            seed: Random seed
            num_frames: Number of frames

        Returns:
            Created job
        """
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed,
            num_frames=num_frames,
        )
        self._jobs[job_id] = job
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job if found, None otherwise
        """
        return self._jobs.get(job_id)

    async def get_all_jobs(self) -> list[Job]:
        """Get all jobs.

        Returns:
            List of all jobs
        """
        return list(self._jobs.values())

    async def process_job(self, job: Job) -> Job:
        """Process a generation job.

        Args:
            job: Job to process

        Returns:
            Updated job
        """
        job.status = JobStatus.PROCESSING
        config = get_config()

        try:
            generator = VideoGenerator()

            output_path = config.storage.output_dir / f"{job.job_id}.mp4"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            job.progress = 0.1

            video_path = generator.generate_to_video(
                prompt=job.prompt,
                output_path=str(output_path),
                negative_prompt=job.negative_prompt,
                num_inference_steps=job.num_inference_steps,
                guidance_scale=job.guidance_scale,
                seed=job.seed,
            )

            job.progress = 1.0
            job.status = JobStatus.COMPLETED
            job.video_path = video_path
            job.completed_at = datetime.utcnow()

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()

        return job

    def submit_job(self, job: Job) -> asyncio.Task:
        """Submit job for async processing.

        Args:
            job: Job to submit

        Returns:
            Asyncio task
        """
        async def run_job():
            await self.process_job(job)

        return asyncio.create_task(run_job())

    async def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Clean up old completed jobs.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of jobs cleaned up
        """
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        to_remove = []

        for job_id, job in self._jobs.items():
            if job.completed_at and job.completed_at < cutoff:
                if job.video_path:
                    try:
                        Path(job.video_path).unlink(missing_ok=True)
                    except OSError:
                        pass
                to_remove.append(job_id)

        for job_id in to_remove:
            del self._jobs[job_id]

        return len(to_remove)

    def shutdown(self) -> None:
        """Shutdown the job manager."""
        self._executor.shutdown(wait=True)


job_manager = JobManager()