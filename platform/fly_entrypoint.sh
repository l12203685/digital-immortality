#!/bin/bash
# Fly.io entrypoint for the recursive daemon.
# Clones the repo into the persistent volume on first boot, pulls on subsequent boots,
# then execs the daemon so it becomes PID 1 (via tini) for clean signal handling.

set -euo pipefail

# --- Secrets sanity check (fail fast if missing) ---
: "${GITHUB_TOKEN:?GITHUB_TOKEN secret is required}"
: "${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY secret is required}"

REPO_URL="https://github.com/l12203685/digital-immortality.git"
REPO_DIR="/data/repo"

# --- Git identity + credential helper (idempotent) ---
git config --global user.email "agent@digital-immortality.local"
git config --global user.name "digital-immortality-daemon"
git config --global pull.rebase true
git config --global --add safe.directory "${REPO_DIR}"

# Embed the PAT in the credential helper store (not in the remote URL — avoids
# leaking it to `git remote -v` output and git operation logs).
mkdir -p /root
umask 077
printf "https://x-access-token:%s@github.com\n" "${GITHUB_TOKEN}" > /root/.git-credentials
git config --global credential.helper store

# --- First-boot clone or existing-volume update ---
if [ ! -d "${REPO_DIR}/.git" ]; then
    echo "[fly_entrypoint] First boot: cloning ${REPO_URL} into ${REPO_DIR}"
    rm -rf "${REPO_DIR}"
    git clone --depth=50 "${REPO_URL}" "${REPO_DIR}"
else
    echo "[fly_entrypoint] Existing volume: fetching latest"
    cd "${REPO_DIR}"
    git fetch origin main || true
    git reset --hard origin/main || true
fi

cd "${REPO_DIR}"
echo "[fly_entrypoint] HEAD: $(git rev-parse --short HEAD) on $(git rev-parse --abbrev-ref HEAD)"

# Handoff — exec replaces the shell, tini stays PID 1 and forwards signals cleanly.
echo "[fly_entrypoint] Launching recursive daemon (API mode, interval=0)"
exec python platform/recursive_daemon.py --interval 0
