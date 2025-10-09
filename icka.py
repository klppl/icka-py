#!/usr/bin/env python3
"""
icka - IRCCloud Keep-Alive
Keeps your IRCCloud session alive by periodically authenticating.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

import requests
import websocket

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
)


class AuthTokenResponse:
    """Response from auth token request."""
    def __init__(self, data: dict):
        self.token = data.get("token", "")
        self.success = data.get("success", False)


class SessionResponse:
    """Response from session request."""
    def __init__(self, data: dict):
        self.api_host = data.get("api_host", "")
        self.session = data.get("session", "")
        self.success = data.get("success", False)
        self.uid = data.get("uid", 0)
        self.url = data.get("url", "")
        self.websocket_host = data.get("websocket_host", "")
        self.websocket_path = data.get("websocket_path", "")


class AuthResponse:
    """Response from websocket auth."""
    def __init__(self, data: dict):
        self.success = data.get("success", False)


def http_request(
    method: str,
    url: str,
    form_data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> bytes:
    """
    Make an HTTP request.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL to request
        form_data: Optional form data to send
        headers: Optional headers to include
        
    Returns:
        Response body as bytes
        
    Raises:
        requests.RequestException: If request fails
    """
    if headers is None:
        headers = {}
    
    if form_data:
        response = requests.request(
            method,
            url,
            data=form_data,
            headers=headers
        )
    else:
        response = requests.request(
            method,
            url,
            headers=headers
        )
    
    response.raise_for_status()
    return response.content


def get_auth_token(user_agent: str) -> AuthTokenResponse:
    """
    Get authentication token from IRCCloud.
    
    Args:
        user_agent: User agent string to use
        
    Returns:
        AuthTokenResponse object
        
    Raises:
        Exception: If request fails or response is invalid
    """
    resp = http_request(
        "POST",
        "https://api-3.irccloud.com/chat/auth-formtoken",
        headers={"User-Agent": user_agent}
    )
    
    data = json.loads(resp)
    return AuthTokenResponse(data)


def get_session(
    email: str,
    password: str,
    token: str,
    user_agent: str
) -> SessionResponse:
    """
    Get session from IRCCloud.
    
    Args:
        email: IRCCloud email
        password: IRCCloud password
        token: Auth token
        user_agent: User agent string
        
    Returns:
        SessionResponse object
        
    Raises:
        Exception: If request fails or response is invalid
    """
    form_data = {
        "email": email,
        "password": password,
        "token": token
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": user_agent,
        "X-Auth-FormToken": token
    }
    
    resp = http_request(
        "POST",
        "https://www.irccloud.com/chat/login",
        form_data=form_data,
        headers=headers
    )
    
    data = json.loads(resp)
    return SessionResponse(data)


def auth_websocket(
    session: str,
    host: str,
    path: str,
    user_agent: str
) -> bool:
    """
    Authenticate via WebSocket.
    
    Args:
        session: Session ID
        host: WebSocket host
        path: WebSocket path
        user_agent: User agent string
        
    Returns:
        True if authentication successful, False otherwise
        
    Raises:
        Exception: If WebSocket connection fails
    """
    ws_url = f"wss://{host}{path}"
    
    headers = {
        "Host": host,
        "Origin": "https://www.irccloud.com",
        "User-Agent": user_agent
    }
    
    ws = websocket.create_connection(ws_url, header=headers)
    
    try:
        # Send auth request
        auth_req = {
            "cookie": session,
            "_method": "auth",
            "_reqid": 1
        }
        ws.send(json.dumps(auth_req))
        
        # Read response
        response = ws.recv()
        data = json.loads(response)
        auth_resp = AuthResponse(data)
        
        # Close connection
        ws.close()
        
        return auth_resp.success
    except Exception as e:
        ws.close()
        raise e


def keep_alive(email: str, password: str, user_agent: str) -> None:
    """
    Perform keep-alive operation.
    
    Args:
        email: IRCCloud email
        password: IRCCloud password
        user_agent: User agent string
        
    Raises:
        Exception: If any step fails
    """
    # Get auth token
    token_resp = get_auth_token(user_agent)
    if not token_resp.success:
        raise Exception("get auth token failed")
    
    # Get session
    session_resp = get_session(email, password, token_resp.token, user_agent)
    if not session_resp.success:
        raise Exception("get session failed, check email and password")
    
    # Authenticate via WebSocket
    ws_path = session_resp.websocket_path + "?exclude_archives=1"
    success = auth_websocket(
        session_resp.session,
        session_resp.websocket_host,
        ws_path,
        user_agent
    )
    
    if not success:
        raise Exception("auth websocket request failed")


def parse_duration(duration_str: str) -> float:
    """
    Parse duration string (e.g., '1h', '30m', '1h30m') to seconds.
    
    Args:
        duration_str: Duration string
        
    Returns:
        Duration in seconds
        
    Raises:
        ValueError: If duration string is invalid
    """
    total_seconds = 0.0
    current_num = ""
    
    for char in duration_str:
        if char.isdigit() or char == '.':
            current_num += char
        elif char in 'hms':
            if not current_num:
                raise ValueError(f"Invalid duration format: {duration_str}")
            
            num = float(current_num)
            if char == 'h':
                total_seconds += num * 3600
            elif char == 'm':
                total_seconds += num * 60
            elif char == 's':
                total_seconds += num
            
            current_num = ""
        else:
            raise ValueError(f"Invalid duration format: {duration_str}")
    
    if current_num:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    return total_seconds


def die(message: str) -> None:
    """Print error message and exit."""
    print(message, file=sys.stderr)
    sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="IRCCloud Keep-Alive - Keeps your IRCCloud session alive"
    )
    
    parser.add_argument(
        "-email",
        "--email",
        default=os.environ.get("ICKA_EMAIL", ""),
        help="IRCCloud email (or set ICKA_EMAIL env var)"
    )
    
    parser.add_argument(
        "-password",
        "--password",
        default=os.environ.get("ICKA_PASSWORD", ""),
        help="IRCCloud password (or set ICKA_PASSWORD env var)"
    )
    
    parser.add_argument(
        "-forever",
        "--forever",
        action="store_true",
        default=os.environ.get("ICKA_FOREVER", "").lower() in ("true", "1", "yes"),
        help="Run forever, will sleep for one hour after each iteration"
    )
    
    parser.add_argument(
        "-sleep-interval",
        "--sleep-interval",
        default=os.environ.get("ICKA_SLEEP_INTERVAL", "1h"),
        help="Sleep interval, used in -forever mode (e.g., '1h', '30m', '1h30m')"
    )
    
    parser.add_argument(
        "-user-agent",
        "--user-agent",
        default=os.environ.get("ICKA_USER_AGENT", DEFAULT_USER_AGENT),
        help="User-Agent string"
    )
    
    args = parser.parse_args()
    
    # Validate required arguments
    if not args.email:
        die("-email is required")
    
    if not args.password:
        die("-password is required")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S"
    )
    
    # Single run mode
    if not args.forever:
        try:
            keep_alive(args.email, args.password, args.user_agent)
        except Exception as e:
            die(str(e))
        return
    
    # Forever mode
    try:
        sleep_seconds = parse_duration(args.sleep_interval)
    except ValueError as e:
        die(f"unable to parse -sleep-interval: {e}")
    
    while True:
        try:
            keep_alive(args.email, args.password, args.user_agent)
            logging.info("successfully kept connection alive")
        except Exception as e:
            logging.error(f"keep alive error: {e}")
        
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()

