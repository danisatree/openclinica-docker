# OpenClinica CE — Docker (local development)

Runs [OpenClinica Community Edition](https://github.com/OpenClinica/OpenClinica) 3.17.2 in Docker for local eCRF design and testing. One command to start, data persists between restarts.

> **For local development only.**  
> Default credentials are intentionally simple and must not be used in production.

## Requirements

- Docker (or OrbStack)
- ~4 GB free disk space (Maven build downloads dependencies on first run)

## Quick start

```bash
git clone https://github.com/danisatree/openclinica-docker.git
cd OpenClinica-docker
docker compose up -d
```

First launch takes **10–20 minutes** — Maven downloads dependencies and compiles the source. Subsequent starts are instant (image is cached).

When the container is ready, open: [http://localhost:8080/OpenClinica](http://localhost:8080/OpenClinica)

Default login: `root` / `1234567890`

## Credentials

| Service | User | Password |
|---|---|---|
| OpenClinica | `root` | `1234567890` |
| PostgreSQL (superuser) | `postgres` | `postgres` |
| PostgreSQL (app user) | `clinica` | `clinica` |

## Useful commands

```bash
# Start
docker compose up -d

# Stop (data is preserved)
docker compose down

# View logs
docker compose logs -f oc

# Full reset (deletes all data)
docker compose down -v
```

## What's inside

- **OpenClinica 3.17.2** built from source (tag `3.17.2` — tag `3.17.3` does not exist upstream)
- **PostgreSQL 13**
- Six fixes applied at build time:
  - LDAP host patched to `127.0.0.1` so login is instant instead of waiting 8+ seconds for a non-existent LDAP server
  - `CompressingFilter` removed from `web.xml` — the bundled v1.6.4 hangs ~20 seconds on gzip requests for static files, causing very slow page loads in all browsers
  - `CreateCRFVersionServlet` patched to handle null session beans — prevents NullPointerException when uploading a CRF XLS after a container restart
  - `CoreSecureController` patched to remove hardcoded `Content-Encoding: gzip` response header — without `CompressingFilter` the header was set but the body was never compressed, causing `ERR_CONTENT_DECODING_FAILED` on all CRF data-entry pages
  - Four JSPs (`home-header.jsp`, `viewSectionDataEntry.jsp`, `doubleDataEntry.jsp`, `initialDataEntryNw.jsp`) patched to fix `function $(x)` overriding Prototype.js's `$` — the override caused `dom:loaded` event to fail with `TypeError: Cannot read properties of null (reading 'dispatchEvent')`, preventing form controls (save button) from rendering on data-entry pages
  - Four data-entry JSPs (`viewSectionDataEntry.jsp`, `initialDataEntryNw.jsp`, `doubleDataEntry.jsp`, `administrativeEditing.jsp`) patched to fix the repeating group Add button — when `GROUP_REPEAT_MAX` is left blank in the CRF XLS the parser defaults it to 1 (same as `GROUP_REPEAT_NUMBER`), causing `repetition-model.js` to cap at 1 block immediately; fix omits the `repeat-max` HTML attribute when it does not exceed `repeat-start`, so JS defaults to unlimited
