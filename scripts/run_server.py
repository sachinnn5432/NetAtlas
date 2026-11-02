"""Server entry point for NetAtlas."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api.app import create_app
from backend.config.settings import NETATLAS_HOST, NETATLAS_PORT, NETATLAS_DEBUG
from backend.config.logging_config import logger

app = create_app()

if __name__ == "__main__":
    logger.info("Starting NetAtlas Intelligence Server on http://%s:%d", NETATLAS_HOST, NETATLAS_PORT)
    app.run(host=NETATLAS_HOST, port=NETATLAS_PORT, debug=NETATLAS_DEBUG)

