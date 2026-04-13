#!/bin/bash
# Digital Immortality Skill Suite — Installer & Auto-Updater
# Usage: curl -sL https://raw.githubusercontent.com/l12203685/digital-immortality/main/install.sh | bash

set -euo pipefail

REPO="l12203685/digital-immortality"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"
CMD_DIR="${HOME}/.claude/commands"
VERSION_FILE="${HOME}/.claude/.digital-immortality-version"
CHECKSUMS_FILE="${HOME}/.claude/.digital-immortality-checksums"

echo "=== Digital Immortality Skill Suite Installer ==="

# --- 1. Python version check ---
check_python() {
  local py_bin
  py_bin=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)
  if [ -z "$py_bin" ]; then
    echo "ERROR: Python 3.9+ is required but no Python interpreter was found." >&2
    echo "       Install Python from https://python.org and re-run this script." >&2
    exit 1
  fi
  local version
  version=$("$py_bin" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
  local major minor
  major=$(echo "$version" | cut -d. -f1)
  minor=$(echo "$version" | cut -d. -f2)
  if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 9 ]; }; then
    echo "ERROR: Python 3.9+ is required; found Python ${version}." >&2
    echo "       Upgrade Python from https://python.org and re-run this script." >&2
    exit 1
  fi
  echo "Python ${version} found — OK"
}
check_python

# --- 2. Offline detection ---
check_network() {
  # Try a lightweight HEAD request first; fall back to ping if curl is absent
  if command -v curl &>/dev/null; then
    if curl -sI --max-time 5 "https://github.com" -o /dev/null 2>/dev/null; then
      return 0
    fi
  elif command -v ping &>/dev/null; then
    if ping -c 1 -W 5 github.com &>/dev/null 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

if ! check_network; then
  echo ""
  echo "WARNING: No internet connection detected. Cannot download skill files." >&2
  echo ""
  echo "To install when you're back online, run:" >&2
  echo "  curl -sL https://raw.githubusercontent.com/${REPO}/${BRANCH}/install.sh | bash" >&2
  echo ""
  echo "If you have the files locally, copy them manually to ${CMD_DIR}/" >&2
  exit 1
fi

# --- 3. SHA-256 helper (cross-platform: sha256sum on Linux, shasum -a 256 on macOS) ---
compute_sha256() {
  local file="$1"
  if command -v sha256sum &>/dev/null; then
    sha256sum "$file" | awk '{print $1}'
  elif command -v shasum &>/dev/null; then
    shasum -a 256 "$file" | awk '{print $1}'
  else
    echo "NOHASH"
  fi
}

# Load existing checksums into an associative array (bash 4+)
declare -A KNOWN_CHECKSUMS=()
if [ -f "$CHECKSUMS_FILE" ]; then
  while IFS='  ' read -r hash path; do
    [ -n "$hash" ] && [ -n "$path" ] && KNOWN_CHECKSUMS["$path"]="$hash"
  done < "$CHECKSUMS_FILE"
fi

# New checksums accumulated during this run
declare -A NEW_CHECKSUMS=()

# Helper: verify an existing file against stored checksum; return 0 = OK / corrupt, 1 = unknown
verify_existing() {
  local dest="$1"
  local stored="${KNOWN_CHECKSUMS[$dest]:-}"
  if [ -z "$stored" ] || [ "$stored" = "NOHASH" ]; then
    return 1  # No baseline — must download
  fi
  local actual
  actual=$(compute_sha256 "$dest")
  if [ "$actual" = "$stored" ]; then
    return 0  # File is intact
  else
    echo "  WARN: checksum mismatch for ${dest} — re-downloading..." >&2
    return 1
  fi
}

# Helper: download with error handling + checksum recording
download() {
  local url="$1"
  local dest="$2"

  # Skip download if file exists and checksum matches
  if [ -f "$dest" ] && verify_existing "$dest"; then
    local hash
    hash=$(compute_sha256 "$dest")
    NEW_CHECKSUMS["$dest"]="$hash"
    echo "  (unchanged) ${dest##*/}"
    return 0
  fi

  if ! curl -sfL --max-time 30 "$url" -o "$dest"; then
    echo "ERROR: Failed to download $url" >&2
    return 1
  fi
  if [ ! -s "$dest" ]; then
    echo "ERROR: Downloaded file is empty: $dest (from $url)" >&2
    return 1
  fi

  # Record new checksum
  local hash
  hash=$(compute_sha256 "$dest")
  NEW_CHECKSUMS["$dest"]="$hash"
}

# Persist all checksums (existing unchanged + newly downloaded)
save_checksums() {
  : > "$CHECKSUMS_FILE"
  for path in "${!NEW_CHECKSUMS[@]}"; do
    echo "${NEW_CHECKSUMS[$path]}  ${path}" >> "$CHECKSUMS_FILE"
  done
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

# Persist checksums for next run
save_checksums
echo "Checksums saved to ${CHECKSUMS_FILE}"

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
CHECKSUMS_FILE="${HOME}/.claude/.digital-immortality-checksums"

# Network check — skip silently if offline
if ! curl -sI --max-time 5 "https://github.com" -o /dev/null 2>/dev/null; then
  exit 0
fi

# Check remote VERSION against local
REMOTE_VERSION=$(curl -sfL --max-time 5 "${RAW}/VERSION" 2>/dev/null || echo "")
LOCAL_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "none")

if [ -z "$REMOTE_VERSION" ]; then
  exit 0  # Network unavailable, skip silently
fi

if [ "$REMOTE_VERSION" = "$LOCAL_VERSION" ]; then
  exit 0  # Up to date
fi

# SHA-256 helper
_sha256() {
  if command -v sha256sum &>/dev/null; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum &>/dev/null; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    echo "NOHASH"
  fi
}

# Version changed — re-download all skills + templates
_dl() {
  local url="$1" dest="$2"
  curl -sfL "$url" -o "$dest" || return 0
  [ -s "$dest" ] || return 0
  echo "$(_sha256 "$dest")  ${dest}" >> "${CHECKSUMS_FILE}.new"
}

: > "${CHECKSUMS_FILE}.new"

_dl "${RAW}/SKILL.md"                          "${CMD}/digital-immortality.md"
_dl "${RAW}/SKILL_zh-TW.md"                   "${CMD}/digital-immortality-zh.md"
_dl "${RAW}/skills/boot-test.md"               "${CMD}/boot-test.md"
_dl "${RAW}/skills/dna-calibrate.md"           "${CMD}/dna-calibrate.md"
_dl "${RAW}/skills/organism-interact.md"       "${CMD}/organism-interact.md"
_dl "${RAW}/skills/recursive-engine.md"        "${CMD}/recursive-engine.md"
_dl "${RAW}/skills/guided-onboarding.md"       "${CMD}/guided-onboarding.md"

mkdir -p "$TDIR"
_dl "${RAW}/templates/example_dna.md"          "${TDIR}/example_dna.md"
_dl "${RAW}/templates/example_boot_tests.md"   "${TDIR}/example_boot_tests.md"

# Atomically replace checksums file and version marker
mv "${CHECKSUMS_FILE}.new" "$CHECKSUMS_FILE"
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
echo "  Checksums: ${CHECKSUMS_FILE}"
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
