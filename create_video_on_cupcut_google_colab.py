# @title 3) Membuat video di CapCut

import os, time, threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import subprocess, shlex
import shutil

from IPython.display import Image, display, clear_output

from IPython.display import Image, display as ipy_display
from pyvirtualdisplay import Display

# Start virtual display
virtual_display = Display(visible=0, size=(1920, 1080))
virtual_display.start()

import logging
logging.getLogger("urllib3").setLevel(logging.ERROR)

# === Path binary Chrome & chromedriver === #
#CHROME_PATH = "/content/chrome-dev/chrome-linux64/chrome"
CHROMEDRIVER_PATH = "/content/chromedriver-dev/chromedriver-linux64/chromedriver"
PROFILE_PATH = "/content/chrome-profile"

!chmod +x $CHROMEDRIVER_PATH

# === Bersihkan file lock profile === #
lock_files = ["SingletonLock", "SingletonCookie", "SingletonSocket"]
for lf in lock_files:
    lf_path = os.path.join(PROFILE_PATH, lf)
    if os.path.exists(lf_path):
        try:
            os.remove(lf_path)
            print(f"✅ Menghapus lock file: {lf}")
        except Exception as e:
            print(f"⚠️ Gagal hapus {lf}: {e}")

# === Chrome options === #
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={PROFILE_PATH}")
chrome_options.add_argument("--profile-directory=Default")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# ==== Fungsi util ==== #
def normal_click(driver, xpath, desc="", wait_s=20):
    try:
        el = WebDriverWait(driver, wait_s).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        el.click()
        print(f"✅ Klik {desc}")
    except Exception as e:
        print(f"⚠️ Gagal klik {desc}: {e}")

def dismiss_overlays(driver, max_clicks=3):
    for _ in range(max_clicks):
        try:
            close_btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'✕') or contains(.,'Close')]"))
            )
            close_btn.click()
            print("✅ Overlay dismissed")
        except:
            break

screenshot_path = "/content/screenshot.png"

# @markdown Pilih Suara (contoh: "Yukiko")
CHOOSE_VOICE_TEXT = "Yukiko" # @param {type:"string"}

