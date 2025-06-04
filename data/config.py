import configparser
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

import i18n
import yaml

from app.utils.logger import error

locales_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
i18n.load_path.append(locales_path)
i18n.set('filename_format', '{locale}.{format}')
i18n.set('file_format', 'yml')
i18n.set('skip_locale_root_data', True)
i18n.set('fallback', 'en')
i18n.set('available_locales', ['en', 'ru'])

LANGUAGE_INFO = {
    'en': {'display': 'English', 'code': 'EN-US'},
    'ru': {'display': 'Русский', 'code': 'RU-RU'},
}


def t(key: str, **kwargs) -> str:
    locale = kwargs.pop('locale', i18n.get('locale'))
    return i18n.t(key, locale=locale, **kwargs)


def get_language_display(locale: str) -> str:
    return LANGUAGE_INFO.get(locale.lower(), {}).get('display', locale)


def get_language_code(locale: str) -> str:
    return LANGUAGE_INFO.get(locale.lower(), {}).get('code', locale.upper())


def get_all_translations(locale: str) -> Dict[str, Any]:
    file_path = os.path.join(locales_path, f"{locale.lower()}.yml")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}


class Config:
    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read('config.ini')
        self.SESSION = str(Path(__file__).parent.parent / "data/account")
        self.DATA_FILEPATH = Path(__file__).parent / "json/history.json"
        self.API_ID = self.config_parser.getint('Telegram', 'API_ID', fallback=0)
        self.API_HASH = self.config_parser.get('Telegram', 'API_HASH', fallback='')
        self.PHONE_NUMBER = self.config_parser.get('Telegram', 'PHONE_NUMBER', fallback='')
        self.CHANNEL_ID = self.config_parser.getint('Telegram', 'CHANNEL_ID', fallback=0)
        self.INTERVAL = self.config_parser.getfloat('Bot', 'INTERVAL', fallback=10.0)
        self.TIMEZONE = self.config_parser.get('Bot', 'TIMEZONE', fallback='UTC')
        self.LANGUAGE = self.config_parser.get('Bot', 'LANGUAGE', fallback='EN').lower()
        self.LANGUAGE_DISPLAY = get_language_display(self.LANGUAGE)
        self.LANGUAGE_CODE = get_language_code(self.LANGUAGE)
        self.USER_ID = self._parse_user_ids()
        self.MIN_GIFT_PRICE = self.config_parser.getint('Gifts', 'MIN_GIFT_PRICE', fallback=100000)
        self.MAX_GIFT_PRICE = self.config_parser.getint('Gifts', 'MAX_GIFT_PRICE', fallback=100000)
        self.EXCLUDED_GIFTS_IDS = self._parse_excluded_gifts_ids()
        self.GIFT_QUANTITY = self.config_parser.getint('Gifts', 'GIFT_QUANTITY', fallback=1)
        self.PURCHASE_NON_LIMITED_GIFTS = self.config_parser.getboolean('Gifts', 'PURCHASE_NON_LIMITED_GIFTS',
                                                                        fallback=False)
        self.PURCHASE_ONLY_UPGRADABLE_GIFTS = self.config_parser.getboolean('Gifts', 'PURCHASE_ONLY_UPGRADABLE_GIFTS',
                                                                            fallback=False)

        i18n.set('locale', self.LANGUAGE.lower())

        self._validate_config()

    def _parse_user_ids(self) -> List:
        user_ids = []
        for user_id in self.config_parser.get('Gifts', 'USER_ID', fallback='').split(','):
            user_id = user_id.strip()
            if user_id:
                try:
                    user_ids.append(int(user_id))
                except ValueError:
                    user_ids.append(user_id)
        return user_ids
    
    def _parse_excluded_gifts_ids(self) -> List:
        excluded_gifts_ids = []
        for excluded_gifts_id in self.config_parser.get('Gifts', 'EXCLUDED_GIFTS_IDS', fallback='').split(','):
            excluded_gifts_id = excluded_gifts_id.strip()
            if excluded_gifts_id:
                try:
                    excluded_gifts_ids.append(int(excluded_gifts_id))
                except ValueError:
                    excluded_gifts_ids.append(excluded_gifts_id)
        return excluded_gifts_ids
    
    def _validate_config(self) -> None:
        validation_rules = {
            "Telegram > API_ID": lambda: self.API_ID == 0,
            "Telegram > API_HASH": lambda: not self.API_HASH,
            "Telegram > PHONE_NUMBER": lambda: not self.PHONE_NUMBER,
            "Gifts > USER_ID": lambda: not self.USER_ID,
            "Gifts > MIN_GIFT_PRICE (must be >= 0)": lambda: self.MIN_GIFT_PRICE < 0,
            "Gifts > MAX_GIFT_PRICE (must be > 0)": lambda: self.MAX_GIFT_PRICE <= 0,
            "Gifts > GIFT_QUANTITY (must be > 0)": lambda: self.GIFT_QUANTITY <= 0,
        }

        missing_fields = [field for field, validator in validation_rules.items() if validator()]

        if missing_fields:
            error_message = t("errors.missing_config").format(
                '\n'.join(f'- {field}' for field in missing_fields)
            )
            error(error_message)
            sys.exit(1)


config = Config()
