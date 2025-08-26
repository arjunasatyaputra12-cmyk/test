import os
import time
import subprocess
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from pyvirtualdisplay import Display
from IPython.display import Image, display as ipy_display


# Start virtual display (headless X server)
virtual_display = Display(visible=0, size=(1920, 1080))
virtual_display.start()

# Reduce verbose logging from urllib3
logging.getLogger("urllib3").setLevel(logging.ERROR)

# === Paths identical to the original script === #
# CHROME_PATH is not used in the original opening flow
# CHROME_PATH = "/content/chrome-dev/chrome-linux64/chrome"
CHROMEDRIVER_PATH = "/content/chromedriver-dev/chromedriver-linux64/chromedriver"
PROFILE_PATH = "/content/chrome-profile"

# Path for screenshots (same style as example)
screenshot_path = "/content/screenshot.png"

# Ensure chromedriver is executable (equivalent of `!chmod +x $CHROMEDRIVER_PATH` in Colab)
try:
	subprocess.run(["chmod", "+x", CHROMEDRIVER_PATH], check=True)
	print("✅ Chromedriver permission set (+x)")
except Exception as e:
	print(f"⚠️ Gagal set permission chromedriver: {e}")

# Clean up potential Chrome profile lock files (identical behavior)
lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket"]
for lf in lock_files:
	lf_path = os.path.join(PROFILE_PATH, lf)
	if os.path.exists(lf_path):
		try:
			os.remove(lf_path)
			print(f"✅ Menghapus lock file: {lf}")
		except Exception as e:
			print(f"⚠️ Gagal hapus {lf}: {e}")

# Chrome options identical to the source script
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={PROFILE_PATH}")
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

service = Service(CHROMEDRIVER_PATH)

driver = None
try:
	driver = webdriver.Chrome(service=service, options=chrome_options)
	print("🌍 Membuka https://chatgpt.com ...")
	driver.get("https://chatgpt.com")
	# Biarkan halaman terbuka sebentar agar proses loading selesai saat dijalankan non-interaktif
	time.sleep(10)
	# Ambil dan tampilkan screenshot seperti contoh
	try:
		driver.save_screenshot(screenshot_path)
		ipy_display(Image(filename=screenshot_path))
		print("📸 Screenshot ditampilkan.")
	except Exception as e:
		print(f"⚠️ Gagal menampilkan screenshot: {e}. Disimpan di {screenshot_path}")
	print("✅ Selesai membuka halaman.")
finally:
	# Tutup browser untuk mencegah proses tertinggal saat dijalankan otomatis
	try:
		if driver is not None:
			driver.quit()
			print("🧹 Browser ditutup.")
	except Exception as e:
		print(f"⚠️ Gagal menutup browser: {e}")
	# Stop virtual display
	try:
		virtual_display.stop()
		print("🛑 Virtual display dimatikan.")
	except Exception as e:
		print(f"⚠️ Gagal mematikan virtual display: {e}")