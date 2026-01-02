#!/usr/bin/env python3
"""
Script to generate remaining project files for Document Intelligence Pipeline.
Run this script to complete the project structure.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def create_file(relative_path: str, content: str) -> None:
    """Create a file with given content."""
    file_path = PROJECT_ROOT / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✓ Created {relative_path}")


def generate_all_files() -> None:
    """Generate all remaining project files."""

    # Create __init__.py files for all packages
    init_files = [
        "src/api/__init__.py",
        "src/api/routes/__init__.py",
        "src/api/schemas/__init__.py",
        "src/api/middleware/__init__.py",
        "src/extractors/__init__.py",
        "src/extractors/prompts/__init__.py",
        "src/validators/__init__.py",
        "src/storage/__init__.py",
        "src/db/__init__.py",
        "src/db/models/__init__.py",
        "src/db/repositories/__init__.py",
        "src/queue/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
    ]

    for init_file in init_files:
        create_file(init_file, '"""Package initialization."""\n')

    print("\n✓ All __init__.py files created!")
    print("\nNext steps:")
    print("1. Review the generated files")
    print("2. Install dependencies: poetry install")
    print("3. Set up environment variables: cp .env.example .env")
    print("4. Run database migrations: poetry run alembic upgrade head")
    print("5. Start the application: poetry run uvicorn src.main:app --reload")


if __name__ == "__main__":
    generate_all_files()
