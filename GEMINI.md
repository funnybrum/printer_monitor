The project aims to monitor a Qidi Q1 Pro 3D printer using its Moonraker API and send HTTP notifications when the printer's state changes from "printing" to any other state. The solution is implemented in Python, modularized into `config.py`, `printer.py`, and `notifier.py` modules, and runs within a lightweight Docker container. Unit tests are provided for key functionalities. The project structure, Dockerfile, Makefile, and `README.md` have been set up to facilitate building, running, and testing the service.

**Current State:**

-   The Python service is implemented and modularized.
-   Unit tests are written and reflect the modular structure.
-   `Dockerfile`, `Makefile`, and `README.md` are up-to-date.
-   Previous errors in `tests/test_monitor.py` have been fixed.
-   `q1_monitor.sh` and `resources/printing_completed.mp3` are no longer needed as the Python service replaces this functionality.
