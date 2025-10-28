# 📋 Workspace and Roles Architecture

## Overview

YodaAI implements a **workspace-based** architecture where all data is organized within workspaces. Users belong to one or more workspaces, each with specific roles that control their access and permissions.

---

## 🏢 Workspace Structure

### What is a Workspace?

A **workspace** is a container for:
- Teams and their members
- Retrospectives
- Action items
- Chat sessions and messages
- All collaborative data

**Key Points:**
- Every retrospective belongs to exactly one workspace
- Users can be members of multiple workspaces
- Each workspace has its own settings and configuration
- Workspace data is isolated from other workspaces

### Workspace Model

```python
class Workspace(Base):
    id: int                    # Primary key
    name: str                  # Workspace name (e.g., "Engineering Team")
    description: str           # Optional description
    created_by: int            # User ID who created the workspace
    settings: JSON             # Workspace-specific settings
    is_active: bool           # Whether workspace is active
    archived_at: DateTime     # When workspace was archived (if applicable)
    created_at: DateTime      # Creation timestamp
    updated_at: DateTime      # Last update timestamp
```

### Workspace Settings (JSON)

```json
{
  "allow_anonymous_responses": false,
  "require_email_verification": true,
  "auto_archive_after_days": 90,
  "max_members": 100
}
```

---

## 👥 Role-Based Access Control (RBAC)

### Role Hierarchy

The system uses **4 role levels** with hierarchical permissions:

```
Owner (Level 4) - Full control
    ↓
Facilitator (Level 3) - Can manage retrospectives
    ↓
Member (Level 2) - Can participate
    ↓
Viewer (Level 1) - Read-only access
```

### Role Definitions

#### 1. **Owner** 🎯
- **Permissions:**
  - Full control over the workspace
  - Add/remove members
  - Change member roles
  - Archive/restore workspace
  - Modify workspace settings
  - Delete workspace
  - All facilitator and member permissions

- **Use Cases:**
  - Workspace creator
  - Team leads
  - Admin users

#### 2. **Facilitator** 🚀
- **Permissions:**
  - Create and manage retrospectives
  - Start retrospectives
  - Advance through retrospective phases
  - Invite new members
  - View all data in workspace
  - Export retrospective data
  - Manage action items
  - All member permissions

- **Use Cases:**
  - Scrum masters
  - Retrospective facilitators
  - Team coaches

#### 3. **Member** 👤
- **Permissions:**
  - Participate in retrospectives
  - Submit responses in 4Ls format
  - Vote on themes
  - Comment in discussions
  - View retrospective summaries
  - See action items
  - Create personal notes

- **Use Cases:**
  - Team members
  - Project participants
  - Regular contributors

#### 4. **Viewer** 👁️
- **Permissions:**
  - View retrospectives (read-only)
  - See summary reports
  - Read action items
  - Export data

- **Use Cases:**
  - Stakeholders
  - Management
  - Observers

---

## 🔗 Workspace Membership

### WorkspaceMember Model

```python
class WorkspaceMember(Base):
    id: int                    # Primary key
    workspace_id: int          # Foreign key to workspace
    user_id: int              # Foreign key to user
    role: str                 # 'owner', 'facilitator', 'member', 'viewer'
    is_active: bool          # Whether membership is active
    joined_at: DateTime      # When user joined
    left_at: DateTime        # When user left (if applicable)
```

### Key Relationships

```
User (1) ←→ (Many) WorkspaceMember ←→ (Many) Workspace
```

- One user can belong to multiple workspaces
- Each workspace can have multiple members
- Each membership has a specific role

---

## 📦 Data Storage Strategy

### Workspace-Scoped Data

All collaborative data is linked to a workspace via `workspace_id`:

1. **Retrospectives**
   ```python
   class Retrospective:
       workspace_id: int  # Links to workspace
   ```

2. **Action Items**
   ```python
   class ActionItem:
       retrospective_id: int  # Links to retrospective → workspace
   ```

3. **Chat Sessions**
   ```python
   class ChatSession:
       user_id: int
       retrospective_id: int  # Links to retrospective → workspace
   ```

4. **Responses & Messages**
   ```python
   class RetrospectiveResponse:
       user_id: int
       retrospective_id: int  # Links to retrospective → workspace
   ```

### Permission Checks

Every API endpoint that accesses workspace data should:

1. **Verify Membership**: Check if user is a member of the workspace
2. **Check Role**: Verify user has sufficient permissions for the action
3. **Filter Results**: Return only data from workspaces user has access to

### Example Permission Check

```python
from app.api.dependencies.permissions import require_workspace_role

@router.post("/retrospectives/")
async def create_retrospective(
    retro_data: RetrospectiveCreate,
    membership = Depends(require_workspace_role(retro_data.workspace_id, "facilitator")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # User is guaranteed to have facilitator+ role
    # Create retrospective...
```

