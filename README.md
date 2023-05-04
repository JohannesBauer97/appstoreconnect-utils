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

* Translation is limited to languages supported by Deepl API
* Only versions with state `PREPARE_FOR_SUBMISSION` are selectable

### Requirements

Setup API Keys and Changelog in `config.ini`

### Usage

```bash
python update_changelog.py
```
