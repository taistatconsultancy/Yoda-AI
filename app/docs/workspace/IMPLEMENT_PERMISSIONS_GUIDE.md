# 🔐 Implementing Permissions in Existing Routes

## Quick Reference

### Permission Dependencies

```python
from app.api.dependencies.permissions import (
    require_workspace_owner,      # Owner only
    require_workspace_facilitator, # Facilitator or higher
    require_workspace_member,      # Member or higher (any role)
    require_workspace_role,        # Custom role requirement
    get_workspace_membership       # Just check membership, no role check
)
```

### Role Hierarchy

```
Owner (4) > Facilitator (3) > Member (2) > Viewer (1)
```

---

## Route Update Examples

### Example 1: Update Workspace Invite Route

**Before:**
```python
@router.post("/{workspace_id}/invite")
async def invite_member(
    workspace_id: int,
    invite_data: InviteMember,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Manual permission check
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member")
    
    if membership.role not in ['owner', 'facilitator']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # ... rest of logic
```

**After:**
```python
@router.post("/{workspace_id}/invite")
async def invite_member(
    workspace_id: int,
    invite_data: InviteMember,
    membership = Depends(require_workspace_role(workspace_id, "facilitator")),
    db: Session = Depends(get_db)
):
    # Permission check handled by dependency!
    # membership object is available if we reach here
    
    # ... rest of logic
```

---

### Example 2: Update Retrospective Creation

**Before:**
```python
@router.post("/retrospectives/")
async def create_retrospective(
    retro_data: RetrospectiveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check workspace membership
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == retro_data.workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a workspace member")
    
    # Only facilitators can create retrospectives
    if membership.role not in ['owner', 'facilitator']:
        raise HTTPException(status_code=403, detail="Must be facilitator or owner")
    
    # ... rest of logic
```

**After:**
```python
@router.post("/retrospectives/")
async def create_retrospective(
    retro_data: RetrospectiveCreate,
    membership = Depends(require_workspace_facilitator(retro_data.workspace_id)),
    db: Session = Depends(get_db)
):
    # Permission check handled! Can proceed with creation
    # ... rest of logic
```

---

### Example 3: View Members (Any Member Can View)

**Before:**
```python
@router.get("/{workspace_id}/members")
async def get_workspace_members(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check membership
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member")
    
    # ... rest of logic
```

**After:**
```python
@router.get("/{workspace_id}/members")
async def get_workspace_members(
    workspace_id: int,
    membership = Depends(require_workspace_member(workspace_id)),
    db: Session = Depends(get_db)
):
    # Permission check handled!
    # membership object available with role info
    # ... rest of logic
```

---

## Routes to Update

### 🔴 High Priority (Critical for Security)

1. **`app/api/routes/workspaces.py`**
   - `POST /{workspace_id}/invite` → Use `require_workspace_role(workspace_id, "facilitator")`
   - `DELETE /{workspace_id}` → Use `require_workspace_owner(workspace_id)`
   - `PUT /{workspace_id}/settings` → Use `require_workspace_owner(workspace_id)`

2. **`app/api/routes/retrospectives_full.py`**
   - `POST /retrospectives/` → Use `require_workspace_facilitator(workspace_id)`
   - `POST /{id}/start` → Use `require_workspace_facilitator(retro.workspace_id)`
   - `POST /{id}/advance-phase` → Use `require_workspace_facilitator(retro.workspace_id)`

### 🟡 Medium Priority (Data Access)

3. **Action Items Routes**
   - Create action item → Check facilitator role
   - Update action item → Check membership
   - Delete action item → Check facilitator role

4. **Voting Routes**
   - Vote on themes → Check member role
   - View voting results → Check member role

### 🟢 Low Priority (Read Operations)

5. **View Routes**
   - View retrospectives → Check member role
   - View responses → Check member role
   - View summaries → Check member role

---

## Step-by-Step Migration

### Step 1: Import Dependencies

```python
# At the top of your route file
from app.api.dependencies.permissions import (
    require_workspace_owner,
    require_workspace_facilitator,
    require_workspace_member,
    require_workspace_role
)
```

### Step 2: Identify Required Role

For each endpoint, determine:
- **Who can access this?** (owner, facilitator, member, viewer)
- **What role is sufficient?**

Examples:
- Delete workspace → **Owner only**
- Invite members → **Facilitator or higher**
- View members → **Member or higher** (any role)
- Create retrospective → **Facilitator or higher**
- Submit response → **Member or higher**
- View retrospective → **Member or higher**

