#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
RUN_DIR="${PROJECT_DIR}/.cloudstudio-run"
LOG_DIR="${RUN_DIR}/logs"
BACKEND_PID_FILE="${RUN_DIR}/backend.pid"
FRONTEND_PID_FILE="${RUN_DIR}/frontend.pid"
BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"

mkdir -p "${LOG_DIR}"

info() {
  printf '[ISLE] %s\n' "$*"
}

fail() {
  printf '[ISLE] 错误：%s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "缺少命令：$1"
}

pid_is_running() {
  local pid_file="$1"
  [[ -f "${pid_file}" ]] || return 1
  local pid
  pid="$(tr -d '[:space:]' < "${pid_file}")"
  [[ "${pid}" =~ ^[0-9]+$ ]] || return 1
  kill -0 "${pid}" 2>/dev/null
}

wait_for_url() {
  local name="$1"
  local url="$2"
  local log_file="$3"
  local attempts="${4:-60}"

  for ((i = 1; i <= attempts; i += 1)); do
    if curl --fail --silent --show-error "${url}" >/dev/null 2>&1; then
      info "${name}已就绪：${url}"
      return 0
    fi
    sleep 1
  done

  printf '\n[ISLE] %s启动失败，最近日志：\n' "${name}" >&2
  tail -n 60 "${log_file}" >&2 || true
  return 1
}

install_dependencies() {
  require_command python3
  require_command npm
  require_command curl

  [[ -f "${BACKEND_DIR}/.env" ]] || fail "未找到 backend/.env，请先把配置文件放到该位置"

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
}

check_database() {
  # 仓库中的 database/law_game.db 是最终 SQLite 备份。只有运行副本缺失时才恢复。
  if [[ ! -f "${BACKEND_DIR}/law_game.db" && -f "${PROJECT_DIR}/database/law_game.db" ]]; then
    cp "${PROJECT_DIR}/database/law_game.db" "${BACKEND_DIR}/law_game.db"
  fi

  info "检查数据库连接并初始化缺失的数据表……"
  (
    cd "${BACKEND_DIR}"
    .venv/bin/python - <<'PY'
from sqlalchemy import func, select, text

from app.database import SessionLocal, engine, init_db
from app.models.database import Event

with engine.connect() as connection:
    connection.execute(text("SELECT 1"))

init_db()
with SessionLocal() as session:
    event_count = session.scalar(select(func.count()).select_from(Event)) or 0

print(f"[ISLE] 数据库类型：{engine.url.get_backend_name()}")
print(f"[ISLE] 国内案例数量：{event_count}")
if event_count == 0:
    print("[ISLE] 警告：当前数据库没有案例数据；未自动导入，以免覆盖远程库。")
PY
  ) || fail "数据库连接失败。若使用腾讯云 MySQL，请检查安全组/白名单是否允许 Cloud Studio 访问"
}

start_backend() {
  if pid_is_running "${BACKEND_PID_FILE}"; then
    info "后端已在运行（PID $(<"${BACKEND_PID_FILE}")）"
    return 0
  fi

  info "启动后端（端口 8000）……"
  (
    cd "${BACKEND_DIR}"
    nohup .venv/bin/python -m uvicorn app.main:app \
      --host 0.0.0.0 \
      --port 8000 \
      >"${BACKEND_LOG}" 2>&1 &
    echo "$!" >"${BACKEND_PID_FILE}"
  )

  if ! wait_for_url "后端" "http://127.0.0.1:8000/health" "${BACKEND_LOG}"; then
    rm -f "${BACKEND_PID_FILE}"
    fail "后端未能正常启动"
  fi
}

start_frontend() {
  if pid_is_running "${FRONTEND_PID_FILE}"; then
    info "前端已在运行（PID $(<"${FRONTEND_PID_FILE}")）"
    return 0
  fi

  info "启动前端（端口 5173）……"
  (
    cd "${FRONTEND_DIR}"
    nohup ./node_modules/.bin/vite --host 0.0.0.0 \
      >"${FRONTEND_LOG}" 2>&1 &
    echo "$!" >"${FRONTEND_PID_FILE}"
  )

  if ! wait_for_url "前端" "http://127.0.0.1:5173" "${FRONTEND_LOG}"; then
    rm -f "${FRONTEND_PID_FILE}"
    fail "前端未能正常启动"
  fi
}

stop_service() {
  local name="$1"
  local pid_file="$2"

  if ! pid_is_running "${pid_file}"; then
    rm -f "${pid_file}"
    info "${name}未运行"
    return 0
  fi

  local pid
  pid="$(<"${pid_file}")"
  kill "${pid}"
  for ((i = 1; i <= 15; i += 1)); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      rm -f "${pid_file}"
      info "${name}已停止"
      return 0
    fi
    sleep 1
  done

  fail "${name}未在 15 秒内停止（PID ${pid}），请手动检查该进程"
}

show_status() {
  if pid_is_running "${BACKEND_PID_FILE}"; then
    info "后端：运行中（PID $(<"${BACKEND_PID_FILE}")，端口 8000）"
  else
    info "后端：未运行"
  fi

  if pid_is_running "${FRONTEND_PID_FILE}"; then
    info "前端：运行中（PID $(<"${FRONTEND_PID_FILE}")，端口 5173）"
  else
    info "前端：未运行"
  fi
}

show_logs() {
  touch "${BACKEND_LOG}" "${FRONTEND_LOG}"
  tail -n 80 -f "${BACKEND_LOG}" "${FRONTEND_LOG}"
}

case "${1:-start}" in
  start)
    install_dependencies
    check_database
    start_backend
    start_frontend
    show_status
    printf '\n'
    info "启动完成。请在 Cloud Studio 的“端口”面板打开 5173。"
    info "API 文档端口为 8000，日志命令：bash scripts/cloud-studio.sh logs"
    ;;
  stop)
    stop_service "前端" "${FRONTEND_PID_FILE}"
    stop_service "后端" "${BACKEND_PID_FILE}"
    ;;
  status)
    show_status
    ;;
  logs)
    show_logs
    ;;
  *)
    printf '用法：bash scripts/cloud-studio.sh {start|stop|status|logs}\n' >&2
    exit 2
    ;;
esac
