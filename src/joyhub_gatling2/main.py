"""Application entry point."""

from .app import *  # noqa: F403,F401

def main() -> int:
    app = RotaryPlayerGUI()
    app.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
