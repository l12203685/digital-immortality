"""Create Immortal Tree -- DIF (Digital Immortal Forest) Discord Setup

Creates a user's private tree in the DIF server:
  - Private category: 🌳 it-{username}
  - Text channels: thinking-{username}, log-{username}
  - Permissions: only the user + bot can see
  - @organism role (created if missing), assigned to user
  - #arena and #scenarios locked to @organism role
  - Announcement posted to #welcome

CLI:
    python platform/create_tree.py --username <name> --user-id <discord_user_id>

Uses Discord REST API (requests). No discord.py dependency.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import requests

BASE = "https://discord.com/api/v10"
CONFIG_PATH = Path(__file__).resolve().parent / "server_config.json"

# -- DIF server constants --
SERVER_ID = "1491042473957658646"
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
BOT_USER_ID = "1489830010297778417"
WELCOME_CHANNEL_ID = "1491665184073322577"
ARENA_CHANNEL_ID = "1491048855779672298"
SCENARIOS_CHANNEL_ID = "1491048860439806102"

# Discord permission bits
VIEW_CHANNEL = 0x0000000000000400          # 1 << 10
SEND_MESSAGES = 0x0000000000000800         # 1 << 11
READ_MESSAGE_HISTORY = 0x0000000000010000  # 1 << 16
BASIC_TEXT = VIEW_CHANNEL | SEND_MESSAGES | READ_MESSAGE_HISTORY


def headers() -> dict[str, str]:
    return {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }


def api_get(path: str) -> Any:
    resp = requests.get(f"{BASE}{path}", headers=headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, data: dict) -> Any:
    resp = requests.post(f"{BASE}{path}", headers=headers(), json=data, timeout=15)
    resp.raise_for_status()
    time.sleep(0.5)
    return resp.json()


def api_put(path: str, data: dict | None = None) -> Any:
    resp = requests.put(
        f"{BASE}{path}", headers=headers(), json=data or {}, timeout=15,
    )
    resp.raise_for_status()
    time.sleep(0.5)
    return resp.json() if resp.content else {}


def api_patch(path: str, data: dict) -> Any:
    resp = requests.patch(f"{BASE}{path}", headers=headers(), json=data, timeout=15)
    resp.raise_for_status()
    time.sleep(0.5)
    return resp.json()


# ── Role helpers ──────────────────────────────────────────────────────────


def find_role(name: str) -> Optional[dict]:
    """Find a role by name. Returns the role dict or None."""
    roles = api_get(f"/guilds/{SERVER_ID}/roles")
    for role in roles:
        if role["name"] == name:
            return role
    return None


def ensure_organism_role() -> dict:
    """Create @organism role if it doesn't exist. Return the role dict."""
    existing = find_role("organism")
    if existing:
        print(f"  @organism role already exists ({existing['id']})")
        return existing
    role = api_post(f"/guilds/{SERVER_ID}/roles", {
        "name": "organism",
        "mentionable": True,
        "color": 0x2ECC71,  # green
    })
    print(f"  Created @organism role ({role['id']})")
    return role


def assign_role(user_id: str, role_id: str) -> None:
    """Add a role to a guild member."""
    api_put(f"/guilds/{SERVER_ID}/members/{user_id}/roles/{role_id}")
    print(f"  Assigned role {role_id} to user {user_id}")


# ── Channel helpers ───────────────────────────────────────────────────────


def lock_channel_to_role(channel_id: str, role_id: str, channel_name: str) -> None:
    """Set a channel so only @organism (+ bot) can view it."""
    overwrites = [
        {  # deny @everyone
            "id": SERVER_ID,
            "type": 0,
            "deny": str(VIEW_CHANNEL),
            "allow": "0",
        },
        {  # allow @organism
            "id": role_id,
            "type": 0,
            "allow": str(BASIC_TEXT),
            "deny": "0",
        },
        {  # allow bot
            "id": BOT_USER_ID,
            "type": 1,
            "allow": str(BASIC_TEXT),
            "deny": "0",
        },
    ]
    api_patch(f"/channels/{channel_id}", {"permission_overwrites": overwrites})
    print(f"  Locked #{channel_name} to @organism role")