### Step 3: Add Permission Dependency

Replace manual checks with dependency:

```python
# Old way
async def my_endpoint(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    membership = db.query(WorkspaceMember)...
    if not membership or membership.role not in ['owner', 'facilitator']:
        raise HTTPException(...)

# New way
async def my_endpoint(
    workspace_id: int,
    membership = Depends(require_workspace_facilitator(workspace_id)),
    db: Session = Depends(get_db)
):
    # Permission guaranteed! Membership object available
    pass
```

### Step 4: Remove Manual Checks

Delete these blocks:
```python
# DELETE THESE
membership = db.query(WorkspaceMember).filter(...).first()
if not membership:
    raise HTTPException(...)
if membership.role not in [...]:
    raise HTTPException(...)
```

### Step 5: Use membership Object

The dependency returns a `WorkspaceMember` object you can use:

```python
@router.get("/{workspace_id}/info")
async def get_workspace_info(
    workspace_id: int,
    membership = Depends(require_workspace_member(workspace_id)),
    db: Session = Depends(get_db)
):
    # membership.role contains user's role
    # membership.user_id contains user ID
    # membership.workspace_id contains workspace ID
    # membership.joined_at contains join date
    
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    return {
        "workspace": workspace,
        "user_role": membership.role,
        "joined_at": membership.joined_at
    }
```

---

## Common Patterns

### Pattern 1: Owner-Only Endpoint

```python
@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: int,
    membership = Depends(require_workspace_owner(workspace_id)),
    db: Session = Depends(get_db)
):
    # Only owners reach here
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    workspace.is_active = False
    db.commit()
    return {"message": "Workspace deleted"}
```

### Pattern 2: Facilitator-Only Endpoint

```python
@router.post("/{workspace_id}/retrospectives")
async def create_retro(
    workspace_id: int,
    retro_data: RetrospectiveCreate,
    membership = Depends(require_workspace_facilitator(workspace_id)),
    db: Session = Depends(get_db)
):
    # Only facilitators and owners reach here
    new_retro = Retrospective(
        workspace_id=workspace_id,
        facilitator_id=membership.user_id,
        ...
    )
    db.add(new_retro)
    db.commit()
    return new_retro
```

### Pattern 3: Member-Endpoint (Any Role)

```python
@router.get("/{workspace_id}/members")
async def get_members(
    workspace_id: int,
    membership = Depends(require_workspace_member(workspace_id)),
    db: Session = Depends(get_db)
):
    # Any workspace member can view members
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.is_active == True
    ).all()
    return members
```

### Pattern 4: Custom Role Requirement

```python
@router.put("/{workspace_id}/settings")
async def update_settings(
    workspace_id: int,
    settings: WorkspaceSettings,
    membership = Depends(require_workspace_role(workspace_id, "facilitator")),
    db: Session = Depends(get_db)
):
    # Requires facilitator role or higher
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    workspace.settings = settings.dict()
    db.commit()
    return workspace
```

---

## Testing Your Changes

### Test 1: Owner Can Access
```python
# Login as owner
owner_token = login_as_owner()
response = client.post(
    f"/workspaces/{workspace_id}/delete",
    headers={"Authorization": f"Bearer {owner_token}"}
)
assert response.status_code == 200
```

### Test 2: Member Cannot Access
```python
# Login as regular member
member_token = login_as_member()
response = client.post(
    f"/workspaces/{workspace_id}/delete",
    headers={"Authorization": f"Bearer {member_token}"}
)
assert response.status_code == 403
assert "requires" in response.json()["detail"].lower()
```

### Test 3: Non-Member Cannot Access
```python
# Login as user not in workspace
non_member_token = login_as_non_member()
response = client.get(
    f"/workspaces/{workspace_id}/members",
    headers={"Authorization": f"Bearer {non_member_token}"}
)
assert response.status_code == 403
assert "not a member" in response.json()["detail"].lower()
```

---

## Benefits of Using Dependencies

✅ **Consistency**: Same permission logic everywhere
✅ **Security**: Centralized authorization checks
✅ **Maintainability**: Update permission logic in one place
✅ **Readability**: Clear intent in route definition
✅ **Testability**: Easy to mock for testing
✅ **DRY**: Don't repeat permission check code

---

## Next Steps

1. Update `app/api/routes/workspaces.py` routes
2. Update `app/api/routes/retrospectives_full.py` routes
3. Update action items, voting, and other routes
4. Test each endpoint with different roles
5. Update API documentation

Happy coding! 🚀
