# JsonActionClient

A wrapper for the FairCom JSON Action API.

## Installation

```bash
pip install faircom-json-action-client
```

## Usage

All certificate files should be PEM-encoded X.509 certificates.

### Example mTLS (client certificate) usage:

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

### Example TLS (one-sided) usage:

```Python
client = JsonActionClient( "https://127.0.0.1:8444/api", ca_cert = "/FairCom/ca.crt" )
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

### Example insecure usage:

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

## Source code

https://github.com/AdamJHowell/JsonActionClient

## Notes

* This project is a work in progress and may change at any time.
* Breaking changes for versions at 1.0 or higher will always result in a new major version.
* I try to use type hints wherever possible.  Please report undocumented `raises`.
