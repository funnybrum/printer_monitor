# Q1 Printer Monitor

This service monitors a Qidi Q1 Pro 3D printer and sends a notification when the printer's state changes from "printing" to any other state.

## Requirements

- Docker
- Python 3

## Setup

1.  **Configure the monitor:**
    -   Copy the example configuration file: `cp config/config.yaml.example config/config.yaml`
    -   Edit `config/config.yaml` and set your printer's IP address, and your notification service's URL and token.

2.  **Build the Docker image:**
    ```bash
    make build
    ```

## Usage

To run the monitor in a Docker container:

```bash
make run
```

## Development

### Running Tests

To run the unit tests:

```bash
make test
```

### Running Tests (outside Docker)

If you wish to run tests directly on your host machine (assuming Python 3 is installed):

1.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run tests:**
    ```bash
    python3 -m unittest discover -s tests
    ```
    Or using the Makefile:
    ```bash
    make test
    ```

### Makefile Targets

-   `all`: Build the Docker image and run the tests.
-   `build`: Build the Docker image.
-   `run`: Run the Docker container.
-   `test`: Run the unit tests.
-   `clean`: Remove temporary files.