#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/david/projects/frederick-businesses"
PROMPT_FILE="${REPO_DIR}/prompts/daily-data-quality.md"
STATE_DIR="${HOME}/.local/state/frederick-businesses"
WORKTREE_ROOT="${STATE_DIR}/worktrees"
NVM_DIR="${HOME}/.nvm"

. "${NVM_DIR}/nvm.sh"
nvm use --silent default >/dev/null

# Fail before creating a branch/worktree if GitHub CLI cannot create the PR.
gh auth status
mkdir -p "${WORKTREE_ROOT}"
BASE_BRANCH="$(git -C "${REPO_DIR}" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
BASE_BRANCH="${BASE_BRANCH#origin/}"
if [[ -z "${BASE_BRANCH}" ]]; then
  BASE_BRANCH="main"
fi
git -C "${REPO_DIR}" fetch origin "${BASE_BRANCH}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BRANCH="opencode/daily-data-quality-${STAMP}"
WORKTREE="${WORKTREE_ROOT}/${STAMP}"
git -C "${REPO_DIR}" worktree add -b "${BRANCH}" "${WORKTREE}" "origin/${BASE_BRANCH}"

cd "${WORKTREE}"
opencode run --auto \
  --dir "${WORKTREE}" \
  --title "Daily Frederick Businesses data quality" \
  --file "${PROMPT_FILE}" \
  "Follow the attached contribution and data quality instructions. Make at most one narrowly scoped, tested improvement and one commit."

if [[ -n "$(git -C "${WORKTREE}" status --porcelain)" ]]; then
  echo "OpenCode left uncommitted changes; preserving worktree for review: ${WORKTREE}" >&2
  exit 1
fi
COMMIT_COUNT="$(git -C "${WORKTREE}" rev-list --count "origin/${BASE_BRANCH}..${BRANCH}")"
if [[ "${COMMIT_COUNT}" -eq 0 ]]; then
  echo "No change was warranted; no commit or PR created."
  git -C "${REPO_DIR}" worktree remove "${WORKTREE}"
  git -C "${REPO_DIR}" branch -D "${BRANCH}"
  exit 0
fi
if [[ "${COMMIT_COUNT}" -ne 1 ]]; then
  echo "Expected exactly one run-scoped commit; preserving worktree without opening a PR: ${WORKTREE}" >&2
  exit 1
fi
if ! git -C "${WORKTREE}" diff --quiet "origin/${BASE_BRANCH}...${BRANCH}" -- .env db.sqlite3 db.yaml; then
  echo "Refusing to publish a PR that changes local credentials or database data." >&2
  exit 1
fi

git -C "${WORKTREE}" push --set-upstream origin "${BRANCH}"
gh pr create --fill --base "${BASE_BRANCH}" --head "${BRANCH}"
git -C "${REPO_DIR}" worktree remove "${WORKTREE}"
git -C "${REPO_DIR}" branch -D "${BRANCH}"
