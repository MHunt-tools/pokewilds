#!/usr/bin/env python3
"""
Sprite Generator for PokeGen
Generates Pokémon sprites from text descriptions using Stable Diffusion
Optimized for CPU-only inference with low memory footprint
"""

import torch
import sys
from pathlib import Path
from typing import Optional
from PIL import Image


class SpriteGenerator:
    """Generate Pokémon sprites from text descriptions using Stable Diffusion"""
    
    def __init__(self, device: str = "cpu", low_memory: bool = True, model_name: str = "justinpinkney/pokemon-stable-diffusion"):
        """
        Initialize sprite generator
        
        Args:
            device: 'cpu' or 'cuda' (default: cpu)
            low_memory: Enable memory optimization for CPU (default: True)
            model_name: HuggingFace model ID (default: Stable Diffusion v1.5)
        """
        self.device = device
        self.low_memory = low_memory
        self.model_name = model_name
        self.pipe = None
    
    def load_model(self):
        """Load Stable Diffusion model (lazy loading)"""
        if self.pipe is not None:
            return
        
        print(f"Loading Stable Diffusion model ({self.model_name})...")
        print("(This may take a few minutes on first run while downloading ~4GB model)")
        
        from diffusers import StableDiffusionPipeline
        
        # Load pipeline
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32
        )
        
        # CPU-specific optimizations
        if self.device == "cpu":
            # Enable attention slicing to reduce memory usage
            self.pipe.enable_attention_slicing()
            
            # Optional: Enable CPU offloading if available
            try:
                self.pipe.enable_sequential_cpu_offload()
            except:
                pass
        else:
            # Move to device (only for non-CPU devices to avoid meta tensor issues)
            self.pipe = self.pipe.to(self.device)
        
        print(f"✓ Model loaded on {self.device}")
    

    def generate_sprite(
        self,
        prompt: str,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        height: int = 96,
        width: int = 96,
        seed: Optional[int] = None
    ) -> Image.Image:
        """
        Generate a sprite from text description
        
        Args:
            prompt: Text description (e.g., "red fire-type dragon")
            num_inference_steps: Number of inference steps (10-50, higher=better quality)
            guidance_scale: Classifier-free guidance scale (7.5 is default)
            height: Image height in pixels (default: 96)
            width: Image width in pixels (default: 96)
            seed: Random seed for reproducibility
        
        Returns:
            PIL Image object
        """
        
        if self.pipe is None:
            self.load_model()
        
        # Set seed for reproducibility
        if seed is not None:
            torch.manual_seed(seed)
        
        print(f"Generating sprite: '{prompt}'")
        
        # Generate with no_grad to save memory
        with torch.no_grad():
            result = self.pipe(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                height=height,
                width=width
            )
        
        image = result.images[0]
        print("✓ Sprite generated successfully")
        
        return image
    
    def generate_and_save(
        self,
        prompt: str,
        output_path: Path,
        num_inference_steps: int = 20,
        **kwargs
    ) -> bool:
        """
        Generate sprite and save to file
        
        Args:
            prompt: Text description
            output_path: Path to save image
            num_inference_steps: Number of inference steps
            **kwargs: Additional arguments for generate_sprite()
        
        Returns:
            True if successful, False otherwise
        """
        
        try:
            # Generate at high resolution (512x512) for better detail
            high_res = self.generate_sprite(
                prompt,
                num_inference_steps=num_inference_steps,
                height=512,
                width=512,
                **kwargs
            )

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save high-resolution image with _512 suffix
            high_res_path = output_path.parent / f"{output_path.stem}_512.png"
            high_res.save(str(high_res_path))

            # Downscale to 96x96 using nearest neighbor to preserve pixel-art look
            downscaled = high_res.resize((96, 96), resample=Image.NEAREST)
            down_res_path = output_path.parent / f"{output_path.stem}_96.png"
            downscaled.save(str(down_res_path))

            print(f"✓ Saved high-res to {high_res_path} and downscaled sprite to {down_res_path}")
            return True
        except Exception as e:
            print(f"✗ Error generating sprite: {e}")
            return False


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Pokémon sprites from text')
    parser.add_argument('name', help='Output name (e.g., MyPokemon)')
    parser.add_argument('prompt', help='Sprite description (e.g., "red fire dragon")')
    parser.add_argument('--steps', type=int, default=20, help='Inference steps (10-50)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--output', type=Path, help='Output directory (default: ./generated_sprites/)')
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu', help='Device to use')
    
    args = parser.parse_args()
    
    # Setup output: allow `--output` to be either a directory or an explicit file path.
    if args.output:
        # If the path already exists on disk, decide by its type
        if args.output.exists():
            if args.output.is_dir():
                output_dir = args.output
                output_path = output_dir / f"{args.name}.png"
            else:
                # Provided a file path: use it directly
                output_path = args.output
                output_dir = output_path.parent
        else:
            # Path doesn't exist yet: infer intent by suffix
            if args.output.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']:
                output_path = args.output
                output_dir = output_path.parent
            else:
                output_dir = args.output
                output_path = output_dir / f"{args.name}.png"
    else:
        output_dir = Path("./generated_sprites")
        output_path = output_dir / f"{args.name}.png"
    
    # Generate
    gen = SpriteGenerator(device=args.device, low_memory=True)
    success = gen.generate_and_save(
        prompt=args.prompt,
        output_path=output_path,
        num_inference_steps=args.steps,
        seed=args.seed
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
