#!/bin/bash
# Digital Immortality Skill Suite — Installer & Auto-Updater
# Usage: curl -sL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash

set -euo pipefail

REPO="l12203685/digital-immortality"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
CMD_DIR="${HOME}/.claude/commands"
VERSION_FILE="${HOME}/.claude/.digital-immortality-version"

echo "=== Digital Immortality Skill Suite Installer ==="

# Helper: download with error handling
download() {
  local url="$1"
  local dest="$2"
  if ! curl -sfL --max-time 30 "$url" -o "$dest"; then
    echo "ERROR: Failed to download $url" >&2
    return 1
  fi
  if [ ! -s "$dest" ]; then
    echo "ERROR: Downloaded file is empty: $dest (from $url)" >&2
    return 1
  fi
}

# Create directories
mkdir -p "$CMD_DIR"

# Download all skills
echo "Downloading skills..."
download "${RAW_BASE}/SKILL.md" "${CMD_DIR}/digital-immortality.md"
download "${RAW_BASE}/SKILL_zh-TW.md" "${CMD_DIR}/digital-immortality-zh.md"
download "${RAW_BASE}/skills/boot-test.md" "${CMD_DIR}/boot-test.md"
download "${RAW_BASE}/skills/dna-calibrate.md" "${CMD_DIR}/dna-calibrate.md"
download "${RAW_BASE}/skills/organism-interact.md" "${CMD_DIR}/organism-interact.md"
download "${RAW_BASE}/skills/recursive-engine.md" "${CMD_DIR}/recursive-engine.md"
download "${RAW_BASE}/skills/guided-onboarding.md" "${CMD_DIR}/guided-onboarding.md"

# Download templates
TEMPLATE_DIR="${HOME}/.claude/templates/digital-immortality"
mkdir -p "$TEMPLATE_DIR"
echo "Downloading templates..."
download "${RAW_BASE}/templates/example_dna.md" "${TEMPLATE_DIR}/example_dna.md"
download "${RAW_BASE}/templates/example_boot_tests.md" "${TEMPLATE_DIR}/example_boot_tests.md"

# Store current version locally
echo "Recording version..."
download "${RAW_BASE}/VERSION" "${VERSION_FILE}"

# Set up auto-update hook (runs on Claude Code session start)
HOOKS_DIR="${HOME}/.claude/hooks"
mkdir -p "$HOOKS_DIR"

# Create update script — checks VERSION file, re-downloads everything if changed
cat > "${HOOKS_DIR}/update-digital-immortality.sh" << 'HOOKEOF'
#!/bin/bash
# Auto-update digital-immortality skill suite from GitHub (runs silently)
set -euo pipefail

REPO="l12203685/digital-immortality"
RAW="https://raw.githubusercontent.com/${REPO}/main"
CMD="${HOME}/.claude/commands"
TDIR="${HOME}/.claude/templates/digital-immortality"
VERSION_FILE="${HOME}/.claude/.digital-immortality-version"

# Check remote VERSION against local
REMOTE_VERSION=$(curl -sfL --max-time 5 "${RAW}/VERSION" 2>/dev/null || echo "")
LOCAL_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "none")

if [ -z "$REMOTE_VERSION" ]; then
  exit 0  # Network unavailable, skip silently
fi

if [ "$REMOTE_VERSION" = "$LOCAL_VERSION" ]; then
  exit 0  # Up to date
fi

# Version changed — re-download all skills + templates
curl -sfL "${RAW}/SKILL.md" -o "${CMD}/digital-immortality.md" || exit 0
curl -sfL "${RAW}/SKILL_zh-TW.md" -o "${CMD}/digital-immortality-zh.md" || exit 0
curl -sfL "${RAW}/skills/boot-test.md" -o "${CMD}/boot-test.md" || exit 0
curl -sfL "${RAW}/skills/dna-calibrate.md" -o "${CMD}/dna-calibrate.md" || exit 0
curl -sfL "${RAW}/skills/organism-interact.md" -o "${CMD}/organism-interact.md" || exit 0
curl -sfL "${RAW}/skills/recursive-engine.md" -o "${CMD}/recursive-engine.md" || exit 0
curl -sfL "${RAW}/skills/guided-onboarding.md" -o "${CMD}/guided-onboarding.md" || exit 0

mkdir -p "$TDIR"
curl -sfL "${RAW}/templates/example_dna.md" -o "${TDIR}/example_dna.md" || exit 0
curl -sfL "${RAW}/templates/example_boot_tests.md" -o "${TDIR}/example_boot_tests.md" || exit 0

# Update local version marker
echo "$REMOTE_VERSION" > "$VERSION_FILE"
HOOKEOF
chmod +x "${HOOKS_DIR}/update-digital-immortality.sh"

INSTALLED_VERSION=$(tr -d '[:space:]' < "${VERSION_FILE}")
echo ""
echo "=== Installed (v${INSTALLED_VERSION}) ==="
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
