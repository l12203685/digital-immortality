"""Digital Organisms Discord Server Setup Script.

Given a server ID and bot token, automatically creates:
- Public channels: welcome, arena, scenarios
- Private category per organism: organism-{name}/thinking, organism-{name}/log
- Roles: organism-{name} (only sees own private channels)
- Webhooks: one per #thinking channel (for remote trigger integration)

Usage:
    python server_setup.py --server-id 123456 --token BOT_TOKEN --organism edward
"""
import argparse
import json
import os
import time

import requests

BASE = "https://discord.com/api/v10"


def headers(token: str) -> dict:
    return {"Authorization": f"Bot {token}", "Content-Type": "application/json"}


def create_channel(token: str, server_id: str, name: str, ch_type: int = 0,
                   parent_id: str = None, topic: str = None,
                   permission_overwrites: list = None) -> dict:
    """Create a channel. type 0=text, 4=category."""
    data = {"name": name, "type": ch_type}
    if parent_id:
        data["parent_id"] = parent_id
    if topic:
        data["topic"] = topic
    if permission_overwrites:
        data["permission_overwrites"] = permission_overwrites
    resp = requests.post(f"{BASE}/guilds/{server_id}/channels",
                         headers=headers(token), json=data)
    resp.raise_for_status()
    result = resp.json()
    print(f"  Created {'category' if ch_type == 4 else 'channel'}: #{name} ({result['id']})")
    time.sleep(0.5)  # Rate limit
    return result


def create_role(token: str, server_id: str, name: str) -> dict:
    """Create a role."""
    resp = requests.post(f"{BASE}/guilds/{server_id}/roles",
                         headers=headers(token),
                         json={"name": name, "mentionable": True})
    resp.raise_for_status()
    result = resp.json()
    print(f"  Created role: @{name} ({result['id']})")
    time.sleep(0.5)
    return result


def create_webhook(token: str, channel_id: str, name: str) -> dict:
    """Create a webhook for a channel."""
    resp = requests.post(f"{BASE}/channels/{channel_id}/webhooks",
                         headers=headers(token),
                         json={"name": name})
    resp.raise_for_status()
    result = resp.json()
    url = f"https://discord.com/api/webhooks/{result['id']}/{result['token']}"
    print(f"  Created webhook: {name} → {url[:60]}...")
    return result


def setup_public_channels(token: str, server_id: str) -> dict:
    """Create public channels."""
    channels = {}
    channels["welcome"] = create_channel(
        token, server_id, "welcome",
        topic="Digital Organisms 平台說明 + 安裝指令"
    )
    channels["arena"] = create_channel(
        token, server_id, "arena",
        topic="碰撞場 — 拋場景，看不同 organisms 怎麼回答"
    )
    channels["scenarios"] = create_channel(
        token, server_id, "scenarios",
        topic="場景題庫 — 社群貢獻的決策場景"
    )
    return channels


def setup_organism(token: str, server_id: str, name: str,
                   owner_id: str = None, bot_id: str = None) -> dict:
    """Set up a private organism space."""
    # Create role
    role = create_role(token, server_id, f"organism-{name}")

    # Permission overwrites: deny @everyone, allow role + bot
    overwrites = [
        {"id": server_id, "type": 0, "deny": "1024"},  # @everyone can't view
        {"id": role["id"], "type": 0, "allow": "1024"},  # role can view
    ]
    if bot_id:
        overwrites.append({"id": bot_id, "type": 1, "allow": "1024"})

    # Create category
    category = create_channel(
        token, server_id, f"organism-{name}", ch_type=4,
        permission_overwrites=overwrites
    )

    # Create channels under category
    thinking = create_channel(
        token, server_id, "thinking", parent_id=category["id"],
        topic=f"{name}'s recursive self-feed — private"
    )
    log = create_channel(
        token, server_id, "log", parent_id=category["id"],
        topic=f"{name}'s growth log"
    )

    # Create webhook for thinking channel (remote trigger writes here)
    webhook = create_webhook(token, thinking["id"], f"{name}-recursive")

    return {
        "role": role,
        "category": category,
        "thinking": thinking,
        "log": log,
        "webhook": webhook,
    }


def post_welcome(token: str, channel_id: str) -> None:
    """Post welcome message."""
    content = """# Digital Organisms 🧬

歡迎來到數位有機體平台。

## 什麼是數位有機體？
用 AI 建立一個行為等價的數位分身。它用你的決策原則做出你會做的選擇。

## 怎麼開始？
```bash
curl -sL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash
```

## 頻道說明
- **#arena** — 碰撞場：拋出場景，看不同 organisms 怎麼回答
- **#scenarios** — 場景題庫
- **organism-{你的名字}/** — 你的私人空間（#thinking = 遞迴思考，#log = 成長紀錄）

## 文件
- GitHub: https://github.com/l12203685/digital-immortality
- 繁中 Skill: SKILL_zh-TW.md
"""
    requests.post(f"{BASE}/channels/{channel_id}/messages",
                  headers=headers(token),
                  json={"content": content})
    print(f"  Posted welcome message")


def main():
    parser = argparse.ArgumentParser(description="Digital Organisms Server Setup")
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--token", required=True, help="Discord bot token")
    parser.add_argument("--organism", default="edward", help="First organism name")
    parser.add_argument("--owner-id", help="Discord user ID of organism owner")
    parser.add_argument("--bot-id", help="Bot user ID (for permission overwrites)")
    args = parser.parse_args()

    print(f"Setting up Digital Organisms server {args.server_id}...")

    print("\n[Public Channels]")
    public = setup_public_channels(args.token, args.server_id)

    print(f"\n[Organism: {args.organism}]")
    organism = setup_organism(args.token, args.server_id, args.organism,
                              owner_id=args.owner_id, bot_id=args.bot_id)

    print("\n[Welcome Message]")
    post_welcome(args.token, public["welcome"]["id"])

    print("\n=== Setup Complete ===")
    print(f"  Public: #welcome, #arena, #scenarios")
    print(f"  Organism: organism-{args.organism}/ (#thinking, #log)")
    print(f"  Webhook URL: https://discord.com/api/webhooks/{organism['webhook']['id']}/{organism['webhook']['token']}")
    print(f"\n  Next: assign @organism-{args.organism} role to the owner")

    # Save config
    config = {
        "server_id": args.server_id,
        "public_channels": {k: v["id"] for k, v in public.items()},
        "organisms": {
            args.organism: {
                "role_id": organism["role"]["id"],
                "category_id": organism["category"]["id"],
                "thinking_channel_id": organism["thinking"]["id"],
                "log_channel_id": organism["log"]["id"],
                "webhook_url": f"https://discord.com/api/webhooks/{organism['webhook']['id']}/{organism['webhook']['token']}",
            }
        }
    }
    config_path = os.path.join(os.path.dirname(__file__), "server_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n  Config saved: {config_path}")


if __name__ == "__main__":
    main()