---

## 🔐 Permission Dependencies

### Available Permission Dependencies

```python
from app.api.dependencies.permissions import (
    get_workspace_membership,
    require_workspace_role,
    require_workspace_owner,
    require_workspace_facilitator,
    require_workspace_member
)
```

### Usage Examples

#### 1. Require Any Member
```python
@router.get("/workspaces/{workspace_id}/members")
async def get_members(
    workspace_id: int,
    membership = Depends(require_workspace_member(workspace_id)),
    db: Session = Depends(get_db)
):
    # Any member can view members
    pass
```

#### 2. Require Facilitator
```python
@router.post("/retrospectives/")
async def create_retro(
    workspace_id: int,
    membership = Depends(require_workspace_facilitator(workspace_id)),
    db: Session = Depends(get_db)
):
    # Only facilitators+ can create retrospectives
    pass
```

#### 3. Require Owner
```python
@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: int,
    membership = Depends(require_workspace_owner(workspace_id)),
    db: Session = Depends(get_db)
):
    # Only owners can delete workspace
    pass
```

#### 4. Custom Role Requirement
```python
@router.post("/workspaces/{workspace_id}/invite")
async def invite_member(
    workspace_id: int,
    membership = Depends(require_workspace_role(workspace_id, "facilitator")),
    db: Session = Depends(get_db)
):
    # Requires facilitator role or higher
    pass
```

---

## 🗄️ Database Schema

### Workspaces Table

```sql
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    settings JSONB DEFAULT '{...}',
    is_active BOOLEAN DEFAULT TRUE,
    archived_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Workspace Members Table

```sql
CREATE TABLE workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(workspace_id, user_id)
);
```

### Indexes for Performance

```sql
CREATE INDEX idx_workspaces_created_by ON workspaces(created_by);
CREATE INDEX idx_workspaces_active ON workspaces(is_active);
CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX idx_workspace_members_active ON workspace_members(workspace_id, is_active);
```

---

## 🚀 Common Workflows

### Creating a Workspace

1. **User creates workspace** → Automatically becomes `owner`
2. **Owner invites members** → Specifies role (facilitator, member, viewer)
3. **Members accept invitation** → Added to `workspace_members` table

### Joining a Retrospective

1. **Check workspace membership** → Verify user is member
2. **Check user role** → Member can participate, viewer can only view
3. **Retrieve participants** → Add user to retrospective participants

### Inviting New Members

1. **Verify inviter has permission** → Must be facilitator or owner
2. **Send invitation** → Create row in `workspace_invitations` table
3. **Send email** → With invitation link containing token
4. **User accepts** → Create `workspace_member` record with specified role

---

## 📊 Data Queries

### Get User's Workspaces

```sql
SELECT w.*, wm.role
FROM workspaces w
JOIN workspace_members wm ON w.id = wm.workspace_id
WHERE wm.user_id = :user_id
  AND wm.is_active = true
  AND w.is_active = true;
```

### Get Workspace Members

```sql
SELECT u.*, wm.role, wm.joined_at
FROM users u
JOIN workspace_members wm ON u.id = wm.user_id
WHERE wm.workspace_id = :workspace_id
  AND wm.is_active = true;
```

### Check User Role

```sql
SELECT role
FROM workspace_members
WHERE workspace_id = :workspace_id
  AND user_id = :user_id
  AND is_active = true;
```

---

## ✅ Best Practices

1. **Always Check Permissions**: Use permission dependencies in all workspace-related endpoints
2. **Filter by Workspace**: Always filter data by user's workspace memberships
3. **Role Hierarchy**: Use `has_role_or_above()` for flexible permission checks
4. **Audit Trail**: Log role changes and permission violations
5. **Default Roles**: Set sensible defaults (e.g., new members get 'member' role)
6. **Soft Deletes**: Use `is_active = false` instead of hard deletes for members

---

## 🔒 Security Considerations

1. **SQL Injection**: Use parameterized queries (SQLAlchemy handles this)
2. **Authorization**: Always verify workspace membership before accessing data
3. **Role Elevation**: Prevent users from modifying their own role
4. **Cross-Workspace Access**: Never allow access to data from another workspace
5. **Token Validation**: Validate invitation tokens before accepting
6. **Rate Limiting**: Limit invitation emails to prevent spam

---

## 📝 Summary

- **Workspace** = Container for all collaborative data
- **Roles** = Hierarchical permissions (Owner > Facilitator > Member > Viewer)
- **Membership** = Links users to workspaces with specific roles
- **Permission Dependencies** = Reusable decorators for access control
- **Data Isolation** = All data scoped to workspace via `workspace_id`

This architecture ensures secure, scalable, and maintainable workspace management. 🎉
