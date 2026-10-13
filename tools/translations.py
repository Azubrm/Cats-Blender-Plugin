# GPL License

# Thanks to https://www.thegrove3d.com/learn/how-to-translate-a-blender-addon/ for the idea

import os
import csv
import ssl
import bpy
import json
import urllib
import addon_utils
import requests

from .register import register_wrap
from . import settings
from . import storage


dictionary: dict[str, str] = dict()
languages = []
verbose = True
last_loaded_language = None
dictionary_download_link = "https://raw.githubusercontent.com/teamneoneko/Cats-Blender-Plugin-Unofficial-translations/4.3-translations/dictionary.json"


def _translation_messages(language):
    """Keep bundled entries when an older downloaded dictionary lacks them."""
    messages = {}
    filename = language + ".json"
    for path in (os.path.join(storage.RESOURCES_DIR, "translations", filename),
                 storage.user_file("translations", filename)):
        try:
            with open(path, encoding="utf8") as file:
                entries = json.load(file).get("messages", {})
            if isinstance(entries, dict):
                messages.update((key, value) for key, value in entries.items()
                                if isinstance(value, str) and value)
        except FileNotFoundError:
            continue
        except (OSError, ValueError, AttributeError) as error:
            print(f"Could not load Cats translations from {path}: {error}")
    return messages


def load_translations(override_language=None):
    global dictionary, languages, last_loaded_language

    dictionary = dict()
    languages = ["auto"]

    print("Loading translations")

    if override_language:
        language = override_language
        print(f"Using override language: {language}")
    else:
        language = get_language_from_settings()
        print(f"Selected language: {language}")

    # Get all current languages
    for filename in storage.resource_files("translations"):
        if filename.endswith(".json"):
            languages.append(os.path.splitext(filename)[0])
    print(f"Available languages: {languages}")

    # Normalize Blender locales (including zh_HANS) to bundled language codes.
    if not language or language == "auto":
        language = bpy.app.translations.locale
    language_to_load = convert_locale_to_language_code(language)

    # If language is not available, fallback to en_US
    if language_to_load is None:
        print(f"Language '{language}' not available, defaulting to en_US")
        language_to_load = "en_US"

    # English is a per-entry fallback, not a replacement for partial locales.
    dictionary = _translation_messages("en_US")
    if language_to_load != "en_US":
        dictionary.update(_translation_messages(language_to_load))
    last_loaded_language = language_to_load
    print(f"Loaded {len(dictionary)} translations for {language_to_load}")

    check_missing_translations()


def t(phrase: str, *args, **kwargs):
    # Translate the given phrase into Blender's current language.
    output = dictionary.get(phrase)
    if output is None:
        if verbose:
            print('Warning: Unknown phrase: ' + phrase)
        return phrase

    return output.format(*args, **kwargs)


def check_missing_translations():
    for key, value in dictionary.items():
        if not value and verbose:
            print('Translations en_US: Value missing for key: ' + key)


def get_languages_list(self, context):
    choices = []
    names = {
        "auto": t('Language.auto'),
        "en_US": "English",
        "zh_CN": "简体中文",
        "ja_JP": "日本語",
        "ko_KR": "한국어",
    }

    for language in languages:
        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        name = names.get(language, language)
        choices.append((language, name, name))

    return choices


def update_ui(self, context):
    print("update_ui function called")

    # Get the NEW language value directly from the scene property (not from file)
    # because the update callback is triggered BEFORE the settings file is saved
    current_language = context.scene.ui_lang if context and hasattr(context, 'scene') else None
    if not current_language or settings.lock_settings or settings.settings_data is None:
        return

    # Persist the selector even if "auto" resolves to the currently loaded locale.
    settings.update_settings_core(self, context)

    # Handle "auto" mode - detect from Blender locale
    if current_language and "auto" in current_language.lower():
        from bpy.app.translations import locale
        current_language = convert_locale_to_language_code(locale)
        if not current_language:
            current_language = "en_US"

    print(f"Current language from scene: {current_language}, Last loaded: {last_loaded_language}")

    if current_language != last_loaded_language:
        print(f"Language changed from {last_loaded_language} to {current_language}, reloading translations")

        load_translations(override_language=current_language)
        # Class labels are translated during import. The existing settings
        # panel shows a restart notice instead of reloading every add-on.
        if context and context.screen:
            for area in context.screen.areas:
                area.tag_redraw()
    else:
        print("Language unchanged, no reload needed")


