"""File hashing utilities for deduplication."""

import hashlib
from typing import BinaryIO


def calculate_file_hash(file: BinaryIO, algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file for deduplication.

    Args:
        file: File object to hash
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    file.seek(0)

    # Read file in chunks to handle large files efficiently
    chunk_size = 8192
    while chunk := file.read(chunk_size):
        hash_obj.update(chunk)

    file.seek(0)  # Reset file pointer
    return hash_obj.hexdigest()


def calculate_bytes_hash(data: bytes, algorithm: str = "sha256") -> str:
    """
    Calculate hash of bytes.

    Args:
        data: Bytes to hash
        algorithm: Hash algorithm to use (default: sha256)

    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    return hash_obj.hexdigest()
