# Database Schema Fix - Retrospectives Table

## Issue
The `retrospectives` table was missing several columns required by the `Retrospective` model, causing errors when trying to create retrospectives.

## Error Messages
1. `column "workspace_id" does not exist`
2. `column "sprint_name" does not exist`

## Solution
Created Alembic migration `372c7e4d8e04_add_workspace_id_to_retrospectives.py` to add all missing columns.

## Columns Added

### 1. Workspace and Organization
- `workspace_id` (INTEGER) - Links retrospective to a workspace
- `sprint_name` (VARCHAR(100)) - Sprint identifier

### 2. Facilitation
- `facilitator_id` (INTEGER) - Foreign key to users table

### 3. Scheduling
- `scheduled_start_time` (TIMESTAMP WITH TIME ZONE)
- `scheduled_end_time` (TIMESTAMP WITH TIME ZONE)
- `actual_start_time` (TIMESTAMP WITH TIME ZONE)
- `actual_end_time` (TIMESTAMP WITH TIME ZONE)

### 4. Status and Phases
- `current_phase` (VARCHAR(20), DEFAULT 'input')
- `phase_completion` (JSONB, DEFAULT '{}')

### 5. Settings and AI
- `settings` (JSONB, DEFAULT '{}')
- `ai_summary` (TEXT)
- `ai_insights` (JSONB)

## Indexes Created
- `idx_retrospectives_workspace` on `workspace_id`
- `idx_retrospectives_scheduled_start` on `scheduled_start_time`
- `idx_retrospectives_current_phase` on `current_phase`

## Foreign Keys
- `retrospectives_workspace_id_fkey` → references `workspaces(id)` ON DELETE CASCADE
- `facilitator_id` → references `users(id)`

## Migration Applied
```bash
python -m alembic upgrade head
```

## Verification
All columns are now present in the `retrospectives` table:
- workspace_id ✓
- sprint_name ✓
- facilitator_id ✓
- All scheduling columns ✓
- Phase tracking ✓
- AI fields ✓

## Status
✅ **COMPLETE** - Retrospective creation should now work without errors.
