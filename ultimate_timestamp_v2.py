import customtkinter as ctk
import requests
import threading
import json
import os
import sys
import webbrowser
import urllib3
import pyperclip
import pytz
from datetime import datetime, timedelta, timezone
from tkinter import filedialog, messagebox

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- КОНФИГУРАЦИЯ ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Ссылка на GitHub для обновлений 
GITHUB_REPO_URL = "https://api.github.com/repos/USER_NAME/REPO_NAME/releases/latest"
CURRENT_VERSION = "2.0.0"

# --- ЛОКАЦИИ НА РАЗНЫХ ЯЗЫКАХ (Коды стран для гарантии отображения) ---
LOCATIONS = {
    "en": {
        "RU Russia": {
            "Kaliningrad": "Europe/Kaliningrad", "Moscow / St. Petersburg": "Europe/Moscow",
            "Samara": "Europe/Samara", "Yekaterinburg": "Asia/Yekaterinburg",
            "Omsk": "Asia/Omsk", "Krasnoyarsk": "Asia/Krasnoyarsk",
            "Irkutsk": "Asia/Irkutsk", "Yakutsk": "Asia/Yakutsk",
            "Vladivostok": "Asia/Vladivostok", "Magadan": "Asia/Magadan",
            "Kamchatka": "Asia/Kamchatka"
        },
        "IN India": {"New Delhi": "Asia/Kolkata", "Mumbai": "Asia/Kolkata"},
        "KZ Kazakhstan": {"Astana": "Asia/Almaty", "Almaty": "Asia/Almaty"},
        "KG Kyrgyzstan": {"Bishkek": "Asia/Bishkek", "Osh": "Asia/Bishkek"},
        "UZ Uzbekistan": {"Tashkent": "Asia/Tashkent", "Samarkand": "Asia/Samarkand"},
        "AZ Azerbaijan": {"Baku": "Asia/Baku", "Ganja": "Asia/Baku"},
        "NP Nepal": {"Kathmandu": "Asia/Kathmandu", "Pokhara": "Asia/Kathmandu"},
        "PK Pakistan": {"Karachi": "Asia/Karachi", "Lahore": "Asia/Karachi"},
        "LK Sri Lanka": {"Colombo": "Asia/Colombo", "Kandy": "Asia/Colombo"},
        "MA Morocco": {"Casablanca": "Africa/Casablanca", "Rabat": "Africa/Casablanca"},
        "EG Egypt": {"Cairo": "Africa/Cairo", "Alexandria": "Africa/Cairo"},
        "BD Bangladesh": {"Dhaka": "Asia/Dhaka", "Chittagong": "Asia/Dhaka"},
        "CZ Czech Republic": {"Prague": "Europe/Prague", "Brno": "Europe/Prague"},
        "PL Poland": {"Warsaw": "Europe/Warsaw", "Krakow": "Europe/Warsaw"}
    },
    "ru": {
        "RU Россия": {
            "Калининград": "Europe/Kaliningrad", "Москва / СПб": "Europe/Moscow",
            "Самара": "Europe/Samara", "Екатеринбург": "Asia/Yekaterinburg",
            "Омск": "Asia/Omsk", "Красноярск": "Asia/Krasnoyarsk",
            "Иркутск": "Asia/Irkutsk", "Якутск": "Asia/Yakutsk",
            "Владивосток": "Asia/Vladivostok", "Магадан": "Asia/Magadan",
            "Камчатка": "Asia/Kamchatka"
        },
        "IN Индия": {"Нью-Дели": "Asia/Kolkata", "Мумбаи": "Asia/Kolkata"},
        "KZ Казахстан": {"Астана": "Asia/Almaty", "Алматы": "Asia/Almaty"},
        "KG Кыргызстан": {"Бишкек": "Asia/Bishkek", "Ош": "Asia/Bishkek"},
        "UZ Узбекистан": {"Ташкент": "Asia/Tashkent", "Самарканд": "Asia/Samarkand"},
        "AZ Азербайджан": {"Баку": "Asia/Baku", "Гянджа": "Asia/Baku"},
        "NP Непал": {"Катманду": "Asia/Kathmandu", "Покхара": "Asia/Kathmandu"},
        "PK Пакистан": {"Карачи": "Asia/Karachi", "Лахор": "Asia/Karachi"},
        "LK Шри-Ланка": {"Коломбо": "Asia/Colombo", "Канди": "Asia/Colombo"},
        "MA Марокко": {"Касабланка": "Africa/Casablanca", "Рабат": "Africa/Casablanca"},
        "EG Египет": {"Каир": "Africa/Cairo", "Александрия": "Africa/Cairo"},
        "BD Бангладеш": {"Дакка": "Asia/Dhaka", "Читтагонг": "Asia/Dhaka"},
        "CZ Чехия": {"Прага": "Europe/Prague", "Брно": "Europe/Prague"},
        "PL Польша": {"Варшава": "Europe/Warsaw", "Краков": "Europe/Warsaw"}
    }
}

