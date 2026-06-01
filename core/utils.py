from django.core.files.base import ContentFile
from PIL import Image
import io
import os

def process_image(image_field, max_width=1200, quality=85):
    """Process image: resize and convert to WebP."""
    if not image_field:
        return

    try:
        # Re-open the image file to ensure we're at the beginning
        image_field.open()
        img = Image.open(image_field)
        
        # Convert to RGB if necessary (e.g. for RGBA to WebP)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Resize if too large
        if img.width > max_width:
            output_size = (max_width, int((max_width / img.width) * img.height))
            img = img.resize(output_size, Image.Resampling.LANCZOS)
        
        # Save to WebP
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=quality, optimize=True)
        
        # Change filename extension
        filename = os.path.splitext(os.path.basename(image_field.name))[0] + ".webp"
        
        # Update field with the new content
        # We use save=False to avoid infinite recursion in model.save()
        image_field.save(filename, ContentFile(buffer.getvalue()), save=False)
    except Exception as e:
        print(f"Error processing image: {e}")
