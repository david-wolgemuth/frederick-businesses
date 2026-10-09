#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/david/projects/frederick-businesses"
PROMPT_FILE="${REPO_DIR}/prompts/daily-data-quality.md"
NVM_DIR="${HOME}/.nvm"

. "${NVM_DIR}/nvm.sh"
nvm use --silent default >/dev/null

# Avoid a host-injected SSH config symlink that OpenSSH rejects in systemd.
export GIT_SSH_COMMAND="ssh -F /dev/null -o BatchMode=yes"

# Do not branch or publish unless GitHub CLI can create the requested PR.
gh auth status
BASE_BRANCH="$(git -C "${REPO_DIR}" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
BASE_BRANCH="${BASE_BRANCH#origin/}"
if [[ -z "${BASE_BRANCH}" ]]; then
  BASE_BRANCH="main"
fi
CURRENT_BRANCH="$(git -C "${REPO_DIR}" branch --show-current)"
if [[ "${CURRENT_BRANCH}" != "${BASE_BRANCH}" ]]; then
  echo "Expected checkout on ${BASE_BRANCH}; found ${CURRENT_BRANCH}. Stopping without changing branches." >&2
  exit 1
fi
git -C "${REPO_DIR}" fetch origin "${BASE_BRANCH}"
git -C "${REPO_DIR}" merge --ff-only "origin/${BASE_BRANCH}"
if ! git -C "${REPO_DIR}" diff --cached --quiet; then
  echo "Index already has staged changes; stopping without touching them." >&2
  exit 1
fi
BASE_STATUS="$(git -C "${REPO_DIR}" status --porcelain --untracked-files=all)"
BASE_DIFF_HASH="$(git -C "${REPO_DIR}" diff --binary | sha256sum | cut -d ' ' -f 1)"
START_HEAD="$(git -C "${REPO_DIR}" rev-parse HEAD)"
STAMP="$(date +%Y%m%d-%H%M%S)"
BRANCH="opencode/daily-data-quality-${STAMP}"
git -C "${REPO_DIR}" switch -c "${BRANCH}" "${START_HEAD}"

# Keep required migrations/tests away from the checkout's real business DB.
TEST_DIR="$(mktemp -d "${TMPDIR:-/tmp}/frederick-opencode-test.XXXXXX")"
trap 'rm -rf "${TEST_DIR}"' EXIT
cat > "${TEST_DIR}/opencode_test_settings.py" <<'PY'
import os
from pathlib import Path
from project.settings import *

DATABASES = {
    **DATABASES,
    "default": {
        **DATABASES["default"],
        "NAME": Path(os.environ["FREDERICK_TEST_DB"]),
    },
}
PY
export FREDERICK_TEST_DB="${TEST_DIR}/test.sqlite3"
export DJANGO_SETTINGS_MODULE=opencode_test_settings
export PYTHONPATH="${TEST_DIR}:${REPO_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

cd "${REPO_DIR}"
opencode run --auto \
  --dir "${REPO_DIR}" \
  --title "Daily Frederick Businesses data quality" \
  --file "${PROMPT_FILE}" \
  "Follow the contribution and data-quality instructions in the attached prompt. Make at most one narrowly scoped, tested improvement and one commit."

STATUS_AFTER="$(git -C "${REPO_DIR}" status --porcelain --untracked-files=all)"
DIFF_HASH_AFTER="$(git -C "${REPO_DIR}" diff --binary | sha256sum | cut -d ' ' -f 1)"
if [[ "${STATUS_AFTER}" != "${BASE_STATUS}" || "${DIFF_HASH_AFTER}" != "${BASE_DIFF_HASH}" ]]; then
  echo "The run changed uncommitted/pre-existing files or left uncommitted work; preserving branch ${BRANCH} for review." >&2
  exit 1
fi
COMMIT_COUNT="$(git -C "${REPO_DIR}" rev-list --count "${START_HEAD}..${BRANCH}")"
if [[ "${COMMIT_COUNT}" -eq 0 ]]; then
  echo "No change was warranted; no commit or PR created."
  git -C "${REPO_DIR}" switch "${BASE_BRANCH}"
  git -C "${REPO_DIR}" branch -D "${BRANCH}"
  exit 0
fi
if [[ "${COMMIT_COUNT}" -ne 1 ]]; then
  echo "Expected exactly one run-scoped commit; preserving branch ${BRANCH} without opening a PR." >&2
  exit 1
fi
if ! git -C "${REPO_DIR}" diff --quiet "${START_HEAD}..${BRANCH}" -- .env db.sqlite3 db.yaml; then
  echo "Refusing to publish a PR that changes local credentials or database data." >&2
  exit 1
fi

git -C "${REPO_DIR}" push --set-upstream origin "${BRANCH}"
gh pr create --fill --base "${BASE_BRANCH}" --head "${BRANCH}"
git -C "${REPO_DIR}" switch "${BASE_BRANCH}"
git -C "${REPO_DIR}" branch -D "${BRANCH}"
