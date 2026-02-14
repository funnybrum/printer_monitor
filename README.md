# Q1 Printer Monitor

A monitoring service for the **Qidi Q1 Pro** 3D printer. It watches the printer status via the [Moonraker API](https://moonraker.readthedocs.io/) and sends push notifications on state changes (e.g. printing complete, errors). While a print is running, it also performs real-time issue detection on the printer's video stream using a YOLOv5 model with [OpenVINO](https://docs.openvino.ai/) GPU inference to catch problems like spaghetti failures early.

## Features

- **Print state monitoring** — Polls the printer at a configurable interval and sends notifications when the state changes (printing &rarr; idle, complete, or error).
- **AI-based issue detection** — Automatically starts when a print begins. Captures frames from the MJPEG camera stream and runs inference to detect spaghetti and other print failures.
- **Annotated image notifications** — When an issue is detected, sends a notification with an annotated snapshot showing the detected problem.
- **Area of interest filtering** — Configurable bounding box to focus detection on the print area and reduce false positives.
- **Per-class confidence thresholds** — Fine-tune sensitivity for each detection class independently.

## Prerequisites

- Docker
- An Intel GPU (for OpenVINO GPU inference)
- A Qidi Q1 Pro printer (or compatible) with Moonraker API enabled
- An MJPEG camera stream URL from the printer
- A notification service endpoint (URL + API token)

## Quick Start

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd printer_monitor
   ```

2. **Create the configuration file**

   ```bash
   cp config/config.yaml.example config/config.yaml
   ```

   Edit `config/config.yaml` with your printer and notification settings (see [Configuration](#configuration) below).

3. **Build the Docker image**

   ```bash
   make build
   ```

4. **Run the service**

   ```bash
   make run
   ```

   > The container runs with `--privileged` to access the Intel GPU for OpenVINO inference.

## Configuration

Copy `config/config.yaml.example` to `config/config.yaml` and update the values.

### Configuration Details

| Setting | Description |
|---|---|
| `printer.ip` / `printer.port` | Address of the Moonraker API on your printer |
| `notifier.url` / `notifier.token` | Endpoint and credentials for push notifications |
| `polling_interval_seconds` | How frequently the printer state is polled |
| `issue_detector.stream_url` | MJPEG stream from the printer camera |
| `issue_detector.confidence_thresholds` | Per-class detection thresholds (0.0–1.0). Classes without an explicit threshold default to 1.0 and are effectively ignored. |
| `issue_detector.detection_area_of_interest` | Rectangle `[x1, y1, x2, y2]` defining the region where detections are considered valid. Only detections with their center inside this box are reported. |

## Architecture

The service runs as a single long-running process with a polling loop:

```
┌──────────────┐       ┌──────────────┐
│   Monitor    │──────▶│   Printer    │  Polls Moonraker API
│  (main loop) │       └──────────────┘
│              │
│              │       ┌──────────────┐
│              │──────▶│   Notifier   │  Sends push notifications
│              │       └──────────────┘
│              │
│              │       ┌──────────────────────┐
│              │──────▶│   Issue Detector     │  Separate process (multiprocessing)
└──────────────┘       │  MJPEG → OpenVINO    │  Runs only during active prints
                       │  → NMS → Filtering   │
                       └──────────────────────┘
```

- **`src/monitor.py`** — Main loop. Polls printer status and spawns/terminates the issue detector process on state changes.
- **`src/printer.py`** — Queries the Moonraker API for printer state.
- **`src/notifier.py`** — Sends push notifications with optional image attachments.
- **`src/issue_detector.py`** — Runs in a separate process. Captures frames, runs OpenVINO inference, and applies confidence thresholds, NMS, and area-of-interest filtering. Rate-limited to 1 inference/sec and 1 notification/min.
- **`src/config.py`** — Singleton YAML config loader.

## Development

### Running Tests

```bash
make test
```

Or run a specific test:

```bash
python3 -m unittest tests.test_monitor.TestMonitor.<test_method>
```

### Project Structure

```
printer_monitor/
├── config/
│   └── config.yaml.example    # Example configuration
├── model/
│   ├── model_torch.xml        # YOLOv5 OpenVINO model
│   └── model_torch.bin        # Model weights
├── src/
│   ├── monitor.py             # Main entry point and polling loop
│   ├── printer.py             # Moonraker API client
│   ├── notifier.py            # Notification sender
│   ├── issue_detector.py      # AI-based print issue detection
│   └── config.py              # Configuration loader
├── tests/                     # Unit tests
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Third-Party Attributions

This project uses the [3dprintfails-yolo5vs](https://huggingface.co/Javiai/3dprintfails-yolo5vs) model by Javiai for print failure detection. See the [NOTICE](NOTICE) file for full attribution details.

## License

This project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
