# -*- coding: utf-8 -*-
# TestVariantFormat/JsonAction/json_action_client.py
import json
import logging

import requests

"""
Example credentials usage:
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


Example client certificate usage:
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
"""


class JsonActionClient:

    def __init__( self, endpoint: str, ca_cert: str = None, client_cert: str = None, client_pass: str = None, description: str = None ) -> None:
        """
        Construct the JsonActionClient class.
        :param endpoint: The JSON Action endpoint.
        :param ca_cert: An optional CA certificate file, in PEM format, to use when verifying the server certificate.
        :param client_cert: An optional client key pair (certificate and key) file, in PEM format, to use for mTLS authentication.
        """
        self.endpoint = endpoint
        self.auth_token = None
        self.description = description
        self._session = requests.Session()
        if ca_cert:
            self._session.verify = ca_cert
            if client_cert:
                self._session.cert = (client_cert, client_pass)

    def __enter__( self ):
        """
        Enters the runtime context related to this object.

        This method validates that :py:meth:`~JsonActionClient.login` has been
        called before entering the ``with`` block by checking for a valid ``auth_token``.

        :raises RuntimeError: If the ``auth_token`` is not set (i.e., :py:meth:`~JsonActionClient.login` was not successfully called).
        :returns: The client instance itself.
        """
        # We expect login() to be called explicitly before a 'with' block.
        # This warns the user if they forget to do so.
        if not self.auth_token:
            raise RuntimeError( "Must call login() before using context manager." )
        return self

    def __exit__( self, exc_type, exc_val, exc_tb ):
        """
        Handles cleanup when exiting a context manager block.

        If a session is active (auth_token is set), this method attempts to log out
        using :py:meth:`~JsonActionClient.logout`. Any exceptions during logout are
        caught and logged as warnings to prevent masking an exception that might have
        occurred within the ``with`` block.

        :param exc_type: The exception type (class), if an exception occurred in the block.
        :param exc_val: The exception instance, if an exception occurred in the block.
        :param exc_tb: The traceback object, if an exception occurred in the block.
        :returns: ``False``, which instructs the Python runtime to propagate any exception
                  that occurred inside the ``with`` block.
        """
        if self.auth_token:
            try:
                self.logout()
            except Exception as exception:
                # Log the logout failure but don't re-raise, the 'with' block should handle it.
                logging.getLogger( __name__ ).warning( f"Failed to log out: {exception}" )
        return False

    def post_json( self, data: dict ) -> dict:
        """
        Post JSON data to the endpoint and return the response.
        :param data: The JSON data to post.
        :return: The response.
        """
        logger = logging.getLogger( __name__ )
        action = data.get( "action", "unknown" )
        try:
            # Use the persistent session from the class constructor.
            logger.debug( f"Posting '{action}' to to {self.endpoint}..." )
            post_response = self._session.post( self.endpoint, json = data, timeout = 10 )
            # This raises requests.exceptions.HTTPError for 4xx/5xx status codes.
            post_response.raise_for_status()

            response_json = post_response.json()
            if "errorCode" in response_json and response_json['errorCode'] == 0:
                return response_json
            else:
                message = f"JSON Action error for '{action}', errorCode: {response_json.get( 'errorCode' )}, errorMessage: {response_json.get( 'errorMessage' )}"
                raise JsonActionApiError( message, response_json.get( 'errorCode' ), response_json.get( 'errorMessage' ), action, response_json )
        # -----------------------------------------------
        # Catch any ConnectionError (server down/refused)
        # -----------------------------------------------
        except requests.exceptions.ConnectionError as connection_error:
            # This catches MaxRetryError, ConnectionRefusedError, etc.
            logger.error( f"FATAL CONNECTION FAILURE: Server at {self.endpoint} is unreachable. Details: {connection_error}" )
            raise JsonActionConnectionError( f"Server connection failed: {connection_error}", self.endpoint ) from connection_error
        # --------------------------------------------------------------------
        # Catch all other requests-related failures (e.g., Timeout, SSL error)
        # --------------------------------------------------------------------
        except requests.exceptions.RequestException as request_error:
            # This will catch Timeout, SSLError, and any other RequestException subclasses
            # not explicitly caught above (like HTTPError from raise_for_status()).
            logger.error( f"Unexpected request error!: {request_error}" )
            logger.error( f"Request: {json.dumps( data )}" )
            # Using the base JsonActionError for anything else
            raise JsonActionError( f"Request failed: {request_error}" ) from request_error

    def login( self, username: str = None, password: str = None ) -> None:
        """
        Log in to the JSON Action server, storing the authToken in the configuration, and return the authToken.
        :param username: The username to log in with.
        :param password: The password to log in with.
        :return: The authToken for the session.
        :raises ValueError: If the client certificate is missing AND credentials are not provided.
        """
        params = { }
        # Only include username/password in params if they are provided.
        if username and password:
            params["username"] = username
            params["password"] = password
        # Set the session timeout to 30 seconds.
        params["idleConnectionTimeoutSeconds"] = 30

        create_session = {
            "api":    "admin",
            "action": "createSession",
            "params": params,
            "debug":  "max",
        }
        # Log in and save the response.
        response = self.post_json( create_session )
        # Store the authToken in the configuration.
        self.auth_token = response['authToken']

    def logout( self ) -> None:
        """
        Log out of the JSON Action server.
        """
        delete_session = {
            "api":       "admin",
            "action":    "deleteSession",
            "authToken": self.auth_token
        }
        self.post_json( delete_session )


class JsonActionError( Exception ):
    """Base exception for FairCom JSON Action API errors."""
    pass


class JsonActionConnectionError( JsonActionError ):
    """Exception for errors preventing a request from completing (e.g., server down)."""

    def __init__( self, message, endpoint_url ):
        # Call the base class constructor with the message
        super().__init__( message )

        # Store custom data on the exception object
        self.endpoint_url = endpoint_url


class JsonActionApiError( JsonActionError ):
    """FairCom API returned a non-zero error code."""

    def __init__( self, message, error_code: int, error_message: str, action: str = None, response_json: dict = None ) -> None:
        super().__init__( message )
        self.error_code = error_code
        self.error_message = error_message
        self.action = action
        self.response_json = response_json
