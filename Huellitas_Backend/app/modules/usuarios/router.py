from postgrest import APIError as PostgrestAPIError
from postgrest import APIResponse as PostgrestAPIResponse
from realtime import AuthorizationError, NotConnectedError
from storage3.utils import StorageException
from supabase_auth.errors import (
    AuthApiError,
    AuthError,
    AuthImplicitGrantRedirectError,
    AuthInvalidCredentialsError,
    AuthRetryableError,
    AuthSessionMissingError,
    AuthUnknownError,
    AuthWeakPasswordError,
)
from supabase_functions.errors import (
    FunctionsError,
    FunctionsHttpError,
    FunctionsRelayError,
)

# Async Client
from ._async.auth_client import AsyncSupabaseAuthClient as ASupabaseAuthClient
from ._async.client import AsyncClient
from ._async.client import AsyncClient as AClient
from ._async.client import AsyncStorageClient as