# Dashboard API Contract

**Feature**: 001-microsoft-login-counter
**Date**: 2025-11-21
**Protocol**: HTTP/1.1
**Base URL**: `http://localhost:8081` (configurable via config.yaml)

## Overview

The dashboard provides both HTML views (server-side rendered) and optional JSON APIs for statistics and event history. All endpoints are read-only - no mutations supported.

## Endpoints

### 1. GET / - Statistics Dashboard (HTML)

**Purpose**: Display today/week/month login counts and summary statistics

**Request**:
```http
GET / HTTP/1.1
Host: localhost:8081
Accept: text/html
```

**Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 2048

<!DOCTYPE html>
<html>
  <head>
    <title>Microsoft Login Counter</title>
    <!-- Basic CSS styling -->
  </head>
  <body>
    <h1>Microsoft Login Statistics</h1>
    <div class="stats">
      <div>Today: 3 logins</div>
      <div>This Week: 10 logins</div>
      <div>This Month: 42 logins</div>
      <div>Total: 156 logins</div>
    </div>
    <p><a href="/history">View Login History</a></p>
  </body>
</html>
```

**Error Responses**:
- `500 Internal Server Error` - Database connection failure

---

### 2. GET /history - Login History (HTML)

**Purpose**: Display chronological list of login events with timestamps

**Request**:
```http
GET /history?page=1&limit=100 HTTP/1.1
Host: localhost:8081
Accept: text/html
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (1-indexed) |
| `limit` | integer | No | 100 | Events per page (max: 1000) |

**Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 4096

<!DOCTYPE html>
<html>
  <head>
    <title>Login History - Microsoft Login Counter</title>
  </head>
  <body>
    <h1>Login Event History</h1>
    <table>
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Detection Method</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>2025-11-21 14:30:00 UTC</td>
          <td>connect_sequence</td>
        </tr>
        <tr>
          <td>2025-11-21 09:15:23 UTC</td>
          <td>oauth_callback</td>
        </tr>
        <!-- More events... -->
      </tbody>
    </table>
    <div class="pagination">
      <a href="/history?page=2">Next Page</a>
    </div>
  </body>
</html>
```

**Error Responses**:
- `400 Bad Request` - Invalid query parameters (e.g., `page < 1`, `limit > 1000`)
- `500 Internal Server Error` - Database query failure

---

### 3. GET /api/stats - Statistics (JSON)

**Purpose**: JSON API for retrieving login statistics (optional endpoint for future enhancements)

**Request**:
```http
GET /api/stats HTTP/1.1
Host: localhost:8081
Accept: application/json
```

**Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 234

{
  "today_count": 3,
  "week_count": 10,
  "month_count": 42,
  "total_count": 156,
  "period_start": "2025-11-21T00:00:00Z",
  "period_end": "2025-11-21T23:59:59Z",
  "first_event": "2024-06-15T10:30:00Z",
  "last_event": "2025-11-21T14:30:00Z"
}
```

**Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "today_count": { "type": "integer", "minimum": 0 },
    "week_count": { "type": "integer", "minimum": 0 },
    "month_count": { "type": "integer", "minimum": 0 },
    "total_count": { "type": "integer", "minimum": 0 },
    "period_start": { "type": "string", "format": "date-time" },
    "period_end": { "type": "string", "format": "date-time" },
    "first_event": { "type": "string", "format": "date-time", "nullable": true },
    "last_event": { "type": "string", "format": "date-time", "nullable": true }
  },
  "required": ["today_count", "week_count", "month_count", "total_count", "period_start", "period_end"]
}
```

**Error Responses**:
- `500 Internal Server Error` - Database connection or query failure

---

### 4. GET /api/events - Event List (JSON)

**Purpose**: JSON API for retrieving paginated login events (optional endpoint)

**Request**:
```http
GET /api/events?page=1&limit=100 HTTP/1.1
Host: localhost:8081
Accept: application/json
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (1-indexed) |
| `limit` | integer | No | 100 | Events per page (max: 1000) |
| `start_date` | string (ISO 8601) | No | null | Filter events >= start_date |
| `end_date` | string (ISO 8601) | No | null | Filter events < end_date |

**Response** (200 OK):
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 1024

{
  "events": [
    {
      "id": 156,
      "timestamp": "2025-11-21T14:30:00Z",
      "detected_via": "connect_sequence"
    },
    {
      "id": 155,
      "timestamp": "2025-11-21T09:15:23Z",
      "detected_via": "oauth_callback"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 100,
    "total_events": 156,
    "total_pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

**Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "timestamp": { "type": "string", "format": "date-time" },
          "detected_via": { "type": "string", "enum": ["connect_sequence", "http_redirect", "oauth_callback"] }
        },
        "required": ["id", "timestamp", "detected_via"]
      }
    },
    "pagination": {
      "type": "object",
      "properties": {
        "page": { "type": "integer", "minimum": 1 },
        "limit": { "type": "integer", "minimum": 1, "maximum": 1000 },
        "total_events": { "type": "integer", "minimum": 0 },
        "total_pages": { "type": "integer", "minimum": 0 },
        "has_next": { "type": "boolean" },
        "has_prev": { "type": "boolean" }
      }
    }
  },
  "required": ["events", "pagination"]
}
```

**Error Responses**:
- `400 Bad Request` - Invalid query parameters
  ```json
  {
    "error": "Invalid query parameter",
    "details": "limit must be between 1 and 1000"
  }
  ```
- `500 Internal Server Error` - Database query failure
  ```json
  {
    "error": "Database error",
    "details": "Failed to query login events"
  }
  ```

---

## Error Responses

All error responses follow a consistent format:

**HTML Errors** (for `/` and `/history`):
```html
<!DOCTYPE html>
<html>
  <head><title>Error</title></head>
  <body>
    <h1>Error {status_code}</h1>
    <p>{error_message}</p>
    <p><a href="/">Back to Dashboard</a></p>
  </body>
