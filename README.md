# Unofficial YouTube Python Client

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [Support These Projects](#support-these-projects)

## Overview

A python library that allows to manipulate the YouTube Data API to
do common channel maintenance ranging from updating descriptions, uploading
thumbnails, downloading statistics, and managing video content.

## Setup

**Setup - Requirements Install:**

For this particular project, you only need to install the dependencies, to use the project. The dependencies
are listed in the `requirements.txt` file and can be installed by running the following command:

```console
pip install -r requirements.txt
```

After running that command, the dependencies should be installed.

**Setup - Local Install:**

If you are planning to make modifications to this project or you would like to access it
before it has been indexed on `PyPi`. I would recommend you either install this project
in `editable` mode or do a `local install`. For those of you, who want to make modifications
to this project. I would recommend you install the library in `editable` mode.

If you want to install the library in `editable` mode, make sure to run the `setup.py`
file, so you can install any dependencies you may need. To run the `setup.py` file,
run the following command in your terminal.

```console
pip install -e .
```

If you don't plan to make any modifications to the project but still want to
use it across your different projects, then do a local install.

```console
pip install .
```

This will install all the dependencies listed in the `setup.py` file. Once done
you can use the library wherever you want.

## Usage

```python
import pathlib
from configparser import ConfigParser
from youtube.client import YouTubeClient

# Grab configuration values.
config = ConfigParser()
config.read('configs/config.ini')

# Grab the Inputs.
api_key = config.get('main', 'api_key')
channel_id = config.get('main', 'channel_id')
playlist_id = config.get('main', 'playlist_id')
client_secret_path = config.get('main', 'client_secret_path')
state_path = config.get('main', 'state_path')

# Create a new instance of the Client.
youtube_session = YouTubeClient(
    api_key=api_key,
    channel_id=channel_id,
    client_secret_path=client_secret_path,
    state_path=state_path
)

# Set the data folder.
youtube_session.data_folder_path = pathlib.Path('data').resolve()
```

## Support These Projects

**Patreon:**
Help support this project and future projects by donating to my [Patreon Page](https://www.patreon.com/sigmacoding). I'm always
looking to add more content for individuals like yourself, unfortuantely some of the APIs I would require me to pay monthly fees.

**YouTube:**
If you'd like to watch more of my content, feel free to visit my YouTube channel [Sigma Coding](https://www.youtube.com/c/SigmaCoding).
