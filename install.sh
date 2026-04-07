#!/bin/bash
# Digital Immortality Skill — Installer & Auto-Updater
# Usage: curl -sL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash

set -e

REPO="l12203685/digital-immortality"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
CMD_DIR="${HOME}/.claude/commands"

echo "=== Digital Immortality Skill Installer ==="

# Create commands directory
mkdir -p "$CMD_DIR"

# Download latest skill
echo "Downloading SKILL.md..."
curl -sL "${RAW_BASE}/SKILL.md" -o "${CMD_DIR}/digital-immortality.md"

# Download 繁中版
echo "Downloading SKILL_zh-TW.md..."
curl -sL "${RAW_BASE}/SKILL_zh-TW.md" -o "${CMD_DIR}/digital-immortality-zh.md"

# Download templates
TEMPLATE_DIR="${HOME}/.claude/templates/digital-immortality"
mkdir -p "$TEMPLATE_DIR"
echo "Downloading templates..."
curl -sL "${RAW_BASE}/templates/example_dna.md" -o "${TEMPLATE_DIR}/example_dna.md"
curl -sL "${RAW_BASE}/templates/example_boot_tests.md" -o "${TEMPLATE_DIR}/example_boot_tests.md"

# Set up auto-update hook (runs on Claude Code session start)
HOOKS_DIR="${HOME}/.claude/hooks"
mkdir -p "$HOOKS_DIR"

# Create update script
cat > "${HOOKS_DIR}/update-digital-immortality.sh" << 'HOOKEOF'
#!/bin/bash
# Auto-update digital-immortality skill from GitHub (runs silently)
REPO="l12203685/digital-immortality"
RAW="https://raw.githubusercontent.com/${REPO}/main"
CMD="${HOME}/.claude/commands/digital-immortality.md"
REMOTE_HASH=$(curl -sL "${RAW}/SKILL.md" | md5sum | cut -d' ' -f1 2>/dev/null || echo "")
LOCAL_HASH=$(md5sum "$CMD" 2>/dev/null | cut -d' ' -f1 || echo "none")
if [ -n "$REMOTE_HASH" ] && [ "$REMOTE_HASH" != "$LOCAL_HASH" ]; then
  curl -sL "${RAW}/SKILL.md" -o "$CMD"
  curl -sL "${RAW}/SKILL_zh-TW.md" -o "${HOME}/.claude/commands/digital-immortality-zh.md"
fi
HOOKEOF
chmod +x "${HOOKS_DIR}/update-digital-immortality.sh"

echo ""
echo "=== Installed ==="
echo "  Skill: ${CMD_DIR}/digital-immortality.md"
echo "  繁中版: ${CMD_DIR}/digital-immortality-zh.md"
echo "  Templates: ${TEMPLATE_DIR}/"
echo "  Auto-updater: ${HOOKS_DIR}/update-digital-immortality.sh"
echo ""
echo "To use: open Claude Code and run /digital-immortality"
echo "To update manually: bash ${HOOKS_DIR}/update-digital-immortality.sh"
echo ""
echo "Next steps:"
echo "  1. cp ${TEMPLATE_DIR}/example_dna.md ~/my_dna.md"
echo "  2. Fill in your DNA (start with sections 0-2)"
echo "  3. /digital-immortality in Claude Code"
