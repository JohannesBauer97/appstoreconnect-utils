import argparse
import configparser
import json
import os

import deepl
import requests
from appstoreconnect import Api


def main():
    parser = argparse.ArgumentParser(description='Automatic translation and update of changelog')
    parser.add_argument('-c', '--config', type=str, help='Path to config.ini', required=False, default='config.ini')
    args = parser.parse_args()

    # print all arguments
    print('Given arguments:')
    for arg in vars(args):
        print(arg, getattr(args, arg))

    # validate config file
    if not validate_config(args.config):
        return

    # setup APIs
    translator, app_store_connect_api = setup_apis(args.config)

    # let user select app and version
    selected_app, selected_version = get_appid_version(app_store_connect_api)

    # get all localization for selected app and version
    localizations = get_localization(app_store_connect_api.token, selected_app.id, selected_version.version)
    if localizations is None:
        return

    # get changelog and language
    changelog, changelog_language = get_changelog_and_language(args.config)
    if changelog is None:
        return

    # translate changelog
    for localization in localizations:
        translated_changelog = translate_changelog_for_localization(
            translator,
            changelog,
            changelog_language,
            localization
        )
        if translated_changelog is None:
            continue

        # update changelog
        status_code = update_changelog(
            app_store_connect_api.token,
            localization['id'],
            translated_changelog
        )
        if status_code == 200:
            print(f"Changelog for {localization['locale']} updated successfully")
        else:
            print(f"Error updating changelog for {localization['locale']}: {status_code}")


def translate_changelog_for_localization(translator, changelog, changelog_language, localization):
    """Translate changelog for a given localization

    Args:
    translator (deepl.Translator): Deepl translator
    changelog (str): Changelog text
    changelog_language (str): Changelog language
    localization (dict): AppStoreConnect localization

    Returns:
    str: Translated changelog
    """
    # get deepl language code for target language
    deepl_target_language = convert_appstore_language_code_to_deepl_language(localization['locale'])
    if deepl_target_language is None:
        print(f"Language {localization['locale']} not supported by Deepl")
        return None

    # translate changelog
    print(f"Translating changelog from {changelog_language} to {localization['locale']}...")
    translated_changelog = translator.translate_text(
        changelog,
        target_lang=deepl_target_language,
        source_lang=changelog_language
    )

    return translated_changelog.text


def update_changelog(token, app_version_localization_id, changelog_text):
    """Update changelog for a given localization

    Args:
    token (str): AppStoreConnect API token
    app_version_localization_id (str): AppStoreConnect localization id
    changelog_text (str): Changelog text

    Returns:
    int: HTTP status code
    """
    url = f"https://api.appstoreconnect.apple.com/v1/appStoreVersionLocalizations/{app_version_localization_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "data": {
            "attributes": {
                "whatsNew": changelog_text
            },
            "id": app_version_localization_id,
            "type": "appStoreVersionLocalizations"
        }
    }
    response = requests.patch(url, headers=headers, data=json.dumps(data))
    return response.status_code


def convert_appstore_language_code_to_deepl_language(language_code):
    """Convert AppStore language code to Deepl language code

    Args:
    language_code (str): AppStore language code

    Returns:
    str: Deepl language code
    """
    if language_code == "en-US":
        return deepl.Language.ENGLISH_AMERICAN
    elif language_code == "zh-Hans":
        return deepl.Language.CHINESE
    elif language_code == "cs":
        return deepl.Language.CZECH
    elif language_code == "da":
        return deepl.Language.DANISH
    elif language_code == "nl-NL":
        return deepl.Language.DUTCH
    elif language_code == "fi":
        return deepl.Language.FINNISH
    elif language_code == "fr-FR":
        return deepl.Language.FRENCH
    elif language_code == "de-DE":
        return deepl.Language.GERMAN
    elif language_code == "el":
        return deepl.Language.GREEK
    elif language_code == "hu":
        return deepl.Language.HUNGARIAN
    elif language_code == "id":
        return deepl.Language.INDONESIAN
    elif language_code == "it":
        return deepl.Language.ITALIAN
    elif language_code == "ja":
        return deepl.Language.JAPANESE
    elif language_code == "pl":
        return deepl.Language.POLISH
    elif language_code == "pt-PT":
        return deepl.Language.PORTUGUESE_EUROPEAN
    elif language_code == "ro":
        return deepl.Language.ROMANIAN
    elif language_code == "ru":
        return deepl.Language.RUSSIAN
    elif language_code == "sk":
        return deepl.Language.SLOVAK
    elif language_code == "es-ES":
        return deepl.Language.SPANISH
    elif language_code == "sv":
        return deepl.Language.SWEDISH
    elif language_code == "tr":
        return deepl.Language.TURKISH
    elif language_code == "uk":
        return deepl.Language.UKRAINIAN
    else:
        return None


