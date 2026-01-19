import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from backend.config.settings import settings
import shutil
import aiofiles


class FileHandler:
    """Handles file upload, validation, and storage."""
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Validate file has allowed extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if extension is allowed, False otherwise
        """
        ext = filename.split('.')[-1].lower()
        return ext in settings.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """
        Validate file size is within limit.
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            True if size is acceptable, False otherwise
        """
        return file_size <= settings.MAX_UPLOAD_SIZE
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Generate unique filename while preserving extension.
        
        Args:
            original_filename: Original name of uploaded file
            
        Returns:
            Unique filename with UUID
        """
        ext = original_filename.split('.')[-1].lower()
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{ext}"
    
    @staticmethod
    async def save_upload_file(upload_file: UploadFile) -> tuple[str, int]:
        """
        Save uploaded file to disk.
        
        Args:
            upload_file: FastAPI UploadFile object
            
        Returns:
            Tuple of (file_path, file_size)
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate extension
        if not FileHandler.validate_file_extension(upload_file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await upload_file.read()
        file_size = len(content)
        
        # Validate size
        if not FileHandler.validate_file_size(file_size):
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.2f}MB"
            )
        
        # Generate unique filename and path
        unique_filename = FileHandler.generate_unique_filename(upload_file.filename)
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Ensure upload directory exists
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return file_path, file_size
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from disk.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
        return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info or None if file doesn't exist
        """
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime
        }