# --- СЛОВАРИ ПЕРЕВОДА ИНТЕРФЕЙСА ---
LANGS = {
    "en": {
        "title": "Global Time & Timestamp Utility",
        "tab_time": "🌍 Current Time",
        "tab_date": "📅 Date Converter",
        "tab_settings": "⚙️ Settings",
        "tab_docs": "📖 Documentation",
        "select_loc": "Select Location:",
        "fav_btn": "⭐ Add to Favs",
        "fav_added": "⭐ In Favorites",
        "no_fav": "No pinned cities. Select a location and click «⭐ Add to Favs».",
        "msk_time": "MSK",
        "local_time": "Local",
        "status": "Status",
        "diff": "Diff to MSK",
        "format": "Format",
        "copy_btn": "📋 Copy",
        "copied": "✅ Copied!",
        "sync_btn": "🌐 Sync Time",
        "syncing": "⏳ Syncing...",
        "synced": "🌐 Synced ✓",
        "sync_error": "❌ Network Error",
        "net_status_pc": "Network Status: PC Time",
        "net_status_syncing": "Network Status: Connecting...",
        "net_status_ok": "Network Status: ✓ Online Time",
        "net_status_offline": "Network Status: ⚠ Using PC Time",
        "retry_sync": "🌐 Retry Sync",
        "convert_date": "Arbitrary Date Converter",
        "date_label": "Date (DD.MM.YYYY):",
        "time_label": "Time (HH:MM):",
        "src_label": "Source City:",
        "calc_btn": "🔄 Calculate",
        "res_source": "Source",
        "res_msk": "In Moscow",
        "settings_title": "App Settings",
        "theme_label": "🎨 Appearance:",
        "theme_dark": "🌙 Dark",
        "theme_light": "☀️ Light",
        "reset_btn": "🔄 Reset Settings",
        "export_btn": "💾 Export Settings",
        "import_btn": "📂 Import Settings",
        "check_update_btn": "🔄 Check Updates",
        "update_title": "Update Check",
        "update_latest": "You have the latest version ({})",
        "update_available": "New version {} available!\nGo to download page?",
        "update_error": "Check error: {}",
        "lang_label": "🌐 Language / Язык:",
        "doc_title": "DOCUMENTATION",
        "day_status_work": "Work Hours 🟢",
        "day_status_morning": "Morning/Evening 🟡",
        "day_status_night": "Night 🔴",
        "day_status_weekend": "Weekend 🟠",
        "error_input": "Input Error",
        "error_input_msg": "Check format: Date (DD.MM.YYYY) and Time (HH:MM)",
        "error_copy": "Error",
        "reset_confirm": "Reset all settings?",
        "export_success": "Settings exported!",
        "import_success": "Settings imported! Restart recommended.",
        "footer_text": "v" + CURRENT_VERSION + " | Created by @m.mosqueen | ",
        "telegram_link": "✈️ Telegram"
    },
    "ru": {
        "title": "Global Time & Timestamp Utility",
        "tab_time": "🌍 Текущее время",
        "tab_date": "📅 Конвертер даты",
        "tab_settings": "⚙️ Настройки",
        "tab_docs": "📖 Документация",
        "select_loc": "Выберите локацию:",
        "fav_btn": "⭐ В избранное",
        "fav_added": "⭐ В избранном",
        "no_fav": "Нет закрепленных городов. Выберите локацию и нажмите «⭐ В избранное».",
        "msk_time": "МСК",
        "local_time": "Местное",
        "status": "Статус",
        "diff": "Разница к МСК",
        "format": "Формат",
        "copy_btn": "📋 Копировать",
        "copied": "✅ Скопировано!",
        "sync_btn": "🌐 Синхронизировать время",
        "syncing": "⏳ Синхронизация...",
        "synced": "🌐 Синхронизировано ✓",
        "sync_error": "❌ Ошибка сети",
        "net_status_pc": "Статус сети: Время ПК",
        "net_status_syncing": "Статус сети: Подключение...",
        "net_status_ok": "Статус сети: ✓ Актуальное время (Интернет)",
        "net_status_offline": "Статус сети: ⚠ Используется время ПК",
        "retry_sync": "🌐 Повторить синхронизацию",
        "convert_date": "Конвертер произвольной даты",
        "date_label": "Дата (ДД.ММ.ГГГГ):",
        "time_label": "Время (ЧЧ:ММ):",
        "src_label": "Город источника:",
        "calc_btn": "🔄 Рассчитать",
        "res_source": "Источник",
        "res_msk": "В Москве",
        "settings_title": "Настройки приложения",
        "theme_label": "🎨 Тема оформления:",
        "theme_dark": "🌙 Тёмная",
        "theme_light": "☀️ Светлая",
        "reset_btn": "🔄 Сбросить настройки",
        "export_btn": "💾 Экспорт настроек",
        "import_btn": "📂 Импорт настроек",
        "check_update_btn": "🔄 Проверить обновления",
        "update_title": "Проверка обновлений",
        "update_latest": "У вас установлена последняя версия ({})",
        "update_available": "Доступна новая версия {}!\nПерейти на страницу загрузки?",
        "update_error": "Ошибка проверки: {}",
        "lang_label": "🌐 Language / Язык:",
        "doc_title": "ДОКУМЕНТАЦИЯ",
        "day_status_work": "Рабочее время 🟢",
        "day_status_morning": "Утро/Вечер 🟡",
        "day_status_night": "Ночь 🔴",
        "day_status_weekend": "Выходной 🟠",
        "error_input": "Ошибка ввода",
        "error_input_msg": "Проверьте формат: Дата (ДД.ММ.ГГГГ) и Время (ЧЧ:ММ)",
        "error_copy": "Ошибка",
        "reset_confirm": "Сбросить все настройки?",
        "export_success": "Настройки экспортированы!",
        "import_success": "Настройки импортированы! Рекомендуется перезапуск.",
        "footer_text": "v" + CURRENT_VERSION + " | Создано @m.mosqueen | ",
        "telegram_link": "✈️ Telegram"
    }
}

