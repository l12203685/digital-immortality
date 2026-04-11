FROM python:3.12-slim

# System deps: git for repo ops, curl+ca-certificates for gh install, tini for proper signal handling
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
        tini \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI (optional but handy for debugging and for the daemon's audit scripts)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Python deps (stdlib + anthropic + requests is all the daemon needs)
RUN pip install --no-cache-dir \
        anthropic \
        requests

# App layer — code lives in /app, working tree clones to persistent /data/repo at runtime
WORKDIR /app
COPY platform/recursive_daemon.py /app/platform/recursive_daemon.py
COPY platform/fly_entrypoint.sh /app/fly_entrypoint.sh
RUN chmod +x /app/fly_entrypoint.sh

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# tini = PID 1 = clean SIGTERM propagation to the python daemon
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/fly_entrypoint.sh"]