try:
    # === Eksekusi langkah === #
    driver.get("https://www.capcut.com/ai-creator/storyboard/")
    print("🌍 Membuka halaman CapCut...")

    ###########################
    # Klik tombol Decline all #
    ###########################

    # Ambil semua button di shadowRoot
    buttons = driver.execute_script("""
        let banner = document.querySelector('tiktok-cookie-banner');
        if (banner && banner.shadowRoot) {
            return Array.from(banner.shadowRoot.querySelectorAll("button"));
        }
        return [];
    """)

    for btn in buttons:
        text = btn.text
        print("Button:", text)
        if "Decline" in text:
            btn.click()
            print("Clicked:", text)
            break

    #################
    # Klik "Script" #
    #################

    normal_click(driver, "//div[normalize-space(text())='Script']", "menu 'Script'")

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    #############
    # Isi Topic #
    #############

    # @markdown Masukkan Judul Video
    TOPIC_TEXT = "Spurs win AGAIN at the Etihad | Man City 0-2 Tottenham Hotspur | Premier League Highlights - 1.5M views"  # @param {type:"string"}
    print(f"✅ Menggunakan Topic input: {TOPIC_TEXT}")

    topic_inputs = driver.find_elements(
        By.XPATH,
        "//input[@placeholder='Enter a topic']"
        " | //textarea[@placeholder='Enter a topic']"
        " | //div[@placeholder='Enter a topic']"
    )

    if not topic_inputs:
        raise Exception("❌ Tidak menemukan field topic.")

    topic_input = topic_inputs[0]
    driver.execute_script("arguments[0].click();", topic_input)

    if topic_input.tag_name.lower() in ["input", "textarea"]:
        driver.execute_script("arguments[0].value = '';", topic_input)
        topic_input.send_keys(TOPIC_TEXT)
    else:
        driver.execute_script("arguments[0].innerText = '';", topic_input)
        driver.execute_script("arguments[0].innerText = arguments[1];", topic_input, TOPIC_TEXT)

    print("✅ Isi Topic tanpa dobel")


    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    dismiss_overlays(driver, max_clicks=4)

    ##################
    # Isi Key Points #
    ##################

    # @markdown Masukkan Link / Key Points
    KEYPOINTS_TEXT = "https://www.youtube.com/watch?v=dM6CiY2Ux1k"  # @param {type:"string"}
    print(f"✅ Menggunakan Key Points input: {KEYPOINTS_TEXT}")

    # Variabel tambahan sesuai permintaan
    KEYPOINTS_TEXT_ADD = f"{KEYPOINTS_TEXT} . Gunakan bahasa Indonesia, dan buat konten semenarik mungkin."
    print(f"✅ Key Points final (dengan tambahan): {KEYPOINTS_TEXT_ADD}")

    # 1) Isi clipboard X11 dengan URL (dibutuhkan agar Ctrl+V benar2 mem-paste)
    try:
        p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
        p.communicate(input=KEYPOINTS_TEXT_ADD.encode("utf-8"))
        if p.returncode != 0:
            raise RuntimeError("xclip gagal set clipboard")
        print("📋 Clipboard di-set via xclip")
    except Exception as e:
        print(f"⚠️ Gagal set clipboard X11: {e}")

    # 2) Temukan elemen contenteditable yang benar (bukan <p> ‘biasa’)
    #    Banyak editor menaruh caret di DIV contenteditable, bukan <p>.
    keypoints_editable = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((
            By.XPATH,
            # cari editor di area Key Points; sesuaikan bila perlu
            "//*[@id='ai-creator']//div[@contenteditable='true']"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", keypoints_editable)
    keypoints_editable.click()
    driver.execute_script("arguments[0].focus();", keypoints_editable)

    # 3) Bersihkan dulu isi lama (select-all + delete) agar tidak dobel
    ActionChains(driver)\
        .key_down(Keys.CONTROL)\
        .send_keys('a')\
        .key_up(Keys.CONTROL)\
        .send_keys(Keys.DELETE)\
        .perform()

    # 4) Lakukan “paste” asli dari clipboard (ini yang memicu handler paste editor)
    ActionChains(driver)\
        .key_down(Keys.CONTROL)\
        .send_keys('v')\
        .key_up(Keys.CONTROL)\
        .perform()

    # 5) Beberapa editor baru membentuk “chip” setelah spasi/Enter atau blur
    time.sleep(0.3)
    keypoints_editable.send_keys(Keys.SPACE)  # atau Keys.ENTER
    # driver.execute_script("arguments[0].blur();", keypoints_editable)  # alternatif: paksa blur

    print("✅ Isi Key Points dengan Ctrl+V (paste event)")

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    #########################
    # Pilih durasi 10 menit #
    #########################

    normal_click(driver,
        '//*[@id="ai-creator"]/div/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[4]/div[1]/div[2]/div[4]',
        "durasi 10 menit"
    )

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    #############
    # Klik Buat #
    #############

    normal_click(driver,
        '//*[@id="ai-creator"]/div/div[2]/div[1]/div[2]/div[1]/div/div[3]/div/button',
        "tombol 'Buat'", wait_s=60
    )

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    USE_BTN = '//*[@id="ai-creator"]/div/div[2]/div[2]/div[1]/div[1]/div[2]/div/div[5]/div/div/div/div[3]/div[3]/button'
    SCENES_BTN = "//div[normalize-space()='Scenes']"
    VOICE_BTN = "//div[normalize-space()='Voice']"
    #CHOOSE_VOICE_BTN = "//div[normalize-space()='Yukiko']" # Diubah untuk menggunakan variabel CHOOSE_VOICE_TEXT
    APPLY_ALL_BTN = '//*[@id="ai-creator"]/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/button'
    MEDIA = "//div[normalize-space()='Media']"

    WebDriverWait(driver, 6000).until(
        EC.element_to_be_clickable((By.XPATH, USE_BTN))
    )

    normal_click(driver, USE_BTN, "tombol 'Use'", wait_s=10)
    time.sleep(1.2)
    dismiss_overlays(driver, max_clicks=6)

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    normal_click(driver, SCENES_BTN, "'Scenes'")
    time.sleep(1.0)

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    normal_click(driver, VOICE_BTN, "'Voice'")
    time.sleep(1.0)

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    # Klik tombol suara berdasarkan input dari form Colab
    CHOOSE_VOICE_BTN_XPATH = f"//div[normalize-space()='{CHOOSE_VOICE_TEXT}']"
    normal_click(driver, CHOOSE_VOICE_BTN_XPATH, f"'{CHOOSE_VOICE_TEXT}'")
    time.sleep(1.0)

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    normal_click(driver, APPLY_ALL_BTN, "'Apply to all scenes'")
    time.sleep(1.5)

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    normal_click(driver, MEDIA, "'Media'")
    time.sleep(5.0)

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    ##############################
    # Tunggu loading mask hilang #
    ##############################

    LOADING_MASK = '//*[@id="ai-creator"]/div/div[2]/div[2]/div[2]/div/div[1]/div[1]'
    try:
        WebDriverWait(driver, 6000).until(
            EC.invisibility_of_element_located((By.XPATH, LOADING_MASK))
        )
        print("✅ Loading selesai, tombol 'Match' siap")
    except:
        print("⚠️ Timeout: Loading mask masih ada")

    #####################################################
    # Klik tombol Match via text (loop sampai berhasil) #
    #####################################################

    while True:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='Match']"))
            )
            el.click()
            print("✅ Klik 'Match' via text")
            break
        except:
            print("⏳ Tombol 'Match' belum siap, coba lagi...")
            time.sleep(2)

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    ##############################
    # Tunggu loading mask hilang #
    ##############################

    LOADING_MASK = '//*[@id="ai-creator"]/div/div[2]/div[2]/div[2]/div/div[1]/div[1]'
    try:
        WebDriverWait(driver, 60000).until(
            EC.invisibility_of_element_located((By.XPATH, LOADING_MASK))
        )
        print("✅ Loading selesai, siap export")
    except:
        print("⚠️ Timeout: Loading mask masih ada sebelum export")

    ##############################
    # Klik tombol Export pertama #
    ##############################

    EXPORT_BTN = '//*[@id="ai-creator"]/div/div[1]/div[3]/div[1]/div/div[2]/div/button'
    try:
        el = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, EXPORT_BTN))
        )
        el.click()
        print("✅ Klik tombol 'Export' pertama")
    except Exception as e:
        print(f"⚠️ Gagal klik 'Export' pertama: {e}")

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    ####################################
    # Klik tombol Export kedua (popup) #
    ####################################

    try:
        export_btns = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[normalize-space()='Export']"))
        )
        export_btns[-1].click()   # klik export yang terakhir (di popup kanan)
        print("✅ Klik tombol 'Export' kedua (popup)")
    except Exception as e:
            print(f"⚠️ Gagal klik 'Export' kedua: {e}")

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    #############################
    # Tunggu tombol Save muncul #
    #############################

    try:
        save_btn = WebDriverWait(driver, 600).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save']"))
        )
        save_btn.click()
        print("✅ Export selesai")
    except Exception as e:
        print(f"⚠️ Gagal export.': {e}")

    driver.save_screenshot(screenshot_path)
    ipy_display(Image(filename=screenshot_path))

    time.sleep(3.0)

    ###################################
    # Menyimpan video ke Google Drive #
    ###################################

    # Gunakan teks topik dari file sebagai nama file
    source_path = f"/root/Downloads/{TOPIC_TEXT}.mp4"
    destination_dir = "/content/drive/MyDrive/CapCut_video"
    filename = os.path.basename(source_path)
    destination_path = os.path.join(destination_dir, filename)

    # Tunggu sampai file benar-benar ada dan selesai diunduh
    print("⏳ Menunggu file selesai diunduh...")
    while not os.path.exists(source_path):
        time.sleep(5)  # cek setiap 5 detik

    # Tambahan cek: pastikan file sudah tidak berubah ukuran (artinya unduhan selesai)
    prev_size = -1
    while True:
        current_size = os.path.getsize(source_path)
        if current_size == prev_size:
            break  # ukuran tidak berubah → unduhan selesai
        prev_size = current_size
        time.sleep(5)

    # Jika file dengan nama sama sudah ada, beri nomor urut
    base, ext = os.path.splitext(destination_path)
    counter = 1
    while os.path.exists(destination_path):
        destination_path = f"{base}_{counter}{ext}"
        counter += 1

    # Pindahkan file
    shutil.move(source_path, destination_path)
    print(f"✅ File berhasil dipindahkan ke {destination_path}")

except KeyboardInterrupt:
    print("⏹️ Proses dihentikan secara manual.")
    driver.quit()