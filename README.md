# icka

irccloud keep-alive (Python version)

## Installation

### Using pip

```sh
# Install dependencies
pip install -r requirements.txt

# Make the script executable (optional)
chmod +x icka.py
```

### Using virtual environment (recommended)

```sh
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Using setup.py

```sh
# Install as a package
pip install .

# Or install in editable mode for development
pip install -e .
```

## Usage

### Command line arguments

```sh
# Execute with command line arguments
python icka.py -email <email> -password <password>

# Or if installed via setup.py
icka -email <email> -password <password>
```

### Environment variables

```sh
# Provide credentials from environment
export ICKA_EMAIL=<email>
export ICKA_PASSWORD=<password>
python icka.py
```

### Run forever mode

```sh
# Run once every hour, without exiting
python icka.py -email <email> -password <password> -forever

# Custom sleep interval (supports h, m, s units)
python icka.py -email <email> -password <password> -forever -sleep-interval 30m
```

### All available options

```sh
python icka.py --help
```

Options:
- `-email` / `--email`: IRCCloud email (or set `ICKA_EMAIL` env var)
- `-password` / `--password`: IRCCloud password (or set `ICKA_PASSWORD` env var)
- `-forever` / `--forever`: Run forever, will sleep after each iteration
- `-sleep-interval` / `--sleep-interval`: Sleep interval in forever mode (default: 1h)
- `-user-agent` / `--user-agent`: Custom User-Agent string (or set `ICKA_USER_AGENT` env var)

## Automation with cron

See `icka.sh` for an example shell script that can be run via cron.

Add to your crontab to run every hour:
```sh
0 * * * * /path/to/python/venv/bin/python /path/to/icka.py -email <email> -password <password> >/dev/null 2>&1
```

Or use the provided shell script:
```sh
0 * * * * /path/to/icka.sh >/dev/null 2>&1
```

## Requirements

- Python 3.6 or higher
- `requests` library for HTTP requests
- `websocket-client` library for WebSocket connections

## Differences from Go version

This Python version is functionally equivalent to the Go version with the following improvements:

1. **Simpler HTTP handling**: Uses the `requests` library instead of manual HTTP client setup
2. **Native JSON support**: Python's built-in JSON handling is more concise
3. **Flexible duration parsing**: Supports h/m/s format (e.g., "1h30m", "90m", "5400s")
4. **Better logging**: Uses Python's `logging` module with timestamps
5. **Environment variable support**: All flags can be set via environment variables with `ICKA_` prefix
6. **Easy installation**: Can be installed as a package via `setup.py`

## License

Same license as the original Go version.

