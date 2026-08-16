#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
RUN_DIR="${PROJECT_DIR}/.cloudstudio-run"
LOG_DIR="${RUN_DIR}/logs"
SOURCE_DB="${PROJECT_DIR}/database/law_game.db"
RUNTIME_DB="${RUN_DIR}/law_game.db"
BACKEND_LOG="${LOG_DIR}/preview-backend.log"
FRONTEND_LOG="${LOG_DIR}/preview-frontend.log"
SQLITE_URL="sqlite:///${RUNTIME_DB}"

backend_pid=""
frontend_pid=""

mkdir -p "${LOG_DIR}"
: >"${BACKEND_LOG}"
: >"${FRONTEND_LOG}"

info() {
  printf '[ISLE Preview] %s\n' "$*"
}

fail() {
  printf '[ISLE Preview] 错误：%s\n' "$*" >&2
  exit 1
}

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM

  if [[ -n "${frontend_pid}" ]] && kill -0 "${frontend_pid}" 2>/dev/null; then
    kill "${frontend_pid}" 2>/dev/null || true
  fi
  if [[ -n "${backend_pid}" ]] && kill -0 "${backend_pid}" 2>/dev/null; then
    kill "${backend_pid}" 2>/dev/null || true
  fi

  [[ -z "${frontend_pid}" ]] || wait "${frontend_pid}" 2>/dev/null || true
  [[ -z "${backend_pid}" ]] || wait "${backend_pid}" 2>/dev/null || true
  exit "${exit_code}"
}

trap cleanup EXIT INT TERM

for command_name in python3 npm curl; do
  command -v "${command_name}" >/dev/null 2>&1 || fail "缺少命令：${command_name}"
done

[[ -f "${SOURCE_DB}" ]] || fail "缺少最终数据库：database/law_game.db"

if [[ ! -f "${RUNTIME_DB}" ]]; then
  info "创建 Cloud Studio SQLite 运行副本……"
  cp "${SOURCE_DB}" "${RUNTIME_DB}"
fi

if [[ ! -x "${BACKEND_DIR}/.venv/bin/python" ]]; then
  info "创建 Python 虚拟环境……"
  python3 -m venv "${BACKEND_DIR}/.venv"
fi

info "安装/更新后端依赖……"
"${BACKEND_DIR}/.venv/bin/python" -m pip install \
  --disable-pip-version-check \
  --quiet \
  -r "${BACKEND_DIR}/requirements.txt"

info "安装前端依赖……"
npm --prefix "${FRONTEND_DIR}" ci --silent

info "检查 SQLite 并初始化缺失的数据表……"
(
  cd "${BACKEND_DIR}"
  DATABASE_URL="${SQLITE_URL}" .venv/bin/python - <<'PY'
from sqlalchemy import func, select, text

from app.database import SessionLocal, engine, init_db
from app.models.database import Event

with engine.connect() as connection:
    connection.execute(text("SELECT 1"))

init_db()
with SessionLocal() as session:
    event_count = session.scalar(select(func.count()).select_from(Event)) or 0

print(f"[ISLE Preview] 数据库类型：{engine.url.get_backend_name()}")
print(f"[ISLE Preview] 国内案例数量：{event_count}")
if event_count == 0:
    raise SystemExit("SQLite 运行数据库没有案例数据")
PY
)

info "启动后端（8000）……"
(
  cd "${BACKEND_DIR}"
  export DATABASE_URL="${SQLITE_URL}"
  exec .venv/bin/python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000
) >>"${BACKEND_LOG}" 2>&1 &
backend_pid=$!

for ((attempt = 1; attempt <= 90; attempt += 1)); do
  if curl --fail --silent "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "${backend_pid}" 2>/dev/null; then
    tail -n 80 "${BACKEND_LOG}" >&2 || true
    fail "后端进程提前退出"
  fi
  if [[ "${attempt}" -eq 90 ]]; then
    tail -n 80 "${BACKEND_LOG}" >&2 || true
    fail "后端健康检查超时"
  fi
  sleep 1
done

info "后端健康检查通过"

info "启动前端（5173）……"
(
  cd "${FRONTEND_DIR}"
  export VITE_API_BASE_URL=""
  exec ./node_modules/.bin/vite \
    --host 0.0.0.0 \
    --port 5173
) >>"${FRONTEND_LOG}" 2>&1 &
frontend_pid=$!

for ((attempt = 1; attempt <= 60; attempt += 1)); do
  if curl --fail --silent "http://127.0.0.1:5173/api/v1/events" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "${frontend_pid}" 2>/dev/null; then
    tail -n 80 "${FRONTEND_LOG}" >&2 || true
    fail "前端进程提前退出"
  fi
  if [[ "${attempt}" -eq 60 ]]; then
    tail -n 80 "${FRONTEND_LOG}" >&2 || true
    fail "前端或 API 代理健康检查超时"
  fi
  sleep 1
done

info "前端与 API 代理均已就绪，等待 Cloud Studio 打开 5173 预览"
wait "${frontend_pid}"
