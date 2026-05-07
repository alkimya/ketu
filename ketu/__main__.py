"""Entry point for running Ketu as a module.

This allows running Ketu with: python -m ketu

Routes to ``ketu.cli:main`` (the argparse-based CLI). The legacy
``ketu.display:main`` interactive prompt was deleted in Phase 11.
"""

from ketu.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
