"""
TTA Prototype Package

This package serves as a logical namespace for the prototype code. The actual
implementation lives under the repository folder named "tta.prototype".
To make `import tta.prototype.<subpkg>` work, we extend this package's __path__
so that Python can find subpackages under the sibling directory.
"""

from pathlib import Path

# Add the sibling filesystem directory "tta.prototype" to this package's search path
# so that imports like `tta.prototype.core` resolve into that folder.
try:
    # __file__ = .../tta/prototype/__init__.py; parents[2] -> repo root
    _repo_root = Path(__file__).resolve().parents[2]
    _alt_path = _repo_root / "tta.prototype"
    if _alt_path.exists():
        __path__.append(str(_alt_path))  # type: ignore[name-defined]
except Exception:
    # Non-fatal; imports will just fall back to default behavior
    pass
