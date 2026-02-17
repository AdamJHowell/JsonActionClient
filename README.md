# JsonActionClient

A wrapper for the FairCom JSON Action API.

## Installation

```bash
pip install faircom-json-action-client
```

## Usage

### Example credential usage:

```Python
client = JsonActionClient( "http://127.0.0.1:8080/api" )
client.login( "admin", "ADMIN" )

with client:
    list_databases_json = {
        "api":       "db",
        "action":    "listDatabases",
        "params":    { },
        "authToken": client.auth_token
    }
    response = client.post_json( list_databases_json )
    print( f"Response: {json.dumps( response, indent = 3 )}" )
```

### Example client certificate usage:

```Python
client = JsonActionClient( "https://127.0.0.1:8444/api", ca_cert = "/FairCom/ca.crt", client_cert = "/FairCom/client.pem" )
client.login()

with client:
    list_databases_json = {
        "api":       "db",
        "action":    "listDatabases",
        "params":    { },
        "authToken": client.auth_token
    }
    response = client.post_json( list_databases_json )
    print( f"Response: {json.dumps( response, indent = 3 )}" )
```

## Location

https://github.com/AdamJHowell/JsonActionClient
