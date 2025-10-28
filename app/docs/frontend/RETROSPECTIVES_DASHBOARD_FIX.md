# Retrospectives Dashboard Fix

## Issue
The dashboard was unable to load retrospectives, showing 404 errors:
```
GET /retrospectives/7 HTTP/1.1" 404 Not Found
```

Scheduled retrospectives were not being displayed in the dashboard.

## Root Cause
The frontend's `loadDashboardData()` function was calling `/api/v1/retrospectives/` (root endpoint), but the `retrospectives_full.router` didn't have a root GET endpoint. It only had:
- `GET /workspace/{workspace_id}` - get retrospectives for a specific workspace
- `GET /{retro_id}` - get a specific retrospective

The API was missing the endpoint to list all retrospectives for the current user.

## Solution
Added a new `GET /` endpoint to `app/api/routes/retrospectives_full.py` that:
1. Gets all workspaces the user is a member of
2. Queries retrospectives where the user is a participant
3. Returns all retrospectives across all workspaces the user belongs to
4. Supports optional `workspace_id` query parameter to filter to a specific workspace

The endpoint returns:
- All retrospectives where the current user is a participant
- Ordered by creation date (most recent first)
- Includes all retrospective details (id, workspace_id, title, sprint_name, status, phase, etc.)

## API Endpoint

### GET /api/v1/retrospectives/

**Query Parameters:**
- `workspace_id` (optional): Filter retrospectives to a specific workspace

**Response:**
```json
[
  {
    "id": 1,
    "workspace_id": 5,
    "title": "Sprint Review",
    "sprint_name": "Sprint 1",
    "description": "Review of sprint activities",
    "facilitator_id": 11,
    "scheduled_start_time": "2025-10-27T17:48:00+00:00",
    "scheduled_end_time": "2025-10-27T17:53:00+00:00",
    "status": "scheduled",
    "current_phase": "input",
    "created_at": "2025-10-27T17:47:35.220839+00:00"
  }
]
```

## Status
✅ Fixed - Dashboard now loads and displays all retrospectives for the user

## How It Works
1. User logs in and dashboard loads
2. Frontend calls `GET /api/v1/retrospectives/` 
3. API queries all retrospectives where user is a participant
4. Returns list of retrospectives with their details
5. Dashboard displays the retrospectives with count and status

The fix ensures that users can see all retrospectives they're involved in, across all their workspaces.
