#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hadees Website — Image Downloader & Packager
=============================================
Downloads all 109 product/brand photos straight from Baly's CDN, saves
each one under the exact English filename that index.html already
expects (see the MENU_ITEMS array and the image manifest comment at
the bottom of the HTML file), then zips everything into
hadees-images.zip ready to unzip next to index.html.

Why this runs on YOUR machine instead of being done automatically:
the sandbox this assistant runs code in can only reach a short
allow-list of developer/package domains (npm, pypi, github, ...) —
it cannot reach food.baly.iq or app.food.baly.iq at all. Your own
computer has normal internet access, so this script does in a few
seconds what the sandbox physically cannot.

USAGE
-----
    python app.py

Requirements: Python 3.6+ only. Every module used (urllib, zipfile,
os, time) ships with Python itself — nothing to pip install.
If Pillow (PIL) happens to be installed, the script will also make
sure logo.png is a *real* PNG; if not, it still works fine (browsers
render an image correctly regardless of its file extension).

OUTPUT
------
    ./images/*.jpg|png|webp|jpeg   (109 files)
    ./hadees-images.zip           (the same 109 files, zipped under images/)

Unzip hadees-images.zip (or just keep the images/ folder) directly
next to index.html and every photo on the site will load locally —
no more dependency on Baly's servers.
"""

import os
import sys
import time
import zipfile
import urllib.request
import urllib.error

# (target filename, source URL on Baly's CDN)
IMAGES = [
    ("logo.png",                  "https://food.baly.iq/wp-content/uploads/sites/4/baly-vendors/2228/logo.jpg"),
    ("hero-box.jpg",               "https://app.food.baly.iq/content/8gzVOz5JV04ifbLghqCSJjpg"),

    # العروض
    ("offer-giants-bucket.png",      "https://app.food.baly.iq/content/ujPWNkcf5QK-qf73J4JiWpng"),
    ("offer-fried-party-meal.png",   "https://app.food.baly.iq/content/Aap58YPtLXOVuq57Vo6EDpng"),
    ("offer-illogical.png",          "https://app.food.baly.iq/content/LomNUyRCZJLye87OKPyXHpng"),
    ("offer-king.jpeg",              "https://app.food.baly.iq/content/9lqOMSEOIvxH6KGX0W_AXjpeg"),
    ("offer-cinema-bucket.png",      "https://app.food.baly.iq/content/x0icM7f501KhTeOf8f3wxpng"),
    ("offer-cheese-burger-combo.png","https://app.food.baly.iq/content/NRSGThgPvLBCX1NmTPR0Vpng"),
    ("offer-twister-box.jpg",        "https://app.food.baly.iq/content/NcPq-uwRb0kETxYa3_mhBjpg"),
    ("offer-yalla-deluxe.png",       "https://app.food.baly.iq/content/ywQGlhPhzGVMq5-E6Jdmcpng"),
    ("offer-fried-chicken-combo.png","https://app.food.baly.iq/content/CrDzinjPY11g-biyfPw1Lpng"),
    ("offer-triple-mini-fried.png",  "https://app.food.baly.iq/content/4IIBni-1eD94YIUe1cj6Wpng"),
    ("offer-tabasco-fillet.png",     "https://app.food.baly.iq/content/BJczVtZRarpv2wutfdUyGpng"),
    ("offer-hotdog-combo.png",       "https://app.food.baly.iq/content/2X5F6GD8k7FbQ8m5fq9nFpng"),
    ("offer-crispy-wings.png",       "https://app.food.baly.iq/content/vxNl5ZRr_Akf9JLEyVVIqpng"),
    # بوكسات هاديز
    ("mini-hadees-box.png",          "https://app.food.baly.iq/content/P8AjbGdYzmX2yvXc5oU6Vpng"),
    ("les-max-box.jpg",              "https://app.food.baly.iq/content/r-568_6WPPmNphBLAxudajpg"),
    ("hadees-box.png",               "https://app.food.baly.iq/content/FBG3w1URzGr7gKgxea3jPpng"),
    ("jeetos-box.jpg",               "https://app.food.baly.iq/content/8gzVOz5JV04ifbLghqCSJjpg"),
    ("doritos-box.jpg",              "https://app.food.baly.iq/content/pKGSzBM3VvN65yOvbcKLajpg"),
    ("oman-box.jpg",                 "https://app.food.baly.iq/content/FnWh9QI3ye9Jy6i1Bb1uWjpg"),
    ("tabasco-box.jpg",              "https://app.food.baly.iq/content/TdDnCBGq_i41OH0OriSAYjpg"),
    ("salad-box.png",                "https://app.food.baly.iq/content/473Z06-qeHCvihhnz2TNJpng"),
    ("taco-box.jpg",                 "https://app.food.baly.iq/content/e5A-c0EDk1fW9LyAoVNVmjpg"),
    ("sahar-box.jpg",                "https://app.food.baly.iq/content/EHR1nbcMgyhR7o2ZQMAzVjpg"),
    # البرغر
    ("cheese-burger.jpg",            "https://app.food.baly.iq/content/zh3gvKsJ1plARBPNcS7Cpjpg"),
    ("big-hadi-chicken.jpg",         "https://app.food.baly.iq/content/muPaJjemCq2N0aP0jdnI8jpg"),
    ("big-deluxe.jpg",               "https://app.food.baly.iq/content/tGr_35xVWdwdzGGNRmwCXjpg"),
    ("big-secret.jpg",               "https://app.food.baly.iq/content/DMrfJrbITFzmG3Ibs0AiGjpg"),
    ("double-double.jpg",            "https://app.food.baly.iq/content/1OK2ypRzWWPcD6a6rlP3Sjpg"),
    ("big-hadi-meat.jpg",            "https://app.food.baly.iq/content/jTS5_kAUE3MOCzY1n12e1jpg"),
    ("swiss-mushroom.jpg",           "https://app.food.baly.iq/content/590GMQRAlY9AKswlywezGjpg"),
    ("bbq-steak.jpg",                "https://app.food.baly.iq/content/lQpIe628xA-huJUydWsRXjpg"),
    ("jalapeno-double-cheese.jpg",   "https://app.food.baly.iq/content/bhXo7N245jk3IJifqqf3Pjpg"),
    ("juicy-lucy.jpg",               "https://app.food.baly.iq/content/XWtWBphFP1ghCknpO_-R4jpg"),
    ("triple-triple.jpg",            "https://app.food.baly.iq/content/YjYybd2ScxnvxKFhWl3gbjpg"),
    ("bacon-double-cheese.jpg",      "https://app.food.baly.iq/content/NkCA0RGMMEgvJpoIL4xEfjpg"),
    ("chicken-fillet.jpg",           "https://app.food.baly.iq/content/Jz84aSX6u6nhphf12WYX7jpg"),
    ("chicken-terminator.jpg",       "https://app.food.baly.iq/content/UuatNlTQzApVkEdFZ4vHVjpg"),
    ("fried-chicken-burger.jpg",     "https://app.food.baly.iq/content/ew79YHz7YLC4lzv4pMqgxjpg"),
    # الساندويش
    ("hotdog-jeetos.jpg",            "https://app.food.baly.iq/content/T3n5ZYWXLr0yVGMei2l0vjpg"),
    ("hotdog-doritos.jpg",           "https://app.food.baly.iq/content/8A_HL765D6JGM7gEUbPBSjpg"),
    ("hotdog-lays.jpg",              "https://app.food.baly.iq/content/7mzSsx2OKHbBvyWC020hQjpg"),
    ("hotdog-oman.jpg",              "https://app.food.baly.iq/content/N-PBLcBU5N1fX4L3UL0DHjpg"),
    ("hotdog-taco.jpg",              "https://app.food.baly.iq/content/ustsuYRXh2Z2nT0kxJKfhjpg"),
    ("hotdog-crispy.jpg",            "https://app.food.baly.iq/content/yzCteiNdg7xtRR7AWRkjtjpg"),
    ("hotdog-bacon.jpg",             "https://app.food.baly.iq/content/31pgr0M4EqBonLkiz0PSljpg"),
    ("twister.jpg",                  "https://app.food.baly.iq/content/svvVt_RvVywhtFLS8laREjpg"),
    ("crunchy-twister.jpg",          "https://app.food.baly.iq/content/6cLsTDtR-LScdjPNc4u8gjpg"),
    ("zinger.jpg",                   "https://app.food.baly.iq/content/Q65QB_kaSl0NaNnD7RdoNjpg"),
    # الوجبات
    ("meat-box.jpg",                 "https://app.food.baly.iq/content/repaB9HxZgvn2GDgjRllcjpg"),
    ("secret-box-meal.jpg",          "https://app.food.baly.iq/content/5_qep0PDaovI4VJta6E6sjpg"),
    ("fillet-box.jpg",               "https://app.food.baly.iq/content/zE2h0cas22Tc6WbwB7MQQjpg"),
    ("snack-box-meal.jpg",           "https://app.food.baly.iq/content/JiJVMsN7KvRdYlIdtPgpyjpg"),
    # البيتزا
    ("pizza-tawouq.png",             "https://app.food.baly.iq/content/MAt2miV2r_EhmxzrDvkv8png"),
    ("pizza-veggie.png",             "https://app.food.baly.iq/content/4ubXAVh8MYymIGRx1vNo_png"),
    ("pizza-pepperoni.png",          "https://app.food.baly.iq/content/-GI8ILA2k-iFRY7tZ1pRjpng"),
    ("pizza-margherita.png",         "https://app.food.baly.iq/content/764iwzxKUnYKm-NRMJ7g3png"),
    ("pizza-cheese.webp",            "https://app.food.baly.iq/content/TBtXt0l7M1pnfAiFrJ6Gcwebp"),
    # وجبات الكنتاكي
    ("dinner-3.jpg",                 "https://app.food.baly.iq/content/1J30k2xnKLYmBOk3SnvvNjpg"),
    ("dinner-5.jpg",                 "https://app.food.baly.iq/content/X660cwfei1vJXZZxsbb5Hjpg"),
    ("bucket-9.jpg",                 "https://app.food.baly.iq/content/WUaHQ5rKButkdroSr9ySSjpg"),
    ("bucket-15.jpg",                "https://app.food.baly.iq/content/2NCNriji09cCjkmclzWH9jpg"),
    ("bucket-21.jpg",                "https://app.food.baly.iq/content/p8DtSXpsCEuXpiJE9M2kdjpg"),
    ("nashville.jpg",                "https://app.food.baly.iq/content/gqrychlioXtzi7fAl4KEfjpg"),
    # الستربس
    ("strips-3.jpg",                 "https://app.food.baly.iq/content/Q7z3cimDvKZKxEf8Qv2tOjpg"),
    ("strips-4.jpg",                 "https://app.food.baly.iq/content/2aN8gOaZguGr6uSR7FQ0pjpg"),
    ("strips-6.jpg",                 "https://app.food.baly.iq/content/pPzewXduA5Rf9cJ6-jAuDjpg"),
    ("strips-9.jpg",                 "https://app.food.baly.iq/content/J-yhrgmSKGC8gX5Kcewhkjpg"),
    ("strips-12.jpg",                "https://app.food.baly.iq/content/STKVmXquGqhW4ftYE-cf7jpg"),
    # الريزو
    ("rizo-strips.jpg",              "https://app.food.baly.iq/content/1e2s7cSrxiKvYJNLuXJyEjpg"),
    ("rizo-kentucky.jpg",            "https://app.food.baly.iq/content/0dxAQ4bDW7O31H_gAnkCojpg"),
    ("rizo-fried-chicken.jpg",       "https://app.food.baly.iq/content/H-DDgA9RamdONNzx3FKfrjpg"),
    ("rizo-burger.jpg",              "https://app.food.baly.iq/content/9MpHbVhA9JYwm4HUKsS7Jjpg"),
    # الأجنحة
    ("wings-buffalo.png",            "https://app.food.baly.iq/content/Qf_xI0hIRPFD9lDvZ-chbpng"),
    ("wings-bbq.png",                "https://app.food.baly.iq/content/dRU8r7S_avpvla2TKPLxHpng"),
    # فتة ورق عنب
    ("fatteh-lays.jpg",              "https://app.food.baly.iq/content/7xTlaC9IO6YDhJNz16Zftjpg"),
    ("fatteh-oman.jpg",              "https://app.food.baly.iq/content/UTO7ejCCCIFxeiImjtK4qjpg"),
    # السناك
    ("oman-secret.png",              "https://app.food.baly.iq/content/8AgH9KxLmLpg5yuFLGtTNpng"),
    ("cheese-fries.jpg",             "https://app.food.baly.iq/content/FT0Vfo8OWzHEhHFnAjMNEjpg"),
    ("secret-cheese-fries.jpg",      "https://app.food.baly.iq/content/rYeUOEJdTD11jx6HCT0Nxjpg"),
    ("jalapeno-cheese-fries.jpg",    "https://app.food.baly.iq/content/MsOW7WclAaLkH03hiED1njpg"),
    ("french-fries.jpg",             "https://app.food.baly.iq/content/HaaCg-XchVReqKuGT7Ub8jpg"),
    # المقبلات
    ("appetizer-small.png",          "https://app.food.baly.iq/content/Rq5llMx2v8JMvFmIF4gVXpng"),
    ("appetizer-medium.png",         "https://app.food.baly.iq/content/Y9Q5AHsoQPAtyMGw0zz6opng"),
    ("appetizer-large.png",          "https://app.food.baly.iq/content/6obLAP6AWCGDCFlOpBJILpng"),
    ("grape-leaves.png",             "https://app.food.baly.iq/content/eDTiF3hHfLqxRAhS5jVNLpng"),
    # الإضافات
    ("addon-cheddar.jpg",            "https://app.food.baly.iq/content/vakCH6Z0dJZqhmVwnwhEWjpg"),
    ("addon-butter-bread.jpg",       "https://app.food.baly.iq/content/VemCeC4K0QVMZ0dNUxEzLjpg"),
    ("addon-nashville-spice.jpeg",   "https://app.food.baly.iq/content/QGzEBZDzcr4lSsgSZ1QYFjpeg"),
    ("addon-secret-sauce.jpg",       "https://app.food.baly.iq/content/7gBb-81RIx41F6m9ipHrDjpg"),
    ("addon-buffalo-sauce.jpg",      "https://app.food.baly.iq/content/eow7Iada-QhLvwR1vGWeojpg"),
    ("addon-garlic-sauce.jpg",       "https://app.food.baly.iq/content/fh4e1GxuYP7tXuPlcdfm8jpg"),
    ("addon-mustard.jpg",            "https://app.food.baly.iq/content/skPordTnCPjBEAK8FxKCxjpg"),
    ("addon-spicy-ketchup.jpg",      "https://app.food.baly.iq/content/cYfi1CV8xH5RzmcbNvZIfjpg"),
    ("addon-bbq-sauce.jpg",          "https://app.food.baly.iq/content/bU-SIM1Smnt3zOo5rXkFbjpg"),
    ("addon-coleslaw.jpg",           "https://app.food.baly.iq/content/iwP573cfzEQO9Rchdl9F8jpg"),
    ("addon-jalapeno.jpg",           "https://app.food.baly.iq/content/8CWvEUNFpXsrSiatCiWOyjpg"),
    # وجبات الأطفال
    ("kids-baby-hadees.png",         "https://app.food.baly.iq/content/WNt_q05fypSEaEO2SJGqIpng"),
    ("kids-baby-rizo.png",           "https://app.food.baly.iq/content/MxEk8369V8h05vlgY6Gjtpng"),
    ("kids-cheese.png",              "https://app.food.baly.iq/content/9z5m_SWI3Y1_gfczBojHUpng"),
    ("kids-fried.png",               "https://app.food.baly.iq/content/EJIdb_S4dTUJhnv9FN8b1png"),
    # المشروبات
    ("water.jpg",                    "https://app.food.baly.iq/content/oESOFaVhuFWgZbkM2AOmRjpg"),
    ("soda.jpg",                     "https://app.food.baly.iq/content/THxY5jrdbCuYsnktEhAtQjpg"),
    ("seven-up-can.png",             "https://app.food.baly.iq/content/RYzgrsmoomYf7dYInbMLYpng"),
    ("cola-can.png",                 "https://app.food.baly.iq/content/gTvkvE33AiEI3fjWYLBI5png"),
    ("diet-can.jpg",                 "https://app.food.baly.iq/content/XDBsHrqt7xgFRg5ByDu-3jpg"),
    ("pepsi-can.jpg",                "https://app.food.baly.iq/content/dY4C_LwWxwvsCZL8b8p0ejpg"),
    ("mirinda-can.png",              "https://app.food.baly.iq/content/Q5oFabSd1D3k-6laQ8GNVjpg"),
]

OUT_DIR = "images"
ZIP_NAME = "hadees-images.zip"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def download_one(filename, url, retries=3):
    """Download a single image with retries. Returns True on success."""
    dest_path = os.path.join(OUT_DIR, filename)
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers=REQUEST_HEADERS)
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
            with open(dest_path, "wb") as out_file:
                out_file.write(data)
            size_kb = os.path.getsize(dest_path) / 1024
            print("  [OK]   {0:<28} ({1:.0f} KB)".format(filename, size_kb))
            return True
        except (urllib.error.URLError, urllib.error.HTTPError) as err:
            last_error = err
            if attempt < retries:
                time.sleep(1.5)
    print("  [FAIL] {0:<28} -> {1}".format(filename, last_error))
    return False


def ensure_logo_is_png(dest_path):
    """Best-effort: if Pillow is available, re-save logo.png as a true PNG.
    If Pillow isn't installed, we simply leave the downloaded bytes as-is —
    browsers display images correctly based on their actual content, not
    just their file extension, so nothing breaks either way."""
    try:
        from PIL import Image
    except ImportError:
        return
    try:
        img = Image.open(dest_path)
        img.save(dest_path, "PNG")
        print("  [INFO] logo.png re-encoded as a true PNG via Pillow")
    except Exception:
        pass


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Downloading {0} images into ./{1}/ ...\n".format(len(IMAGES), OUT_DIR))

    failed = []
    for filename, url in IMAGES:
        if not download_one(filename, url):
            failed.append(filename)

    logo_path = os.path.join(OUT_DIR, "logo.png")
    if os.path.exists(logo_path):
        ensure_logo_is_png(logo_path)

    print("\nPackaging into {0} ...".format(ZIP_NAME))
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, _ in IMAGES:
            file_path = os.path.join(OUT_DIR, filename)
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=os.path.join("images", filename))

    ok_count = len(IMAGES) - len(failed)
    print("\nDone: {0}/{1} images downloaded successfully.".format(ok_count, len(IMAGES)))
    if failed:
        print("These failed and need a manual look (check your internet connection and retry):")
        for name in failed:
            print("  -", name)
        sys.exit(1)
    else:
        print("All images downloaded with zero errors.")
        print("{0} is ready — unzip it next to index.html so the 'images' folder sits right beside it.".format(ZIP_NAME))


if __name__ == "__main__":
    main()