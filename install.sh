#!/bin/bash
# Digital Immortality Skill Suite — Installer & Auto-Updater
# Usage: curl -sL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash

set -e

REPO="l12203685/digital-immortality"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
CMD_DIR="${HOME}/.claude/commands"
VERSION_FILE="${HOME}/.claude/.digital-immortality-version"

echo "=== Digital Immortality Skill Suite Installer ==="

# Create directories
mkdir -p "$CMD_DIR"

# Download all skills
echo "Downloading skills..."
curl -sL "${RAW_BASE}/SKILL.md" -o "${CMD_DIR}/digital-immortality.md"
curl -sL "${RAW_BASE}/SKILL_zh-TW.md" -o "${CMD_DIR}/digital-immortality-zh.md"
curl -sL "${RAW_BASE}/skills/boot-test.md" -o "${CMD_DIR}/boot-test.md"
curl -sL "${RAW_BASE}/skills/dna-calibrate.md" -o "${CMD_DIR}/dna-calibrate.md"
curl -sL "${RAW_BASE}/skills/organism-interact.md" -o "${CMD_DIR}/organism-interact.md"
curl -sL "${RAW_BASE}/skills/recursive-engine.md" -o "${CMD_DIR}/recursive-engine.md"
curl -sL "${RAW_BASE}/skills/guided-onboarding.md" -o "${CMD_DIR}/guided-onboarding.md"

# Download templates
TEMPLATE_DIR="${HOME}/.claude/templates/digital-immortality"
mkdir -p "$TEMPLATE_DIR"
echo "Downloading templates..."
curl -sL "${RAW_BASE}/templates/example_dna.md" -o "${TEMPLATE_DIR}/example_dna.md"
curl -sL "${RAW_BASE}/templates/example_boot_tests.md" -o "${TEMPLATE_DIR}/example_boot_tests.md"

# Store current version locally
echo "Recording version..."
curl -sL "${RAW_BASE}/VERSION" -o "${VERSION_FILE}"

# Set up auto-update hook (runs on Claude Code session start)
HOOKS_DIR="${HOME}/.claude/hooks"
mkdir -p "$HOOKS_DIR"

# Create update script — checks VERSION file, re-downloads everything if changed
cat > "${HOOKS_DIR}/update-digital-immortality.sh" << 'HOOKEOF'
#!/bin/bash
# Auto-update digital-immortality skill suite from GitHub (runs silently)
REPO="l12203685/digital-immortality"
RAW="https://raw.githubusercontent.com/${REPO}/main"
CMD="${HOME}/.claude/commands"
TDIR="${HOME}/.claude/templates/digital-immortality"
VERSION_FILE="${HOME}/.claude/.digital-immortality-version"

# Check remote VERSION against local
REMOTE_VERSION=$(curl -sL --max-time 5 "${RAW}/VERSION" 2>/dev/null || echo "")
LOCAL_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "none")

if [ -z "$REMOTE_VERSION" ]; then
  exit 0  # Network unavailable, skip silently
fi

if [ "$REMOTE_VERSION" = "$LOCAL_VERSION" ]; then
  exit 0  # Up to date
fi

# Version changed — re-download all skills + templates
curl -sL "${RAW}/SKILL.md" -o "${CMD}/digital-immortality.md"
curl -sL "${RAW}/SKILL_zh-TW.md" -o "${CMD}/digital-immortality-zh.md"
curl -sL "${RAW}/skills/boot-test.md" -o "${CMD}/boot-test.md"
curl -sL "${RAW}/skills/dna-calibrate.md" -o "${CMD}/dna-calibrate.md"
curl -sL "${RAW}/skills/organism-interact.md" -o "${CMD}/organism-interact.md"
curl -sL "${RAW}/skills/recursive-engine.md" -o "${CMD}/recursive-engine.md"
curl -sL "${RAW}/skills/guided-onboarding.md" -o "${CMD}/guided-onboarding.md"

mkdir -p "$TDIR"
curl -sL "${RAW}/templates/example_dna.md" -o "${TDIR}/example_dna.md"
curl -sL "${RAW}/templates/example_boot_tests.md" -o "${TDIR}/example_boot_tests.md"

# Update local version marker
echo "$REMOTE_VERSION" > "$VERSION_FILE"
HOOKEOF
chmod +x "${HOOKS_DIR}/update-digital-immortality.sh"

echo ""
echo "=== Installed (v$(cat "${VERSION_FILE}" | tr -d '[:space:]')) ==="
echo ""
echo "  Skills installed:"
echo "    ${CMD_DIR}/digital-immortality.md      (core skill)"
echo "    ${CMD_DIR}/digital-immortality-zh.md   (core skill, 繁中版)"
echo "    ${CMD_DIR}/boot-test.md                (behavioral verification)"
echo "    ${CMD_DIR}/dna-calibrate.md            (interactive calibration)"
echo "    ${CMD_DIR}/organism-interact.md        (social collision)"
echo "    ${CMD_DIR}/recursive-engine.md         (continuous thinking)"
echo "    ${CMD_DIR}/guided-onboarding.md       (new user onboarding)"
echo ""
echo "  Templates: ${TEMPLATE_DIR}/"
echo "  Auto-updater: ${HOOKS_DIR}/update-digital-immortality.sh"
echo "  Version: ${VERSION_FILE}"
echo ""
echo "To use: open Claude Code and run any of:"
echo "  /digital-immortality    — core skill"
echo "  /boot-test              — behavioral verification"
echo "  /dna-calibrate          — interactive calibration"
echo "  /organism-interact      — social collision"
echo "  /recursive-engine       — continuous thinking"
echo "  /guided-onboarding     — new user DNA creation"
echo ""
echo "To update manually: bash ${HOOKS_DIR}/update-digital-immortality.sh"
echo ""
echo "Next steps:"
echo "  1. /guided-onboarding in Claude Code (recommended for new users)"
echo "     OR: cp ${TEMPLATE_DIR}/example_dna.md ~/my_dna.md and fill manually"
echo "  2. /digital-immortality for full system overview"
