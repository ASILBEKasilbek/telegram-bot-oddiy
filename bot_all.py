import os
import subprocess
import time
import sys
import logging
import asyncio

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot_all.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOTS_DIR = os.path.join(BASE_DIR, 'Hamkorlik')
PYTHON_EXECUTABLE = sys.executable

processes = {}

async def log_bot_output(proc, folder):
    """Botning stdout/stderr chiqishlarini loglash."""
    while proc.poll() is None:
        try:
            stdout_line = proc.stdout.readline().strip()
            if stdout_line:
                logger.info(f"[{folder}] {stdout_line}")

            stderr_line = proc.stderr.readline().strip()
            if stderr_line:
                logger.error(f"[{folder}] {stderr_line}")

            await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"[{folder}] Stream o'qishda xato: {e}")
            break

    return_code = proc.poll()
    if return_code is not None:
        logger.info(f"Bot {folder} tugadi, return code: {return_code}")
        if return_code != 0:
            logger.error(f"Bot {folder} xato bilan tugadi, return code: {return_code}")


def start_bot(folder, bot_file_path):
    """Berilgan botni subprocess orqali ishga tushurish."""
    logger.info(f"Bot ishga tushirilmoqda: {folder}")
    try:
        proc = subprocess.Popen(
            [PYTHON_EXECUTABLE, bot_file_path],
            cwd=os.path.dirname(bot_file_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Bot {folder} muvaffaqiyatli ishga tushdi, PID: {proc.pid}")
        return proc
    except Exception as e:
        logger.error(f"Bot {folder} ni ishga tushirishda xato: {e}")
        return None


async def monitor_bots():
    """Hamkorlik botlarini monitoring qilish va kerak bo‘lsa qayta ishga tushirish."""
    while True:
        for folder in sorted(os.listdir(BOTS_DIR)):
            bot_folder_path = os.path.join(BOTS_DIR, folder)
            bot_file_path = os.path.join(bot_folder_path, 'bot.py')

            if not os.path.isdir(bot_folder_path) or not os.path.isfile(bot_file_path):
                continue

            if folder not in processes or processes[folder].poll() is not None:
                if folder in processes:
                    logger.warning(f"Bot {folder} ishdan chiqdi. Qayta ishga tushirilmoqda...")
                    del processes[folder]

                proc = start_bot(folder, bot_file_path)
                if proc:
                    processes[folder] = proc
                    asyncio.create_task(log_bot_output(proc, folder))

                time.sleep(1)  # kichik kechikish

        await asyncio.sleep(5)


async def main():
    logger.info("Skript boshlanmoqda...")

    # 🔹 Asosiy bot.py ni ishga tushurish
    main_bot_path = os.path.join(BASE_DIR, 'bot.py')
    if os.path.isfile(main_bot_path):
        proc = start_bot("main_bot", main_bot_path)
        if proc:
            processes["main_bot"] = proc
            asyncio.create_task(log_bot_output(proc, "main_bot"))
        time.sleep(1)

    # 🔹 Hamkorlikdagi botlarni ishga tushurish
    for folder in sorted(os.listdir(BOTS_DIR)):
        bot_folder_path = os.path.join(BOTS_DIR, folder)
        bot_file_path = os.path.join(bot_folder_path, 'bot.py')

        if not os.path.isdir(bot_folder_path) or not os.path.isfile(bot_file_path):
            continue

        proc = start_bot(folder, bot_file_path)
        if proc:
            processes[folder] = proc
            asyncio.create_task(log_bot_output(proc, folder))
        time.sleep(1)

    # 🔹 Monitoringni ishga tushurish
    await monitor_bots()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Skript to‘xtatilmoqda...")
        for folder, proc in list(processes.items()):
            logger.info(f"Bot {folder} to‘xtatilmoqda...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Bot {folder} majburan o‘chirilmoqda...")
                proc.kill()
        logger.info("Barcha botlar to‘xtatildi.")
