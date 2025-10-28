# 📋 Complete User Flow After Workspace Creation

## Overview

This document outlines the **complete user journey** from workspace creation to viewing retrieved data.

---

## 🔄 Complete Flow

### **Phase 1: User Signs In**
```
1. User logs in with email/password or Google
2. ✅ Receives JWT token
3. ✅ User data stored in localStorage
```

### **Phase 2: Workspace Creation**
```
1. Frontend checks: Does user have workspaces?
   - GET /api/v1/workspaces/
   
2. If empty → Show "Create Workspace" modal

3. User creates workspace:
   - Name: "Engineering Team"
   - Description: "Our team workspace"
   - Role: "facilitator"
   
4. POST /api/v1/workspaces/
   {
     "name": "Engineering Team",
     "description": "Our team workspace",
     "your_role": "facilitator"
   }

5. Backend creates:
   - Workspace record in `workspaces` table
   - Workspace membership in `workspace_members` table
   - User added as creator with specified role

6. ✅ Returns workspace data
7. ✅ Frontend stores in localStorage as currentWorkspace
```

### **Phase 3: What Should Happen After?**

After workspace creation, here's the **recommended flow**:

#### **Option A: Direct to Dashboard (Recommended)**

```
1. ✅ Workspace created
2. ✅ Navigate to: Dashboard View
3. Show:
   - Workspace name and description
   - Member count (you + others)
   - List of retrospectives (empty initially)
   - "Create Retrospective" button
```

#### **Option B: Create First Retrospective**

```
1. ✅ Workspace created
2. ✅ Show "Create First Retrospective" modal
3. User creates retrospective:
   - Title: "Sprint 1 Retrospective"
   - Sprint Name: "Sprint 1"
   - Start/End times
4. ✅ Backend creates retrospective
5. ✅ All workspace members added as participants
6. ✅ Redirect to retrospective dashboard
```

---

## 🎯 Recommended Implementation

### **Frontend Flow:**

```javascript
// After workspace creation
async function afterWorkspaceCreated(workspace) {
  // 1. Store workspace
  currentWorkspace = workspace;
  localStorage.setItem('current_workspace', JSON.stringify(workspace));
  
  // 2. Load workspace data
  await loadWorkspaceData(workspace.id);
  
  // 3. Show dashboard
  showWorkspaceDashboard(workspace);
}

async function loadWorkspaceData(workspaceId) {
  // Fetch retrospectives
  const retros = await fetch(`/api/v1/retrospectives/workspace/${workspaceId}`);
  
  // Fetch members
  const members = await fetch(`/api/v1/workspaces/${workspaceId}/members`);
  
  // Update UI
  displayRetrospectives(retros);
  displayMembers(members);
}

function showWorkspaceDashboard(workspace) {
  // Hide login/create workspace modals
  hideAllModals();
  
  // Show main content
  document.getElementById('app-content').style.display = 'block';
  
  // Render dashboard
  renderDashboard(workspace);
}
```

---

## 📊 Available API Endpoints

### **After Workspace Creation, You Can:**

#### **1. Get All Retros in Workspace**
```
GET /api/v1/retrospectives/workspace/{workspace_id}

Response:
[
  {
    "id": 1,
    "title": "Sprint 1 Retro",
    "sprint_name": "Sprint 1",
    "status": "scheduled",
    "current_phase": "input",
    "participant_count": 5,
    ...
  }
]
```

#### **2. Get Workspace Members**
```
GET /api/v1/workspaces/{workspace_id}/members

Response:
[
  {
    "id": 1,
    "user_id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "facilitator"
  }
]
```

#### **3. Create Retrospective**
```
POST /api/v1/retrospectives/
{
  "workspace_id": 1,
  "title": "Sprint 1 Retro",
  "sprint_name": "Sprint 1",
  "scheduled_start_time": "2025-11-01T10:00:00Z",
  "scheduled_end_time": "2025-11-01T11:00:00Z"
}
```

#### **4. Get Action Items**
```
GET /api/v1/action-items/

Response:
[
  {
    "id": 1,
    "title": "Fix login bug",
    "status": "pending",
    "assigned_to": "john@example.com",
    ...
  }
]
```

---

## 🗄️ Data Retrieval from Database

### **How to Get Workspace Data:**

```javascript
// 1. Get workspace info
const workspace = currentWorkspace; // Already stored

// 2. Fetch retrospectives
async function fetchRetrospectives() {
  const response = await fetch(`/api/v1/retrospectives/workspace/${currentWorkspace.id}`, {
    headers: { 'Authorization': `Bearer ${authToken}` }
  });
  return await response.json();
}

// 3. Fetch action items
async function fetchActionItems() {
  const response = await fetch('/api/v1/action-items/', {
    headers: { 'Authorization': `Bearer ${authToken}` }
  });
  return await response.json();
}

// 4. Fetch members
async function fetchMembers() {
  const response = await fetch(`/api/v1/workspaces/${currentWorkspace.id}/members`, {
    headers: { 'Authorization': `Bearer ${authToken}` }
  });
  return await response.json();
}
```

---

## 🎨 Recommended Dashboard UI

### **Workspace Dashboard Should Show:**

```
┌─────────────────────────────────────────────────┐
│ 🏢 Engineering Team                        [⚙️] │
├─────────────────────────────────────────────────┤
│                                                 │
│ 👥 Members: 5                                   │
│ 📊 Retros: 3 (1 scheduled, 2 completed)         │
│ ✅ Action Items: 12 (8 pending, 4 completed)    │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ 📋 RECENT RETROSPECTIVES                        │
│ ┌─────────────────────────────────────────────┐ │
│ │ Sprint 2 Retro | Scheduled | Nov 5, 2025   │ │
│ │ [Start Retro]                               │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ Sprint 1 Retro | Completed | Oct 28, 2025  │ │
│ │ [View Results]                              │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [+ Create New Retrospective]                    │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ ✅ ACTION ITEMS                                 │
│ • Fix authentication bug (High)                 │
│ • Improve performance (Medium)                  │
│ • Add unit tests (Low)                          │
│                                                 │
│ [View All Action Items]                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔑 Key Points

1. **After workspace creation**: User should see their workspace dashboard
2. **Dashboard shows**: Retros, members, action items
3. **Can create**: New retrospectives from dashboard
4. **Data is fetched**: From database via API calls
5. **All data**: Scoped to the current workspace

---

## 💡 Implementation Example

```javascript
// Complete flow
async function handleWorkspaceCreated(workspace) {
  // 1. Store workspace
  currentWorkspace = workspace;
  
  // 2. Fetch all data
  const [retros, members, actionItems] = await Promise.all([
    fetchRetrospectives(),
    fetchMembers(),
    fetchActionItems()
  ]);
  
  // 3. Render dashboard
  renderDashboard({
    workspace: workspace,
    retrospectives: retros,
    members: members,
    actionItems: actionItems
  });
  
  // 4. Hide modals, show app
  hideAllModals();
  showMainApp();
}
```

---

## ✅ Summary

**After workspace creation:**
1. ✅ User should be redirected to workspace dashboard
2. ✅ Dashboard fetches data from database
3. ✅ Shows retros, members, action items
4. ✅ User can create new retrospectives
5. ✅ All data is workspace-scoped

This provides a **complete, actionable flow** for users!
