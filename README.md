# icka

irccloud keep-alive

Converted from the Go version: https://github.com/osm/icka

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```sh
# Execute with command line arguments
python icka.py -email <email> -password <password>

# Provide credentials from environment
export ICKA_EMAIL=<email>
export ICKA_PASSWORD=<password>
python icka.py

# Run once every hour, without exiting
python icka.py -email <email> -password <password> -forever
```

## Requirements

- Python 3.6+
- `requests`
- `websocket-client`