</html>
```

**JSON Errors** (for `/api/*`):
```json
{
  "error": "Error type",
  "details": "Detailed error message",
  "status_code": 500
}
```

---

## Common HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | OK | Successful request |
| `400` | Bad Request | Invalid query parameters |
| `404` | Not Found | Endpoint does not exist |
| `500` | Internal Server Error | Database or server failure |
| `503` | Service Unavailable | Proxy/dashboard starting up |

---

## Content Types

**Supported Request Headers**:
- `Accept: text/html` - HTML response (default)
- `Accept: application/json` - JSON response (for `/api/*` endpoints)

**Response Headers**:
- `Content-Type: text/html; charset=utf-8` - HTML responses
- `Content-Type: application/json` - JSON responses
- `Cache-Control: no-cache, no-store, must-revalidate` - Prevent caching (data changes frequently)
- `X-Content-Type-Options: nosniff` - Security header

---

## Time Period Calculations

All time periods use user's local timezone for display but UTC for storage.

**Today**: Midnight to midnight in local timezone
**This Week**: Monday 00:00 to Sunday 23:59 in local timezone (ISO 8601)
**This Month**: 1st 00:00 to last day 23:59 in local timezone

**Example**:
- Current time: 2025-11-21 14:30:00 UTC (user in UTC timezone)
- Today: 2025-11-21 00:00:00 to 2025-11-21 23:59:59
- This Week: 2025-11-18 00:00:00 (Monday) to 2025-11-24 23:59:59 (Sunday)
- This Month: 2025-11-01 00:00:00 to 2025-11-30 23:59:59

---

## Performance Requirements

Per spec success criteria (SC-007, SC-006):
- Dashboard page load: < 2 seconds
- Statistics computation: < 10 seconds (typically < 100ms for <10k events)
- History pagination: < 1 second per page

---

## Security Considerations

**Access Control**:
- Dashboard bound to `localhost` or `127.0.0.1` by default (not exposed to network)
- Optional configuration to bind to `0.0.0.0` (user must explicitly enable)

**CORS**: Not applicable (same-origin, localhost-only)

**Authentication**: None (local-only deployment, single user)

**CSRF**: Not applicable (no mutations, read-only endpoints)

**SQL Injection**: Prevented via parameterized queries in backend

---

## Testing Contract

### Unit Tests

Test each endpoint independently with mocked database:

```python
def test_stats_endpoint_success():
    # Mock database to return sample statistics
    response = client.get('/api/stats')
    assert response.status_code == 200
    assert response.json['today_count'] >= 0

def test_history_endpoint_pagination():
    # Mock database with 250 events
    response = client.get('/history?page=2&limit=100')
    assert response.status_code == 200
    assert 'Page 2' in response.text
```

### Integration Tests

Test with real SQLite database:

```python
def test_end_to_end_dashboard_flow():
    # Insert 5 test events
    db.insert_events(generate_test_events(5))

    # Fetch statistics
    response = client.get('/api/stats')
    assert response.json['total_count'] == 5

    # Fetch history
    response = client.get('/api/events')
    assert len(response.json['events']) == 5
```

### Contract Tests

Verify response schemas match specification:

```python
def test_stats_response_schema():
    response = client.get('/api/stats')
    validate(response.json, stats_schema)  # JSON Schema validation

def test_events_response_schema():
    response = client.get('/api/events')
    validate(response.json, events_schema)
```

---

## Implementation Notes

### Flask Routes

```python
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    stats = get_statistics()  # Query database
    return render_template('index.html', stats=stats)

@app.route('/history')
def history():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    events = get_events_paginated(page, limit)
    return render_template('history.html', events=events, page=page)

@app.route('/api/stats')
def api_stats():
    stats = get_statistics()
    return jsonify(stats)

@app.route('/api/events')
def api_events():
    page = request.args.get('page', 1, type=int)
    limit = min(request.args.get('limit', 100, type=int), 1000)
    events = get_events_paginated(page, limit)
    return jsonify({
        'events': events,
        'pagination': calculate_pagination(page, limit)
    })
```

### Error Handling

```python
@app.errorhandler(404)
def not_found(error):
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Not Found', 'status_code': 404}), 404
    return render_template('error.html', code=404, message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Internal Server Error', 'status_code': 500}), 500
    return render_template('error.html', code=500, message='Server error'), 500
```

---

## Next Steps

- [x] API contract documented
- [ ] Implement Flask routes in `src/dashboard/routes.py`
- [ ] Create Jinja2 templates (`index.html`, `history.html`)
- [ ] Write contract tests for response schemas
- [ ] Test pagination logic with large event datasets