def create_private_tree(username: str, user_id: str) -> dict[str, str]:
    """Create the private category + channels for a user's immortal tree.

    Returns dict with category_id, thinking_channel_id, log_channel_id.
    """
    category_name = f"\U0001f333 it-{username}"  # 🌳

    # Permission overwrites for the category
    overwrites = [
        {  # deny @everyone
            "id": SERVER_ID,
            "type": 0,
            "deny": str(VIEW_CHANNEL),
            "allow": "0",
        },
        {  # allow the user
            "id": user_id,
            "type": 1,
            "allow": str(BASIC_TEXT),
            "deny": "0",
        },
        {  # allow the bot
            "id": BOT_USER_ID,
            "type": 1,
            "allow": str(BASIC_TEXT),
            "deny": "0",
        },
    ]

    # Create category (type 4)
    category = api_post(f"/guilds/{SERVER_ID}/channels", {
        "name": category_name,
        "type": 4,
        "permission_overwrites": overwrites,
    })
    cat_id = category["id"]
    print(f"  Created category: {category_name} ({cat_id})")

    # Create thinking channel (inherits category perms)
    thinking = api_post(f"/guilds/{SERVER_ID}/channels", {
        "name": f"thinking-{username}",
        "type": 0,
        "parent_id": cat_id,
        "topic": f"{username}'s recursive self-feed -- private",
    })
    print(f"  Created channel: #thinking-{username} ({thinking['id']})")

    # Create log channel (inherits category perms)
    log_ch = api_post(f"/guilds/{SERVER_ID}/channels", {
        "name": f"log-{username}",
        "type": 0,
        "parent_id": cat_id,
        "topic": f"{username}'s growth log",
    })
    print(f"  Created channel: #log-{username} ({log_ch['id']})")

    return {
        "category_id": cat_id,
        "thinking_channel_id": thinking["id"],
        "log_channel_id": log_ch["id"],
    }


# ── Welcome announcement ─────────────────────────────────────────────────


def post_welcome_announcement(username: str) -> None:
    """Post tree creation announcement to #welcome."""
    content = f"\U0001f333 **{username}** joined Digital Immortal Forest"
    api_post(f"/channels/{WELCOME_CHANNEL_ID}/messages", {"content": content})
    print(f"  Posted announcement to #welcome")


def update_welcome_message() -> None:
    """Post updated welcome/flow message to #welcome."""
    content = """# Digital Immortal Forest \U0001f333

Welcome to the Digital Immortal Forest (DIF).

## How to grow your immortal tree

1. **Install the skill** -- run the digital immortality skill to build your DNA
2. **Build your DNA** -- go through the calibration process
3. **Create your tree** -- tell the server admin your Discord username, or run `/create-tree`
4. **Get your private channels** -- `thinking-{you}` (recursive self-feed) and `log-{you}` (growth log)
5. **Access unlocked** -- you get the `@organism` role and can see #arena and #scenarios

## Channels
- **#arena** -- organisms collide: throw a scenario, see how different organisms respond
- **#scenarios** -- community scenario bank
- **your private tree** -- only you and the bot can see it

## Get started
```bash
curl -sL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash
```

GitHub: https://github.com/l12203685/digital-immortality
"""
    api_post(f"/channels/{WELCOME_CHANNEL_ID}/messages", {"content": content})
    print(f"  Posted updated welcome flow to #welcome")


# ── Main ──────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an immortal tree for a user in the DIF Discord server",
    )
    parser.add_argument("--username", required=True, help="Display name for the tree")
    parser.add_argument("--user-id", required=True, help="Discord user ID")
    parser.add_argument(
        "--update-welcome", action="store_true",
        help="Also post updated welcome/flow message",
    )
    parser.add_argument(
        "--token", default="",
        help="Bot token (overrides DISCORD_BOT_TOKEN env var)",
    )
    args = parser.parse_args()

    # Resolve token: CLI flag > env var
    global BOT_TOKEN  # noqa: PLW0603
    if args.token:
        BOT_TOKEN = args.token
    if not BOT_TOKEN:
        sys.exit("Error: set DISCORD_BOT_TOKEN env var or pass --token")

    username = args.username.lower().strip()
    user_id = args.user_id.strip()

    print(f"Creating immortal tree for {username} (user {user_id})...\n")

    # 1. Ensure @organism role exists
    print("[1/5] Organism role")
    organism_role = ensure_organism_role()

    # 2. Assign @organism role to user
    print("[2/5] Assign role")
    assign_role(user_id, organism_role["id"])

    # 3. Lock #arena and #scenarios to @organism
    print("[3/5] Lock public channels")
    lock_channel_to_role(ARENA_CHANNEL_ID, organism_role["id"], "arena")
    lock_channel_to_role(SCENARIOS_CHANNEL_ID, organism_role["id"], "scenarios")

    # 4. Create private tree
    print("[4/5] Create private tree")
    tree = create_private_tree(username, user_id)

    # 5. Announce in #welcome
    print("[5/5] Announce")
    post_welcome_announcement(username)
    if args.update_welcome:
        update_welcome_message()

    # Output result
    result = {
        "username": username,
        "user_id": user_id,
        "organism_role_id": organism_role["id"],
        **tree,
    }
    print(f"\nDone. Tree channels:")
    print(json.dumps(result, indent=2))

    # Update server_config.json
    config: dict[str, Any] = {}
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    trees = config.setdefault("trees", {})
    trees[username] = result
    config["organism_role_id"] = organism_role["id"]
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Config updated: {CONFIG_PATH}")


if __name__ == "__main__":
    main()
