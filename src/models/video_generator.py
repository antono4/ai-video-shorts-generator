"""Video generation model using Hugging Face Transformers."""

import torch
from diffusers import DiffusionPipeline
from PIL import Image
from typing import Optional

from src.utils.config import ModelConfig, GenerationConfig, StorageConfig


class VideoGenerator:
    """AI Video Generator using Hugging Face Diffusers."""

    def __init__(
        self,
        model_config: Optional[ModelConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        storage_config: Optional[StorageConfig] = None,
    ):
        """Initialize the video generator.

        Args:
            model_config: Model configuration settings
            generation_config: Generation parameters
            storage_config: Storage paths configuration
        """
        self.model_config = model_config or ModelConfig()
        self.generation_config = generation_config or GenerationConfig()
        self.storage_config = storage_config or StorageConfig()
        self._pipeline: Optional[DiffusionPipeline] = None

    def _get_torch_dtype(self) -> torch.dtype:
        """Get torch dtype from config string."""
        dtype_map = {
            "float32": torch.float32,
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
        }
        return dtype_map.get(self.model_config.torch_dtype, torch.float16)

    def load_model(self) -> None:
        """Load the diffusion model pipeline."""
        if self._pipeline is not None:
            return

        dtype = self._get_torch_dtype()
        device = self.model_config.device

        self._pipeline = DiffusionPipeline.from_pretrained(
            self.model_config.model_name,
            torch_dtype=dtype,
            safety_checker=None,
            use_safetensors=self.model_config.use_safetensors,
            cache_dir=str(self.storage_config.cache_dir),
        )

        if self.model_config.enable_xformers:
            self._pipeline.enable_xformers_memory_efficient_attention()

        self._pipeline = self._pipeline.to(device)

        if device == "cuda" and torch.cuda.is_available():
            self._pipeline.enable_model_cpu_offload()

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> list[Image.Image]:
        """Generate a video from a text prompt.

        Args:
            prompt: Text description of the video to generate
            negative_prompt: Text to discourage in generation
            num_inference_steps: Number of denoising steps
            guidance_scale: Classifier-free guidance scale
            seed: Random seed for reproducibility

        Returns:
            List of PIL Images representing video frames
        """
        if self._pipeline is None:
            self.load_model()

        if seed is not None:
            generator = torch.Generator(device=self.model_config.device)
            generator.manual_seed(seed)
        else:
            generator = None

        frames = self._pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps or self.generation_config.num_inference_steps,
            guidance_scale=guidance_scale or self.generation_config.guidance_scale,
            num_frames=self.generation_config.num_frames,
            height=self.generation_config.height,
            width=self.generation_config.width,
            generator=generator,
        ).frames[0]

        return frames

    def generate_to_video(
        self,
        prompt: str,
        output_path: str,
        **kwargs,
    ) -> str:
        """Generate a video and save it to file.

        Args:
            prompt: Text description of the video
            output_path: Path to save the output video
            **kwargs: Additional generation parameters

        Returns:
            Path to the saved video file
        """
        from src.utils.video import frames_to_video

        frames = self.generate(prompt, **kwargs)
        video_path = frames_to_video(
            frames=frames,
            output_path=output_path,
            fps=self.generation_config.fps,
        )
        return video_path

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._pipeline is not None

    def unload(self) -> None:
        """Unload model from memory."""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()