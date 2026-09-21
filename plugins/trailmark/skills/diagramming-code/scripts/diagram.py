# /// script
# requires-python = ">=3.12"
# dependencies = ["trailmark"]
# ///
"""Generate Mermaid diagrams from Trailmark code graphs.

Compatibility wrapper for callers using the former script path. New skill
instructions use ``trailmark diagram`` directly.
"""

from __future__ import annotations

import sys

from trailmark.diagram import main


if __name__ == "__main__":
    sys.exit(main())