TIME_FORMATS = {
    "ДД.ММ.ГГГГ ЧЧ:ММ:СС": "%d.%m.%Y %H:%M:%S",
    "ДД.ММ.ГГГГ ЧЧ:ММ": "%d.%m.%Y %H:%M",
    "ISO 8601": "%Y-%m-%dT%H:%M:%S",
    "Unix Timestamp": "unix",
    "12h Format (AM/PM)": "%d.%m.%Y %I:%M:%S %p",
    "Только время (24h)": "%H:%M:%S",
    "Только дата": "%d.%m.%Y"
}

class UltimateTimestampApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.files_dir = os.path.dirname(os.path.abspath(__file__))
        self.favorites_file = os.path.join(self.files_dir, "favorites.json")
        self.settings_file = os.path.join(self.files_dir, "settings.json")
        
        # Состояние
        self.network_utc_offset = timedelta(0)
        self.is_network_synced = False
        self.sync_in_progress = False
        self.sync_completed = False
        self.favorites = []
        self.fav_time_labels = {}
        self.current_tz_str = "Europe/Moscow"
        self.combo_list = []
        self.tz_map = {}
        self.locations_db = {}

        # Загрузка настроек
        self._load_settings()
        
        # Инициализация локаций
        self._update_locations()
        
        self.title(self.t("title"))
        self.geometry("760x850")
        self.resizable(False, False)

        self._build_ui()
        
        # Инициализация значений
        default_key = list(self.combo_list)[0] if self.combo_list else ""
        if default_key:
            self.combo_var.set(default_key)
            self.current_tz_str = self.tz_map[default_key]
        
        self.format_var.set("ДД.ММ.ГГГГ ЧЧ:ММ:СС")
        self._refresh_favorites_ui()
        
        # Горячие клавиши
        self.bind("<Control-Key-c>", lambda e: self._copy_timestamp())
        self.bind("<Control-Key-s>", lambda e: self._sync_time_background(force=True))
        self.bind("<Control-Key-t>", lambda e: self._toggle_theme())
        self.bind("<Control-Key-d>", lambda e: self.tabview.set(self.t("tab_docs")))

        self.after(1000, self._sync_time_background)
        self._update_loop()

    def t(self, key):
        """Помощник для перевода"""
        return LANGS.get(self.lang, LANGS["en"]).get(key, key)

    def _update_locations(self):
        """Обновление списка локаций при смене языка"""
        self.locations_db = LOCATIONS.get(self.lang, LOCATIONS["ru"])
        self.combo_list = []
        self.tz_map = {}
        
        for country, cities in self.locations_db.items():
            for city, tz in cities.items():
                label = f"{country} — {city}"
                self.combo_list.append(label)
                self.tz_map[label] = tz

    def _load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.lang = data.get("lang", "en")
                    theme = data.get("theme", "Dark")
                    ctk.set_appearance_mode(theme)
                    self.favorites = data.get("favorites", [])
            except Exception:
                self.lang = "en"
        else:
            self.lang = "en"

    def _save_settings(self):
        try:
            data = {
                "lang": self.lang,
                "theme": ctk.get_appearance_mode(),
                "favorites": self.favorites
            }
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self, width=730, height=740)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tab_current = self.tabview.add(self.t("tab_time"))
        self.tab_converter = self.tabview.add(self.t("tab_date"))
        self.tab_settings = self.tabview.add(self.t("tab_settings"))
        self.tab_docs = self.tabview.add(self.t("tab_docs"))
        
        self._build_current_tab()
        self._build_converter_tab()
        self._build_settings_tab()
        self._build_docs_tab()

    def _build_current_tab(self):
        header = ctk.CTkFrame(self.tab_current, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(header, text=self.t("select_loc"), anchor="w", width=130).pack(side="left", padx=(0, 5))
        self.combo_var = ctk.StringVar()
        self.combo = ctk.CTkComboBox(header, values=self.combo_list, variable=self.combo_var,
                                     command=self._on_location_change, width=380, font=("Segoe UI", 11))
        self.combo.pack(side="left", fill="x", expand=True)
        self.btn_fav = ctk.CTkButton(header, text=self.t("fav_btn"), width=130, 
                                     command=self._toggle_favorite, fg_color="#FFC107", text_color="#000")
        self.btn_fav.pack(side="left", padx=(10, 0))

        self.fav_scroll = ctk.CTkScrollableFrame(self.tab_current, height=80, fg_color="transparent")
        self.fav_scroll.pack(fill="x", padx=20, pady=(5, 10))
        self.fav_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        self.frame_display = ctk.CTkFrame(self.tab_current, fg_color="#2b2b2b", corner_radius=10)
        self.frame_display.pack(padx=20, fill="x")
        
        self.lbl_msk = ctk.CTkLabel(self.frame_display, text=f"{self.t('msk_time')}: --:--:--", 
                                   font=("Consolas", 18, "bold"), text_color="#4CAF50")
        self.lbl_msk.pack(pady=8)
        self.lbl_local = ctk.CTkLabel(self.frame_display, text=f"{self.t('local_time')}: --:--:--", 
                                     font=("Consolas", 18, "bold"), text_color="#2196F3")
        self.lbl_local.pack(pady=4)
        
        self.scale_frame = ctk.CTkFrame(self.frame_display, fg_color="transparent")
        self.scale_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(self.scale_frame, text="-12h", font=("Segoe UI", 9), text_color="gray").pack(side="left")
        self.diff_bar = ctk.CTkProgressBar(self.scale_frame, mode="determinate", progress_color="#4CAF50")
        self.diff_bar.pack(side="left", fill="x", expand=True, padx=5)
        self.diff_bar.set(0.5)
        ctk.CTkLabel(self.scale_frame, text="+12h", font=("Segoe UI", 9), text_color="gray").pack(side="right")

        self.lbl_status_day = ctk.CTkLabel(self.frame_display, text=f"{self.t('status')}: --", 
                                          font=("Segoe UI", 12, "bold"))
        self.lbl_status_day.pack(pady=4)
        self.lbl_diff = ctk.CTkLabel(self.frame_display, text=f"{self.t('diff')}: --", 
                                    font=("Segoe UI", 11), text_color="gray")
        self.lbl_diff.pack(pady=6)

        frame_copy = ctk.CTkFrame(self.tab_current, fg_color="transparent")
        frame_copy.pack(pady=12)
        ctk.CTkLabel(frame_copy, text=self.t("format"), font=("Segoe UI", 11)).grid(row=0, column=0, padx=(0, 5))
        self.format_var = ctk.StringVar(value="ДД.ММ.ГГГГ ЧЧ:ММ:СС")
        ctk.CTkComboBox(frame_copy, values=list(TIME_FORMATS.keys()), variable=self.format_var, 
                       width=170, font=("Segoe UI", 11)).grid(row=0, column=1, padx=5)
        self.btn_copy = ctk.CTkButton(frame_copy, text=self.t("copy_btn"), command=self._copy_timestamp, width=150)
        self.btn_copy.grid(row=0, column=2, padx=5)

        self.btn_sync = ctk.CTkButton(self.tab_current, text=self.t("sync_btn"), 
                                     command=self._sync_time_background, width=220, fg_color="#FF9800")
        self.btn_sync.pack(pady=10)
        self.lbl_net_status = ctk.CTkLabel(self.tab_current, text=self.t("net_status_pc"), 
                                          font=("Segoe UI", 11), text_color="gray")
        self.lbl_net_status.pack(pady=5)
        
        # === ФУТЕР С TELEGRAM И ВЕРСИЕЙ (ТОЛЬКО ВО ВКЛАДКЕ "ТЕКУЩЕЕ ВРЕМЯ") ===
        footer_frame = ctk.CTkFrame(self.tab_current, fg_color="#1a1a1a", height=50)
        footer_frame.pack(side="bottom", fill="x", padx=0, pady=0)
        
        footer_content = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_content.pack(expand=True, fill="both", padx=10, pady=5)
        
        ctk.CTkLabel(footer_content, text=self.t("footer_text"), 
                    font=("Segoe UI", 10), text_color="#666").pack(side="left")
        
        btn_telegram = ctk.CTkButton(footer_content, text=self.t("telegram_link"),
                                    width=120, height=28,
                                    font=("Segoe UI", 10),
                                    fg_color="#2AABEE",
                                    hover_color="#229ED9",
                                    command=lambda: webbrowser.open("https://t.me/m_mosqueen"))
        btn_telegram.pack(side="right")

    def _build_converter_tab(self):
        ctk.CTkLabel(self.tab_converter, text=self.t("convert_date"), 
                    font=("Segoe UI", 17, "bold")).pack(pady=15)
        frame_input = ctk.CTkFrame(self.tab_converter, fg_color="transparent")
        frame_input.pack(pady=10)
        ctk.CTkLabel(frame_input, text=self.t("date_label")).grid(row=0, column=0, padx=5, sticky="e")
        self.entry_date = ctk.CTkEntry(frame_input, width=120)
        self.entry_date.grid(row=0, column=1, padx=5)
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        ctk.CTkLabel(frame_input, text=self.t("time_label")).grid(row=0, column=2, padx=5, sticky="e")
        self.entry_time = ctk.CTkEntry(frame_input, width=100)
        self.entry_time.grid(row=0, column=3, padx=5)
        self.entry_time.insert(0, datetime.now().strftime("%H:%M"))
        ctk.CTkLabel(frame_input, text=self.t("src_label")).grid(row=1, column=0, padx=5, pady=(10,0), sticky="e")
        self.conv_combo_var = ctk.StringVar(value=list(self.combo_list)[0] if self.combo_list else "")
        ctk.CTkComboBox(frame_input, values=self.combo_list, variable=self.conv_combo_var, 
                       width=220).grid(row=1, column=1, columnspan=3, padx=5, pady=(10,0), sticky="w")
        ctk.CTkButton(self.tab_converter, text=self.t("calc_btn"), command=self._calculate_conversion, 
                     width=200).pack(pady=15)
        self.frame_result = ctk.CTkFrame(self.tab_converter, fg_color="#2b2b2b", corner_radius=8)
        self.frame_result.pack(padx=20, fill="x", expand=True)
        self.lbl_res_source = ctk.CTkLabel(self.frame_result, text=f"{self.t('res_source')}: --", 
                                          font=("Consolas", 14), text_color="#FF9800")
        self.lbl_res_source.pack(pady=8)
        self.lbl_res_msk = ctk.CTkLabel(self.frame_result, text=f"{self.t('res_msk')}: --", 
                                       font=("Consolas", 14), text_color="#4CAF50")
        self.lbl_res_msk.pack(pady=8)

    def _build_settings_tab(self):
        ctk.CTkLabel(self.tab_settings, text=self.t("settings_title"), 
                    font=("Segoe UI", 17, "bold")).pack(pady=15)
        settings_frame = ctk.CTkFrame(self.tab_settings, fg_color="#2b2b2b", corner_radius=10)
        settings_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(settings_frame, text=self.t("lang_label"), 
                    font=("Segoe UI", 13)).pack(padx=15, pady=(15, 5), anchor="w")
        self.lang_var = ctk.StringVar(value=self.lang)
        lang_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        lang_frame.pack(padx=15, pady=5, fill="x")
        ctk.CTkRadioButton(lang_frame, text="🇷🇺 Русский", variable=self.lang_var, 
                          value="ru", command=self._change_lang).pack(side="left", padx=10)
        ctk.CTkRadioButton(lang_frame, text="🇬🇧 English", variable=self.lang_var, 
                          value="en", command=self._change_lang).pack(side="left", padx=10)

        ctk.CTkFrame(settings_frame, height=2, fg_color="gray").pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(settings_frame, text=self.t("theme_label"), 
                    font=("Segoe UI", 13)).pack(padx=15, pady=(5, 5), anchor="w")
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        theme_frame.pack(padx=15, pady=5, fill="x")
        ctk.CTkRadioButton(theme_frame, text=self.t("theme_dark"), variable=self.theme_var, 
                          value="Dark", command=self._change_theme).pack(side="left", padx=10)
        ctk.CTkRadioButton(theme_frame, text=self.t("theme_light"), variable=self.theme_var, 
                          value="Light", command=self._change_theme).pack(side="left", padx=10)

        ctk.CTkFrame(settings_frame, height=2, fg_color="gray").pack(fill="x", padx=15, pady=10)
        
        file_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        file_frame.pack(padx=15, pady=5, fill="x")
        ctk.CTkButton(file_frame, text=self.t("export_btn"), command=self._export_settings, 
                     width=150).pack(side="left", padx=10)
        ctk.CTkButton(file_frame, text=self.t("import_btn"), command=self._import_settings, 
                     width=150).pack(side="left", padx=10)

        ctk.CTkFrame(settings_frame, height=2, fg_color="gray").pack(fill="x", padx=15, pady=10)
        
        ctk.CTkButton(settings_frame, text=self.t("check_update_btn"), command=self._check_update, 
                     width=200).pack(pady=10)
        
        ctk.CTkFrame(settings_frame, height=2, fg_color="gray").pack(fill="x", padx=15, pady=10)
        
        ctk.CTkButton(settings_frame, text=self.t("reset_btn"), command=self._reset_settings, 
                     width=200, fg_color="#F44336").pack(pady=15)

    def _build_docs_tab(self):
        docs_textbox = ctk.CTkTextbox(self.tab_docs, wrap="word", state="disabled", 
                                     font=("Segoe UI", 12), fg_color="#2b2b2b")
        docs_textbox.pack(padx=15, pady=15, fill="both", expand=True)
        
        if self.lang == "en":
            content = f"""
{self.t('doc_title')} v{CURRENT_VERSION}

🔹 1. INTERFACE & HOTKEYS
- Ctrl+C: Copy time
- Ctrl+S: Sync time
- Ctrl+T: Toggle Theme
- Ctrl+D: Open Docs

🔹 2. SETTINGS & EXPORT
- Use "Export Settings" to save your favorites and theme to a file.
- Use "Import Settings" to restore them on another PC.
- Language switcher changes UI instantly.

🔹 3. UPDATES
- Click "Check Updates" to compare your version with the GitHub release.
- Works in both Python script and compiled .exe.

🔹 4. VISUAL SCALE
- The bar under the time shows timezone difference from Moscow.
- Left (Red) = Behind MSK, Right (Green) = Ahead of MSK.

🔹 5. FAQ
- Time stuck? Check internet or click Sync.
- SSL Error? The app has auto-fix built-in.
            """
        else:
            content = f"""
{self.t('doc_title')} v{CURRENT_VERSION}

🔹 1. ИНТЕРФЕЙС И ГОРЯЧИЕ КЛАВИШИ
- Ctrl+C: Копировать время
- Ctrl+S: Синхронизация
- Ctrl+T: Смена темы
- Ctrl+D: Открыть документацию

🔹 2. НАСТРОЙКИ И ЭКСПОРТ
- Используйте "Экспорт настроек" для сохранения избранного и темы.
- Используйте "Импорт настроек" для восстановления на другом ПК.
- Переключатель языка меняет интерфейс мгновенно.

🔹 3. ОБНОВЛЕНИЯ
- Нажмите "Проверить обновления" для сравнения с версией на GitHub.
- Работает как в Python скрипте, так и в скомпилированном .exe.

🔹 4. ВИЗУАЛЬНАЯ ШКАЛА
- Полоса под временем показывает разницу часовых поясов от Москвы.
- Слева (Красный) = Отстаёт от МСК, Справа (Зелёный) = Опережает МСК.

🔹 5. FAQ
- Время не обновляется? Проверьте интернет или нажмите Синхронизация.
- Ошибка SSL? В приложении есть авто-исправление.
            """
        
        docs_textbox.configure(state="normal")
        docs_textbox.insert("0.0", content.strip())
        docs_textbox.configure(state="disabled")

    # === ЛОГИКА ===

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new = "Light" if current == "Dark" else "Dark"
        self.theme_var.set(new)
        self._change_theme()

    def _change_theme(self):
        theme = self.theme_var.get()
        self.attributes("-alpha", 0.8)
        self.update()
        ctk.set_appearance_mode(theme)
        self.after(100, lambda: self.attributes("-alpha", 1.0))
        self._save_settings()

    def _change_lang(self):
        new_lang = self.lang_var.get()
        if new_lang != self.lang:
            self.lang = new_lang
            self._rebuild_ui()

    def _rebuild_ui(self):
        current_tz = self.current_tz_str
        current_format = self.format_var.get()
        
        # Обновляем локации для нового языка
        self._update_locations()
        
        # Сохраняем текущий выбранный часовой пояс
        new_default = list(self.combo_list)[0] if self.combo_list else ""
        for label, tz in self.tz_map.items():
            if tz == current_tz:
                new_default = label
                break
        
        for widget in self.winfo_children():
            widget.destroy()
        
        self.title(self.t("title"))
        self._build_ui()
        
        self.combo_var.set(new_default)
        self.current_tz_str = self.tz_map.get(new_default, "Europe/Moscow")
        self.format_var.set(current_format)
        
        if hasattr(self, 'conv_combo_var'):
            self.conv_combo_var.set(new_default)
        
        self._refresh_favorites_ui()
        
        if self.is_network_synced:
            self.lbl_net_status.configure(text=self.t("net_status_ok"))
        else:
            self.lbl_net_status.configure(text=self.t("net_status_pc"))
        
        self._save_settings()

    def _refresh_favorites_ui(self):
        for widget in self.fav_scroll.winfo_children(): 
            widget.destroy()
        self.fav_time_labels.clear()
        
        if not self.favorites:
            ctk.CTkLabel(self.fav_scroll, text=self.t("no_fav"), 
                        text_color="gray", font=("Segoe UI", 10)).pack(pady=15)
            return
        
        row, col = 0, 0
        for key in self.favorites:
            if key not in self.tz_map: 
                continue
            
            card = ctk.CTkFrame(self.fav_scroll, fg_color="#333333", corner_radius=8)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card.bind("<Button-1>", lambda e, k=key: self._on_favorite_click(k))
            
            # Формат отображения: Город (Код Страна)
            parts = key.split(" — ")
            if len(parts) == 2:
                country_code = parts[0].split()[0]  # RU, IN, KZ...
                country_name = parts[0].split(maxsplit=1)[1] if len(parts[0].split()) > 1 else parts[0]
                city = parts[1]
                display_text = f"{city} ({country_code} {country_name})"
            else:
                display_text = key
            
            ctk.CTkLabel(card, text=display_text, 
                        font=("Segoe UI", 10, "bold"), text_color="#fff").pack(pady=(4, 0))
            
            lbl = ctk.CTkLabel(card, text="--:--:--", font=("Consolas", 14), text_color="#2196F3")
            lbl.pack(pady=(2, 4))
            lbl.bind("<Button-1>", lambda e, k=key: self._on_favorite_click(k))
            self.fav_time_labels[key] = lbl
            
            ctk.CTkButton(card, text="✕", width=20, height=20, 
                         command=lambda k=key: self._remove_favorite(k), 
                         fg_color="#F44336").place(relx=0.9, rely=0.5, anchor="center")
            
            col += 1
            if col > 2: 
                col, row = 0, row + 1
        
        self.btn_fav.configure(
            text=self.t("fav_btn") if self.combo_var.get() not in self.favorites else self.t("fav_added"),
            fg_color="#FFC107" if self.combo_var.get() not in self.favorites else "#4CAF50"
        )

    def _toggle_favorite(self):
        current = self.combo_var.get()
        if current in self.favorites:
            self.favorites.remove(current)
            self.btn_fav.configure(text=self.t("fav_btn"), fg_color="#FFC107")
        else:
            self.favorites.append(current)
            self.btn_fav.configure(text=self.t("fav_added"), fg_color="#4CAF50")
        self._save_settings()
        self._refresh_favorites_ui()

    def _remove_favorite(self, key):
        if key in self.favorites:
            self.favorites.remove(key)
            self._save_settings()
            self._refresh_favorites_ui()

    def _on_favorite_click(self, key):
        self.combo_var.set(key)
        self.current_tz_str = self.tz_map[key]
        self._update_display()

    def _on_location_change(self, choice):
        if choice in self.tz_map:
            self.current_tz_str = self.tz_map[choice]
            self._update_display()

    def _get_accurate_utc_now(self):
        if self.is_network_synced:
            return datetime.now(timezone.utc) + self.network_utc_offset
        return datetime.now(timezone.utc)

    def _get_timezone(self, tz_name):
        try: 
            return pytz.timezone(tz_name)
        except: 
            return pytz.UTC

    def _update_display(self):
        try:
            utc_now = self._get_accurate_utc_now()
            msk_tz = self._get_timezone("Europe/Moscow")
            target_tz = self._get_timezone(self.current_tz_str)
            
            msk_time = utc_now.astimezone(msk_tz)
            target_time = utc_now.astimezone(target_tz)

            self.lbl_msk.configure(text=f"{self.t('msk_time')}: {msk_time.strftime('%d.%m.%Y %H:%M:%S')}")
            self.lbl_local.configure(text=f"{self.t('local_time')}: {target_time.strftime('%d.%m.%Y %H:%M:%S')}")
            
            h, w = target_time.hour, target_time.weekday()
            if w >= 5: 
                txt, col = self.t("day_status_weekend"), "#FF9800"
            elif 9 <= h < 18: 
                txt, col = self.t("day_status_work"), "#4CAF50"
            elif 6 <= h < 9 or 18 <= h < 23: 
                txt, col = self.t("day_status_morning"), "#FFEB3B"
            else: 
                txt, col = self.t("day_status_night"), "#F44336"
            
            self.lbl_status_day.configure(text=f"{self.t('status')}: {txt}", text_color=col)

            diff_sec = (target_time.utcoffset() - msk_time.utcoffset()).total_seconds()
            sign = "+" if diff_sec >= 0 else "-"
            hh, mm = divmod(int(abs(diff_sec)) // 60, 60)
            self.lbl_diff.configure(text=f"{self.t('diff')}: {sign}{hh}ч {mm}м")
            
            diff_hours = diff_sec / 3600
            progress = (diff_hours + 12) / 24
            self.diff_bar.set(max(0.0, min(1.0, progress)))
            self.diff_bar.configure(progress_color="#4CAF50" if diff_sec >= 0 else "#F44336")

            for key, tz_name in self.tz_map.items():
                if key in self.fav_time_labels:
                    dt = utc_now.astimezone(self._get_timezone(tz_name))
                    self.fav_time_labels[key].configure(text=dt.strftime("%H:%M:%S"))
        except Exception as e: 
            print(e)

    def _update_loop(self):
        self._update_display()
        self.after(1000, self._update_loop)

    def _copy_timestamp(self):
        try:
            utc_now = self._get_accurate_utc_now()
            target_tz = self._get_timezone(self.current_tz_str)
            target_time = utc_now.astimezone(target_tz)
            fmt = TIME_FORMATS[self.format_var.get()]
            txt = str(int(target_time.timestamp())) if fmt == "unix" else target_time.strftime(fmt)
            pyperclip.copy(txt)
            old = self.btn_copy.cget("text")
            self.btn_copy.configure(text=self.t("copied"), fg_color="#4CAF50")
            self.after(1500, lambda: self.btn_copy.configure(text=self.t("copy_btn"), fg_color="#1f6aa5"))
        except Exception as e:
            messagebox.showerror(self.t("error_copy"), str(e))

    def _calculate_conversion(self):
        try:
            dt = datetime.strptime(f"{self.entry_date.get()} {self.entry_time.get()}", "%d.%m.%Y %H:%M")
            src_tz = self._get_timezone(self.tz_map[self.conv_combo_var.get()])
            dt_src = src_tz.localize(dt)
            dt_msk = dt_src.astimezone(self._get_timezone("Europe/Moscow"))
            self.lbl_res_source.configure(text=f"{self.t('res_source')}: {dt_src.strftime('%d.%m.%Y %H:%M:%S')}")
            self.lbl_res_msk.configure(text=f"{self.t('res_msk')}: {dt_msk.strftime('%d.%m.%Y %H:%M:%S')}")
        except:
            messagebox.showerror(self.t("error_input"), self.t("error_input_msg"))

    def _sync_time_background(self, force=False):
        if self.sync_in_progress or (self.sync_completed and not force): 
            return
        self.sync_in_progress = True
        self.sync_completed = False
        self.btn_sync.configure(state="disabled", text=self.t("syncing"), fg_color="#FF9800")
        self.lbl_net_status.configure(text=self.t("net_status_syncing"), text_color="orange")

        def fetch():
            headers = {"User-Agent": "TimestampApp/2.0"}
            apis = [
                ("https://timeapi.io/api/time/current/zone?timeZone=UTC", "timeapi"),
                ("https://worldtimeapi.org/api/timezone/Etc/UTC", "world")
            ]
            for url, src in apis:
                try:
                    r = requests.get(url, timeout=6, headers=headers)
                    r.raise_for_status()
                    if src == "timeapi":
                        api_utc = datetime.fromisoformat(r.json()["dateTime"])
                    else:
                        api_utc = datetime.fromisoformat(r.json()["datetime"].replace('Z', '+00:00'))
                    
                    pc_utc = datetime.now(timezone.utc)
                    self.network_utc_offset = api_utc.replace(tzinfo=None) - pc_utc.replace(tzinfo=None)
                    self.is_network_synced = True
                    self.after(0, self._on_sync_success)
                    return
                except requests.exceptions.SSLError:
                    try:
                        r = requests.get(url, timeout=6, headers=headers, verify=False)
                        r.raise_for_status()
                        if src == "timeapi": 
                            api_utc = datetime.fromisoformat(r.json()["dateTime"])
                        else: 
                            api_utc = datetime.fromisoformat(r.json()["datetime"].replace('Z', '+00:00'))
                        pc_utc = datetime.now(timezone.utc)
                        self.network_utc_offset = api_utc.replace(tzinfo=None) - pc_utc.replace(tzinfo=None)
                        self.is_network_synced = True
                        self.after(0, self._on_sync_success)
                        return
                    except: 
                        continue
                except: 
                    continue
            
            self.after(0, lambda: self._on_sync_error("No response"))

        threading.Thread(target=fetch, daemon=True).start()

    def _on_sync_success(self):
        self.btn_sync.configure(state="normal", text=self.t("synced"), fg_color="#4CAF50")
        self.lbl_net_status.configure(text=self.t("net_status_ok"), text_color="#4CAF50")
        self.sync_in_progress = False
        self.sync_completed = True
        self.after(3000, lambda: self.btn_sync.configure(text=self.t("sync_btn"), fg_color="#FF9800"))
        
    def _on_sync_error(self, err):
        self.btn_sync.configure(state="normal", text=self.t("sync_error"), fg_color="#F44336")
        self.lbl_net_status.configure(text=self.t("net_status_offline"), text_color="#F44336")
        self.is_network_synced = False
        self.sync_in_progress = False
        self.after(2000, lambda: self.btn_sync.configure(text=self.t("retry_sync"), fg_color="#FF9800"))

    def _reset_settings(self):
        if messagebox.askyesno("Reset", self.t("reset_confirm")):
            self.lang = "en"
            self.lang_var.set("en")
            self.favorites = []
            ctk.set_appearance_mode("Dark")
            self.theme_var.set("Dark")
            self._save_settings()
            self._rebuild_ui()

    def _export_settings(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", 
                                           filetypes=[("JSON", "*.json")])
        if path:
            self._save_settings()
            import shutil
            shutil.copy(self.settings_file, path)
            messagebox.showinfo("Export", self.t("export_success"))

    def _import_settings(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.lang = data.get("lang", "en")
                self.favorites = data.get("favorites", [])
                ctk.set_appearance_mode(data.get("theme", "Dark"))
                self._save_settings()
                self.lang_var.set(self.lang)
                self.theme_var.set(ctk.get_appearance_mode())
                self._rebuild_ui()
                messagebox.showinfo("Import", self.t("import_success"))
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _check_update(self):
        self.btn_sync.configure(text="Checking...", state="disabled")
        def check():
            try:
                # Временно используем публичный репозиторий для теста. 
                # Замени на свою ссылку GITHUB_REPO_URL когда создашь репо
                test_url = "https://api.github.com/repos/psf/requests/releases/latest"
                r = requests.get(test_url, timeout=5)
                data = r.json()
                latest = data.get("tag_name", "0.0.0").replace("v", "")
                
                if latest > CURRENT_VERSION:
                    self.after(0, lambda: self._show_update_dialog(latest, data.get("html_url")))
                else:
                    self.after(0, lambda: messagebox.showinfo(
                        self.t("update_title"), 
                        self.t("update_latest").format(CURRENT_VERSION)
                    ))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Error", 
                    self.t("update_error").format(str(e))
                ))
            finally:
                self.after(0, lambda: self.btn_sync.configure(
                    text=self.t("sync_btn"), 
                    state="normal"
                ))
        
        threading.Thread(target=check, daemon=True).start()

    def _show_update_dialog(self, version, url):
        if messagebox.askyesno(self.t("update_title"), 
                              self.t("update_available").format(version)):
            webbrowser.open(url)

if __name__ == "__main__":
    app = UltimateTimestampApp()
    app.mainloop()