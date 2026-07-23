"""
logger.py -- simple structured logger for fdaskills.
"""

import logging
import sys

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(name)s -- %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
    level=logging.INFO,
)

logger = logging.getLogger("fdaskills")