def get_changelog_and_language(config_file_path):
    """Get changelog and language from user

    Args:
    config_file_path (str): Path to config.ini

    Returns:
    str, str: Changelog and language
    """
    config = configparser.ConfigParser()
    config.read(config_file_path)
    changelog_path = config['Changelog']['changelog_path']
    changelog_language = config['Changelog']['changelog_language']

    # read changelog
    with open(changelog_path, 'r') as f:
        changelog = f.read()

    # print changelog and language
    print("=== Changelog ===")
    print(f"Changelog source language: {changelog_language}")
    print(changelog)

    # ask user to continue
    if input("Continue? (y/n): ") != "y":
        return None, None

    return changelog, changelog_language


def get_localization(token, app_id, app_version):
    """Get localization for a given app and version

    Args:
    token (str): AppStoreConnect API token
    app_id (str): App ID
    app_version (str): App version

    Returns:
    list: List of localization ids
    """
    print("=== App Store Version Localizations ===")
    localizations = get_all_localization_ids(token, app_id, app_version)
    print("Following localizations will be updated:")
    for localization in localizations:
        print(f"{localization['locale']} ", end=" ")

    # ask user to continue
    if input("Continue? (y/n): ") != "y":
        return None

    return localizations


def get_all_localization_ids(token, app_id, app_version):
    """Get all localization ids for a given app and version

    Args:
    token (str): AppStoreConnect API token
    app_id (str): App ID
    app_version (str): App version

    Returns:
    list: List of localization ids
    """
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{app_id}/appStoreVersions?filter[versionString]={app_version}&include=appStoreVersionLocalizations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    localization_ids = []

    if response.status_code == 200:
        data = json.loads(response.text)
        for included_item in data["included"]:
            if included_item["type"] == "appStoreVersionLocalizations":
                localization_ids.append({
                    "id": included_item["id"],
                    "locale": included_item["attributes"]["locale"]
                })

    return localization_ids


def get_appid_version(app_store_connect_api):
    """Get app and version from user

    Args:
    app_store_connect_api (appstoreconnect.Api): AppStoreConnect API

    Returns:
    appstoreconnect.App, appstoreconnect.Version: Selected app and version
    """
    print("=== Apps ===")
    apps = app_store_connect_api.list_apps()

    if len(apps) == 0:
        print("No apps found")
        return None

    for i, app in enumerate(apps):
        print(f"{i}: {app.name}")
    selected_app = apps[int(input("Select app: "))]
    print(f"Selected app: {selected_app.name}")

    print("=== Versions ===")
    versions = app_store_connect_api.list_prerelease_versions(selected_app.id)

    if len(versions) == 0:
        print("No prerelease versions found")
        return None

    for i, version in enumerate(versions):
        print(f"{i}: {version.version} - {version.platform}")
    selected_version = versions[int(input("Select version: "))]
    print(f"Selected version: {selected_version.version} - {selected_version.platform}")

    return selected_app, selected_version


def setup_apis(config_file_path):
    """Setup APIs

    Args:
    config_file_path (str): Path to config.ini

    Returns:
    deepl.Translator: Deepl API
    appstoreconnect.Api: AppStoreConnect API
    """

    # setup Deepl API
    config = configparser.ConfigParser()
    config.read(config_file_path)
    deepl_auth_key = config['Deepl']['auth_key']
    translator = deepl.Translator(deepl_auth_key)

    # setup AppStoreConnect API
    app_store_connect_key_id = config['AppStoreConnect']['key_id']
    app_store_connect_key_file_path = config['AppStoreConnect']['key_file_path']
    app_store_connect_issuer_id = config['AppStoreConnect']['issuer_id']
    app_store_connect_api = Api(app_store_connect_key_id, app_store_connect_key_file_path, app_store_connect_issuer_id,
                                submit_stats=False)

    return translator, app_store_connect_api


def validate_config(config_file_path):
    """Validate config file

    Args:
    config_file_path (str): Path to config.ini
    """

    # check if config file exists
    if not os.path.isfile(config_file_path):
        print('Config file does not exist')
        return False

    # check if config file is readable
    if not os.access(config_file_path, os.R_OK):
        print('Config file is not readable')
        return False

    # check if config.ini contains all required sections
    required_sections = ['Deepl', 'AppStoreConnect', 'Changelog']
    config = configparser.ConfigParser()
    config.read(config_file_path)
    for section in required_sections:
        if section not in config:
            print('Config file does not contain section ' + section)
            return False

    # check if config.ini contains all required keys
    required_keys = {
        'Deepl': ['auth_key'],
        'AppStoreConnect': ['key_id', 'key_file_path', 'issuer_id'],
        'Changelog': ['changelog_path', 'changelog_language']
    }
    for section in required_keys:
        for key in required_keys[section]:
            if key not in config[section]:
                print('Config file does not contain key ' + key + ' in section ' + section)
                return False

    # check if changelog_path exists
    changelog_path = config['Changelog']['changelog_path']
    if not os.path.isfile(changelog_path):
        print('Changelog file does not exist')
        return False

    return True


if __name__ == '__main__':
    main()
