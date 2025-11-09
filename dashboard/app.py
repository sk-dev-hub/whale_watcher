# dashboard/app.py
# dashboard/app.py
import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime
from pathlib import Path
import subprocess
import time
import re
import sys

# === ДОБАВЛЯЕМ КОРЕНЬ ПРОЕКТА ===
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# === ПУТИ ===
BACKTEST_DIR = BASE_DIR / "backtests"
LOG_FILE = BASE_DIR / "logs" / "whale_watcher.log"
ENV_FILE = BASE_DIR / ".env"

# === ИМПОРТЫ ===
from config.settings import Settings
from utils.logger import get_logger

log = get_logger()

def check_requirements():
    missing = []
    for module in ["ccxt", "pandas", "matplotlib"]:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        st.error(f"Отсутствуют зависимости: {', '.join(missing)}")
        st.info("Установи: `pip install " + " ".join(missing) + "`")
        st.stop()

check_requirements()

# === ФУНКЦИИ ===
def load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Убираем комментарии после #
                if "#" in line:
                    line = line.split("#", 1)[0].strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

def save_env(env_dict: dict):
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")
    st.success("Настройки сохранены! Перезапусти бота.")

# === ПОМОЩНИК: Чтение логов ===
def tail_log(lines=50):
    if not LOG_FILE.exists():
        return "Лог-файл не найден"
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return "".join(f.readlines()[-lines:])
    except:
        return "Ошибка чтения лога"

# === ПОМОЩНИК: Запуск бэктеста ===
def run_backtest():
    st.info("Запуск бэктеста...")

    python_exe = BASE_DIR / ".venv" / "Scripts" / "python.exe"

    if not python_exe.exists():
        st.error(f"Python не найден: {python_exe}")
        return

    result = subprocess.run(
        [str(python_exe), "backtester/backtester.py"],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR)
    )

    if result.returncode == 0:
        st.success("Бэктест завершён!")
        if result.stdout:
            st.code(result.stdout)
        st.rerun()
    else:
        st.error("Ошибка:")
        st.code(result.stderr)



# === ГЛАВНАЯ СТРАНИЦА ===
st.title("WhaleWatcher AI Дашборд")
st.markdown("### Управление ИИ-трейдером китов")

# === БОКОВАЯ ПАНЕЛЬ: НАСТРОЙКИ ===
with st.sidebar:
    st.header("Режим работы")
    env = load_env()

    mode = st.selectbox("Режим", ["TRADING", "SIGNALS_ONLY", "BACKTEST"],
                        index=["TRADING", "SIGNALS_ONLY", "BACKTEST"].index(env.get("MODE", "TRADING")))
    env["MODE"] = mode

    enable_trading = st.checkbox("Торговля на Binance", value=env.get("ENABLE_TRADING", "true").lower() == "true")
    env["ENABLE_TRADING"] = str(enable_trading).lower()

    st.header("Фильтры китов")
    symbols = st.text_input("Криптовалюты (через запятую)", value=env.get("WHALE_SYMBOLS", "BTC"))
    env["WHALE_SYMBOLS"] = symbols

    min_usd = st.number_input("Мин. сумма (USD)", min_value=100000, value=int(float(env.get("WHALE_MIN_USD", "1000000"))))
    env["WHALE_MIN_USD"] = str(min_usd)

    ignore_unknown = st.checkbox("Игнорировать unknown → unknown", value=env.get("WHALE_IGNORE_UNKNOWN", "true").lower() == "true")
    env["WHALE_IGNORE_UNKNOWN"] = str(ignore_unknown).lower()

    st.header("Бэктест")
    if st.button("Сохранить настройки"):
        save_env(env)

    if st.button("Запустить бэктест"):
        run_backtest()

# === ОСНОВНОЙ ЭКРАН ===
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Последние бэктесты")

    # КНОПКА ОБНОВЛЕНИЯ
    if st.button("Обновить галерею", key="refresh_backtests"):
        st.rerun()

    # ЗАГРУЗКА БЕЗ КЭША
    files = sorted(BACKTEST_DIR.glob("backtest_*.png"), key=os.path.getmtime, reverse=True)[:6]

    if not files:
        st.info("Бэктестов нет. Запусти бэктест.")
    else:
        for file_path in files:
            profit_match = re.search(r"profit_([+-]?\d+,\d+)%", file_path.name)
            profit_val = profit_match.group(1).replace(",", ".") if profit_match else "?"
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            caption = f"{file_path.stem} (+{profit_val}%) — {mtime:%H:%M:%S}"
            st.image(str(file_path), caption=caption, use_column_width=True)

with col2:
    st.subheader("Live-логи")
    log_placeholder = st.empty()
    log_text = tail_log(30)
    log_placeholder.code(log_text, language="text")

    # Автообновление логов
    if st.button("Обновить логи"):
        st.rerun()

# === НИЖНЯЯ ПАНЕЛЬ: СТАТУС ===
st.markdown("---")
st.markdown("### Статус системы")
status_col1, status_col2, status_col3 = st.columns(3)
status_col1.metric("Режим", mode)
status_col2.metric("Торговля", "ВКЛ" if enable_trading else "ВЫКЛ")
status_col3.metric("Китов за сутки", "3", "+1")

# === АВТООБНОВЛЕ Logs ===
if st.checkbox("Автообновление логов (каждые 5 сек)"):
    time.sleep(5)
    st.rerun()

if st.checkbox("Автообновление галереи (каждые 10 сек)"):
    time.sleep(10)
    st.rerun()