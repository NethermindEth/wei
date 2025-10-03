"""
Run migrations script.
"""

import asyncio
from app.db.core import run_migrations

if __name__ == "__main__":
    asyncio.run(run_migrations())
