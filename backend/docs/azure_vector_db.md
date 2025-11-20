# Azure Vector DB (env flags)

Short notes on environment flags used by the runtime vector DB stub.

- **`USE_AZURE_VECTOR_DB`**: Optional opt-in flag. When set (e.g. `1`, `true`, `True`) the runtime will attempt to use Azure Cognitive Search. When not set or falsy, the runtime falls back to the deterministic local index used for development and tests.

- Required Azure variables (only necessary if `USE_AZURE_VECTOR_DB` is enabled):
  - `AZURE_SEARCH_ENDPOINT` (e.g. `https://my-search-service.search.windows.net`)
  - `AZURE_SEARCH_KEY` (admin or query API key)
  - `AZURE_SEARCH_INDEX` (index name to query)

Example (PowerShell) export:

```powershell
$env:USE_AZURE_VECTOR_DB = '1'
$env:AZURE_SEARCH_ENDPOINT = 'https://your-service.search.windows.net'
$env:AZURE_SEARCH_KEY = 'REPLACE_WITH_KEY'
$env:AZURE_SEARCH_INDEX = 'products'
```

Notes
- The code guards Azure SDK imports; installing the Azure SDK is required for the Azure code path to run. If the SDK is missing or configuration is incomplete, the runtime falls back to the local deterministic index to keep tests and local runs deterministic.
