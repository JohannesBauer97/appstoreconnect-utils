# Appstoreconnect Utils

Python scripts to automate Appstoreconnect tasks

## Installation

```bash
git clone https://github.com/JohannesBauer97/appstoreconnect-utils
cd appstoreconnect-utils
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Automatic changelog translation

Using [Deepl API](https://www.deepl.com/docs-api) to translate the changelog of your app to multiple languages.

![Demo Video](https://user-images.githubusercontent.com/15695124/236224757-e8ad5934-cf02-4908-a8e0-1541621a6201.gif)

### Limitations

* Only versions with state `PREPARE_FOR_SUBMISSION` are selectable

<details>
  <summary>Click to see supported languages</summary>

```
BULGARIAN = "bg"
CZECH = "cs"
DANISH = "da"
GERMAN = "de"
GREEK = "el"
ENGLISH = "en"  # Only usable as a source language
ENGLISH_BRITISH = "en-GB"  # Only usable as a target language
ENGLISH_AMERICAN = "en-US"  # Only usable as a target language
SPANISH = "es"
ESTONIAN = "et"
FINNISH = "fi"
FRENCH = "fr"
HUNGARIAN = "hu"
INDONESIAN = "id"
ITALIAN = "it"
JAPANESE = "ja"
KOREAN = "ko"
LITHUANIAN = "lt"
LATVIAN = "lv"
NORWEGIAN = "nb"
DUTCH = "nl"
POLISH = "pl"
PORTUGUESE = "pt"  # Only usable as a source language
PORTUGUESE_BRAZILIAN = "pt-BR"  # Only usable as a target language
PORTUGUESE_EUROPEAN = "pt-PT"  # Only usable as a target language
ROMANIAN = "ro"
RUSSIAN = "ru"
SLOVAK = "sk"
SLOVENIAN = "sl"
SWEDISH = "sv"
TURKISH = "tr"
UKRAINIAN = "uk"
CHINESE = "zh"
```

</details>

### Requirements

Setup API Keys and Changelog in `config.ini`

### Usage

```bash
python update_changelog.py
```
