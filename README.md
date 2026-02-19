# JsonActionClient

A wrapper for the FairCom JSON Action API.

## What it does

This class provides a Python "client" that manages logging into the server (createSession), logging out of the server (deleteSession), and provides an easy way to POST to the server and access the session authToken.

When your program closes, any client you created will automatically log out of the FairCom server.

Exceptions are caught and re-raised as a JsonActionError (or a derived exception).

## What it does not do

The client does not perform any "keepalive" operations. By default, the session will expire after 30 seconds. This timeout can be set by using the "timeout" parameter when instantiating the client.

## Installation

```bash
pip install faircom-json-action-client
```

## Usage

Both secure and insecure connections are possible. All certificate files should be PEM-encoded X.509 certificates.

### Example mTLS usage:

```Python
from json_action_client import JsonActionClient, JsonActionConnectionError, JsonActionApiError

client = JsonActionClient( "https://127.0.0.1:8444/api", ca_cert = "/FairCom/ca.crt", client_cert = "/FairCom/client.pem" )
client.login()

with client:
    list_databases_json = client.build_basic_request( api = "db", action = "listDatabases" )
    response = client.post_json( list_databases_json )
    print( f"Response: {response}" )
```

This connection is considered the most secure and when done properly will be adequate to use over public networks. In the example above a client certificate and CA certificate are used to enable mutual-TLS (mTLS) with the [FairCom](https://www.faircom.com/) server.

The CA certificate (`ca.crt` in this example) must have signed both the client certificate (`client.pem`) and the server certificate. This provides TLS encryption for client communications and user-level access controls on the server (the client certificate CN must match a user account on the server). Client certificates can be invalidated by disabling the account on the server, avoiding the hassle of CRLs.

More details on FairCom TLS [can be found here](https://docs.faircom.com/docs/en/UUID-bbee8e14-258d-4203-397e-9f1486d852ca.html).

### Example TLS (one-sided) and credential usage:

```Python
from json_action_client import JsonActionClient, JsonActionConnectionError, JsonActionApiError

client = JsonActionClient( "https://127.0.0.1:8443/api", ca_cert = "/FairCom/ca.crt" )
client.login( "admin", "ADMIN" )

with client:
    list_databases_json = client.build_basic_request( api = "db", action = "listDatabases" )
    response = client.post_json( list_databases_json )
    print( f"Response: {response}" )
```

This connection is also considered secure enough to use over public networks when properly configured. Ensure the [FairCom server TLS settings](https://docs.faircom.com/docs/en/UUID-af006a2a-a08c-afa5-806a-f5f5979a1ae2.html) are adequate for modern threats (particularly the allowed cipher suites).

### Example insecure usage (credentials without TLS):

```Python
from json_action_client import JsonActionClient, JsonActionConnectionError, JsonActionApiError

client = JsonActionClient( "http://127.0.0.1:8080/api" )
client.login( "admin", "ADMIN" )

with client:
    list_databases_json = client.build_basic_request( api = "db", action = "listDatabases" )
    response = client.post_json( list_databases_json )
    print( f"Response: {response}" )
```

An insecure connection should only be used on private networks where security is guaranteed via other means (e.g., an enterprise-grade firewall).

## Links

[Package info on PyPI](https://pypi.org/project/faircom-json-action-client/)

[Source code on GitHub](https://github.com/AdamJHowell/JsonActionClient)

## Notes

* This project is a work in progress and may change at any time.
* Breaking changes for versions at 1.0 or higher will always result in a new major version.
* I try to use type hints wherever possible. Please report undocumented `raises`.
