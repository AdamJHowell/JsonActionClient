# JsonActionClient

A wrapper for the FairCom JSON Action API.

## Installation

```bash
pip install faircom-json-action-client
```

## Usage
```Python
from json_action_client import JsonActionClient

client = JsonActionClient("[http://127.0.0.1:8080/api](http://127.0.0.1:8080/api)")
client.login("admin", "ADMIN")

with client:
    # ... do work
```

## Location

https://github.com/AdamJHowell/JsonActionClient
