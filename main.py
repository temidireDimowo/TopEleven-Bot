#!/usr/bin/env python3
"""TopEleven Bot — entry point."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.ui.main_window import MainWindow


def main() -> None:
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
