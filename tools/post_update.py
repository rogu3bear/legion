#!/usr/bin/env python3
"""
Post update tool for Legion repository.
Sends status messages to agent-feed and other monitoring targets.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> tuple[int, str, str]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def post_to_discord(message: str, webhook_url: str = None) -> bool:
    """Post message to Discord via webhook."""
    if not webhook_url:
        # Try to get webhook URL from environment
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not webhook_url:
            print("⚠️  No Discord webhook URL configured")
            return False
    
    payload = {
        "content": message,
        "username": "Legion Cursor Bot",
        "avatar_url": "https://cdn.discordapp.com/avatars/12345/avatar.png"
    }
    
    curl_cmd = f'''curl -X POST "{webhook_url}" \
        -H "Content-Type: application/json" \
        -d '{json.dumps(payload)}' '''
    
    code, stdout, stderr = run_command(curl_cmd, check=False)
    if code == 0:
        print(f"✅ Message posted to Discord")
        return True
    else:
        print(f"❌ Failed to post to Discord: {stderr}")
        return False


def post_to_agent_feed(message: str) -> bool:
    """Post message to agent-feed channel."""
    # Try to find Discord bot integration
    discord_script = Path("scripts/post_agent_feed.sh")
    if discord_script.exists():
        cmd = f"echo '{message}' | {discord_script}"
        code, stdout, stderr = run_command(cmd, check=False)
        if code == 0:
            print("✅ Message posted to agent-feed")
            return True
        else:
            print(f"⚠️  Failed to post to agent-feed via script: {stderr}")
    
    # Fallback: try environment-based posting
    webhook_url = os.getenv('AGENT_FEED_WEBHOOK_URL')
    if webhook_url:
        return post_to_discord(message, webhook_url)
    
    # Last resort: log to file
    log_file = Path("memory/logs/agent_feed.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(f"✅ Message logged to {log_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to log message: {e}")
        return False


def post_to_echo_log(message: str) -> bool:
    """Post message to Echo Log Index."""
    # Try to use the existing echo logging mechanism
    echo_log_file = Path("memory/logs/task_log.jsonl")
    echo_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "source": "cursor_merge_routine",
        "type": "status_update",
        "message": message,
        "level": "INFO"
    }
    
    try:
        with open(echo_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        print(f"✅ Message logged to Echo Log Index")
        return True
    except Exception as e:
        print(f"❌ Failed to log to Echo Log Index: {e}")
        return False


def post_to_file(message: str, file_path: str) -> bool:
    """Post message to a specific file."""
    log_file = Path(file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(f"✅ Message logged to {log_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to log to file: {e}")
        return False


def format_message(message: str, context: dict = None) -> str:
    """Format message with additional context."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if context:
        context_str = " | ".join([f"{k}: {v}" for k, v in context.items()])
        return f"[{timestamp}] {message} | {context_str}"
    else:
        return f"[{timestamp}] {message}"


def main():
    """Main post update routine."""
    parser = argparse.ArgumentParser(description="Post status updates for Legion")
    parser.add_argument("--target", required=True, 
                        choices=["agent-feed", "echo-log", "discord", "file"],
                        help="Target for the status update")
    parser.add_argument("--message", required=True, help="Message to post")
    parser.add_argument("--file", help="File path (when target is 'file')")
    parser.add_argument("--webhook", help="Discord webhook URL")
    parser.add_argument("--context", help="Additional context as JSON")
    parser.add_argument("--format", action="store_true", help="Format with timestamp")
    
    args = parser.parse_args()
    
    # Parse context if provided
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("⚠️  Invalid JSON context, ignoring...")
    
    # Format message if requested
    message = args.message
    if args.format:
        message = format_message(message, context)
    
    success = False
    
    if args.target == "agent-feed":
        success = post_to_agent_feed(message)
    elif args.target == "echo-log":
        success = post_to_echo_log(message)
    elif args.target == "discord":
        success = post_to_discord(message, args.webhook)
    elif args.target == "file":
        if not args.file:
            print("❌ File path required when target is 'file'")
            return 1
        success = post_to_file(message, args.file)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 