def get_language_from_settings():
    # Load settings file
    settings_data = {}
    try:
        with open(storage.readable_resource("settings.json"), encoding="utf8") as file:
            settings_data = json.load(file)
    except FileNotFoundError:
        pass
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN SETTINGS FILE")
    if not isinstance(settings_data, dict):
        settings_data = {}

    lang = settings_data.get("ui_lang", "auto")
    if not lang or "auto" in lang.lower():
        # Auto-detect language from Blender's locale
        from bpy.app.translations import locale as current_locale
        detected_lang = convert_locale_to_language_code(current_locale)
        print(f"Auto-detecting language from Blender locale: {current_locale} -> {detected_lang}")
        return detected_lang

    return lang


def convert_locale_to_language_code(blender_locale):
    """
    Convert Blender's locale format to supported language code format.
    Blender uses formats like 'en_US', 'ja_JP', 'ko_KR', etc.
    """
    if not blender_locale:
        return None

    # Blender locale is already in the format we need (e.g., 'en_US')
    locale_str = str(blender_locale).replace('-', '_')
    if locale_str.lower() in {"zh", "zh_hans", "zh_hans_cn", "zh_sg", "zh_cn"}:
        return "zh_CN"

    # Check if exact match exists in available languages
    for lang_file in storage.resource_files("translations"):
        lang_code = lang_file.split(".")[0]
        if locale_str == lang_code:
            print(f"Found exact locale match: {lang_code}")
            return lang_code

    # Try to match by language code (first part before underscore)
    language_only = locale_str.split("_")[0].lower() if "_" in locale_str else locale_str.lower()
    for lang_file in storage.resource_files("translations"):
        lang_code = lang_file.split(".")[0]
        if lang_code.lower().startswith(language_only):
            print(f"Found language match: {lang_code}")
            return lang_code

    # Fallback to English if no match
    print(f"No language match found for locale: {locale_str}, defaulting to en_US")
    return None

# Load before operator class labels call t().
load_translations()


@register_wrap
class DownloadTranslations(bpy.types.Operator):
    bl_idname = 'cats_translations.download_latest'
    bl_label = t('DownloadTranslations.label')
    bl_description = t('DownloadTranslations.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # GitHub repository and folder information
        repo_owner = "teamneoneko"
        repo_name = "Cats-Blender-Plugin-Unofficial-translations"
        branch = "5x-translations"
        folder_path = "UI%20Tanslations"

        # Construct the API URL to get the list of files in the folder
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}?ref={branch}"

        try:
            # Send a GET request to the API URL
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception if the request was unsuccessful

            # Parse the JSON response
            files = response.json()

            # Download each translation file
            for file in files:
                if file["type"] == "file" and file["name"].endswith(".json"):
                    file_url = file["download_url"]
                    file_name = file["name"]
                    file_path = storage.user_file("translations", file_name, create=True)

                    # Download the translation file
                    file_response = requests.get(file_url)
                    file_response.raise_for_status()

                    # Save the translation file
                    with open(file_path, 'wb') as file:
                        file.write(file_response.content)

                    print(f"Downloaded: {file_name}")

        except requests.exceptions.RequestException as e:
            print("TRANSLATIONS FILES COULD NOT BE DOWNLOADED")
            self.report({'ERROR'}, t('DownloadTranslations.error.ui', error=str(e)))
            return {'CANCELLED'}

        print('TRANSLATIONS DOWNLOAD FINISHED')

        # Define the dictionary file path
        dictionary_file = storage.user_file("dictionary.json", create=True)

        # Download dictionary.json from GitHub
        print('DOWNLOAD DICTIONARY FILE')
        try:
            response = requests.get(dictionary_download_link)
            response.raise_for_status()  # Raise an exception if the request was unsuccessful
            with open(dictionary_file, 'wb') as file:
                file.write(response.content)
        except requests.exceptions.RequestException as e:
            print("DICTIONARY FILE COULD NOT BE DOWNLOADED")
            self.report({'ERROR'}, t('DownloadTranslations.error.dictionary', error=str(e)))
            return {'CANCELLED'}
        print('DICTIONARY DOWNLOAD FINISHED')

        load_translations()

        self.report({'INFO'}, t('DownloadTranslations.success'))
        return {'FINISHED'}




