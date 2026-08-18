"""
Vercel Python entrypoint. Vercel's runtime looks for a WSGI-compatible
`app` callable in files under /api — this just points it at the normal
Django WSGI application, with the project root on sys.path so `paulas_african`
is importable from here.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paulas_african.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
