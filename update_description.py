import argparse
import configparser
import json
import os

import deepl
import requests
from appstoreconnect import Api


def main():
    parser = argparse.ArgumentParser(description='Automatic translation and update of description')
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

    print(app_store_connect_api.token)

    # let user select app and version
    selected_app, selected_version = get_appid_version(app_store_connect_api)

    # get all localizations for selected version
    localizations = get_localization(app_store_connect_api.token, selected_version["id"])
    if localizations is None:
        return

    # get description and language
    description, description_language = get_description_and_language(args.config)
    if description is None:
        return

    # translate description
    for localization in localizations:
        translated_description = translate_description_for_localization(
            translator,
            description,
            description_language,
            localization
        )
        if translated_description is None:
            continue

        # update description
        status_code = update_description(
            app_store_connect_api.token,
            localization['id'],
            translated_description
        )
        if status_code == 200:
            print(f"Description for {localization['locale']} updated successfully")
        else:
            print(f"Error updating description for {localization['locale']}: {status_code}")


def translate_description_for_localization(translator, description, description_language, localization):
    """Translate description for a given localization

    Args:
    translator (deepl.Translator): Deepl translator
    description (str): Description text
    description_language (str): Description language
    localization (dict): AppStoreConnect localization

    Returns:
    str: Translated description
    """
    # get deepl language code for target language
    deepl_target_language = convert_appstore_language_code_to_deepl_language(localization['locale'])
    if deepl_target_language is None:
        print(f"Language {localization['locale']} not supported by Deepl")
        return None

    # translate description
    print(f"Translating description from {description_language} to {localization['locale']}...")
    translated_description = translator.translate_text(
        description,
        target_lang=deepl_target_language,
        source_lang=description_language
    )

    return translated_description.text


def update_description(token, app_version_localization_id, description_text):
    """Update description for a given localization

    Args:
    token (str): AppStoreConnect API token
    app_version_localization_id (str): AppStoreConnect localization id
    description_text (str): description text

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
                "description": description_text
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
    elif language_code == "en-GB":
        return deepl.Language.ENGLISH_BRITISH
    elif language_code == "et":
        return deepl.Language.ESTONIAN
    elif language_code == "ko":
        return deepl.Language.KOREAN
    elif language_code == "lt":
        return deepl.Language.LITHUANIAN
    elif language_code == "lv":
        return deepl.Language.LATVIAN
    elif language_code == "nb":
        return deepl.Language.NORWEGIAN
    elif language_code == "pt-BR":
        return deepl.Language.PORTUGUESE_BRAZILIAN
    elif language_code == "sl":
        return deepl.Language.SLOVENIAN
    else:
        return None


def get_description_and_language(config_file_path):
    """Get description and language

    Args:
    config_file_path (str): Path to config.ini

    Returns:
    str, str: Description and language
    """
    config = configparser.ConfigParser()
    config.read(config_file_path)
    description_path = config['Description']['description_path']
    description_language = config['Description']['description_language']

    # read description
    with open(description_path, 'r') as f:
        description = f.read()

    # print description and language
    print("=== Description ===")
    print(f"Description source language: {description_language}")
    print(description)

    # ask user to continue
    if input("Continue? (y/n): ") != "y":
        return None, None

    return description, description_language


def get_localization(token, version_id):
    """Get localization from user

    Args:
    token (str): AppStoreConnect API token
    version_id (str): AppStoreConnect version id

    Returns:
    dict: AppStoreConnect localization
    """
    print("=== App Store Version Localizations ===")
    localizations = get_all_localization_ids(token, version_id)
    print("Following localizations will be updated:")
    for localization in localizations:
        print(f"{localization['locale']} ", end=" ")

    # ask user to continue
    if input("Continue? (y/n): ") != "y":
        return None

    return localizations


def get_all_localization_ids(token, version_id):
    """Get all localization ids for a given version

    Args:
    token (str): AppStoreConnect API token
    version_id (str): AppStoreConnect version id

    Returns:
    list: List of localization ids
    """
    url = f"https://api.appstoreconnect.apple.com/v1/appStoreVersions/{version_id}/appStoreVersionLocalizations" \
          f"?limit=200"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    localizations = []

    if response.status_code == 200:
        data = json.loads(response.text)
        for localization in data["data"]:
            if localization["type"] == "appStoreVersionLocalizations":
                localizations.append({
                    "id": localization["id"],
                    "locale": localization["attributes"]["locale"]
                })

    return localizations


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
    versions = get_prerelease_versions(app_store_connect_api.token, selected_app.id)

    if len(versions) == 0:
        print("No prerelease versions found")
        return None

    for i, version in enumerate(versions):
        print(f"{i}: {version['versionString']} - {version['platform']}")
    selected_version = versions[int(input("Select version: "))]
    print(f"Selected version: {selected_version['versionString']} - {selected_version['platform']}")

    return selected_app, selected_version


def get_prerelease_versions(token, appid):
    """Get all prerelease versions

    Args:
    token (str): AppStoreConnect API token
    appid (str): App ID

    Returns:
    list: List of prerelease versions
    """
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{appid}/appStoreVersions?limit=200&filter[appStoreState]=PREPARE_FOR_SUBMISSION"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    versions = []

    if response.status_code == 200:
        data = json.loads(response.text)
        for version in data["data"]:
            if version["type"] == "appStoreVersions":
                versions.append({
                    "id": version["id"],
                    "platform": version["attributes"]["platform"],
                    "versionString": version["attributes"]["versionString"],
                })

    return versions


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
    required_sections = ['Deepl', 'AppStoreConnect', 'Description']
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
        'Description': ['description_path', 'description_language']
    }
    for section in required_keys:
        for key in required_keys[section]:
            if key not in config[section]:
                print('Config file does not contain key ' + key + ' in section ' + section)
                return False

    # check if description_path exists
    description_path = config['Description']['description_path']
    if not os.path.isfile(description_path):
        print('Description file does not exist')
        return False

    return True


if __name__ == '__main__':
    main()
