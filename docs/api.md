# API Reference

All endpoints except `/health` require authentication when `AUTH_DISABLED=false`. See [Authentication](authentication.md) for details.

The API is auto-generated from the resource registry. The FastAPI application also serves interactive API documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running.

## Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Unauthenticated health check. Returns `{"status": "ok"}`. Used by Kubernetes probes. |

## Groups

Groups use a string primary key with dot-notation (e.g., `engineering.backend`). The `parent_id` field creates a self-referencing hierarchy.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/groups/` | List all groups, ordered by ID. |
| `GET` | `/groups/{id}` | Get a single group by ID. |
| `POST` | `/groups/` | Create a group. Returns 409 if the ID already exists. Returns 422 if `parent_id` references a non-existent group. |
| `PATCH` | `/groups/{id}` | Update a group's `label` or `parent_id`. Returns 422 if new `parent_id` does not exist. |
| `DELETE` | `/groups/{id}` | Delete a group. Returns 409 if the group is still referenced by details. |

### Group Schema

**Create (`POST`):**
```json
{
  "id": "engineering.backend",
  "parent_id": "engineering",
  "label": "Backend"
}
```

**Response:**
```json
{
  "id": "engineering.backend",
  "parent_id": "engineering",
  "label": "Backend"
}
```

## Items

Items use an auto-increment integer primary key. The `name` field must be unique.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/items/` | List all items, ordered by `name`. Supports `?q=` for case-insensitive search and `?group=` for filtering by detail group. |
| `GET` | `/items/{id}` | Get an item with its details. |
| `POST` | `/items/` | Create an item with one or more details. Returns 409 if the name already exists. Returns 422 if any detail's `group_id` does not exist. |
| `PATCH` | `/items/{id}` | Update an item's name. Returns 409 if the new name already exists. |
| `DELETE` | `/items/{id}` | Delete an item and all its details (cascade). |

### Item Schema

**Create (`POST`):**
```json
{
  "name": "Widget",
  "details": [
    {
      "description": "A reusable component",
      "notes": "Used in production",
      "group_id": "engineering.backend"
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Widget",
  "details": [
    {
      "id": 1,
      "description": "A reusable component",
      "notes": "Used in production",
      "group_id": "engineering.backend"
    }
  ]
}
```

## Details (Nested Under Items)

Details are managed as nested resources under items.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/items/{item_id}/details` | Add a detail to an item. Returns 422 if `group_id` does not exist. |
| `PATCH` | `/items/{item_id}/details/{detail_id}` | Update a detail. |
| `DELETE` | `/items/{item_id}/details/{detail_id}` | Delete a detail. |

### Detail Schema

**Create (`POST`):**
```json
{
  "description": "An alternative implementation",
  "notes": null,
  "group_id": "engineering"
}
```

## Backup and Restore

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/backup/` | Authenticated | Export all groups and items (with inline details) as JSON. |
| `POST` | `/backup/restore` | `App.Admin` role | Replace all data from a JSON upload. Deletes all existing data first. |

### Backup Format

```json
{
  "version": 1,
  "groups": [
    { "id": "engineering", "parent_id": null, "label": "Engineering" },
    { "id": "engineering.backend", "parent_id": "engineering", "label": "Backend" }
  ],
  "items": [
    {
      "name": "Widget",
      "details": [
        { "description": "A reusable component", "notes": "Used in production", "group_id": "engineering.backend" }
      ]
    }
  ]
}
```

The restore endpoint handles self-referencing FK ordering (groups with `parent_id` are inserted topologically) and parent-child inline embedding (item details are extracted and linked after the parent item is created).

## Error Responses

The API uses standard HTTP status codes with a `detail` field:

| Status | Meaning |
|--------|---------|
| 201 | Created (POST success) |
| 204 | No Content (DELETE success) |
| 401 | Missing or invalid authentication token |
| 403 | Insufficient role or scope |
| 404 | Resource not found |
| 409 | Conflict (duplicate unique field, or resource still referenced on delete) |
| 422 | Validation error (missing required field, FK reference not found) |
