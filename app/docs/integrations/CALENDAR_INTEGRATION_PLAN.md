# 📅 Calendar Integration for Retrospective Notifications

## Overview

Users need calendar integration to:
1. ✅ **Schedule retrospectives** with proper calendar events
2. ✅ **Send notifications** when retro starts
3. ✅ **Send reminders** before the retro
4. ✅ **Block calendar time** for the session

---

## 🎯 Implementation Options

### **Option A: Google Calendar (Recommended for MVP)**

**Pros:**
- ✅ Most users have Gmail/Google accounts
- ✅ Google Calendar API is well-documented
- ✅ Can create events programmatically
- ✅ Can send reminders automatically

**Cons:**
- Requires Google OAuth (we already have Google Sign-In!)

**Implementation:**
```python
# Backend: Create calendar event
POST /api/v1/retrospectives/{id}/add-calendar-event
{
  "calendar_type": "google",  # google, outlook, etc.
  "access_token": "..."
}
```

### **Option B: iCal/ICS File Download**

**Pros:**
- ✅ Works with all calendar apps (Google, Outlook, Apple)
- ✅ No OAuth needed
- ✅ Simple to implement
- ✅ Users manually add to calendar

**Cons:**
- Can't send automatic reminders
- User has to add manually

**Implementation:**
```python
# Backend: Generate iCal file
GET /api/v1/retrospectives/{id}/download-calendar
# Returns .ics file that user downloads
```

### **Option C: Email Notifications (Hybrid)**

**Pros:**
- ✅ No calendar integration needed
- ✅ Works immediately
- ✅ We already have email setup

**Cons:**
- Doesn't block calendar
- Not as integrated

**Implementation:**
- Send email with calendar link
- Send reminder emails

---

## 🚀 Recommended Approach: Hybrid

Use **Option B (iCal download) + Option C (Email notifications)** for MVP:

### **When User Creates Retrospective:**

```
1. User fills out retro form:
   - Title: "Sprint 1 Retro"
   - Start time: Nov 5, 2025 at 2:00 PM
   - End time: Nov 5, 2025 at 3:00 PM

2. Backend creates retrospective ✅

3. Backend sends email with:
   - Calendar invite (.ics file attached)
   - Direct "Add to Calendar" link
   - Reminder: "We'll send you a reminder 15 min before"

4. User clicks "Add to Calendar" → Opens in their calendar app

5. At scheduled time - 15 min:
   - Backend sends reminder email
   - "Your retrospective starts in 15 minutes!"

6. At scheduled time:
   - Backend sends start notification
   - "Your retrospective is starting now!"
```

---

## 📧 Email with Calendar Invite

### **Email Template:**

```
Subject: Sprint 1 Retrospective - Scheduled for Nov 5, 2:00 PM

Hi John,

Your retrospective "Sprint 1 Retro" has been scheduled!

📅 Date: November 5, 2025
🕐 Time: 2:00 PM - 3:00 PM
📍 Workspace: Engineering Team

[Add to Google Calendar]  [Add to Outlook]  [Download .ics file]

We'll send you a reminder 15 minutes before it starts.

See you there!
The YodaAI Team
```

---

## 💻 Implementation

### **Backend: Generate iCal File**

```python
# app/services/calendar_service.py

from icalendar import Calendar, Event
from datetime import datetime
import pytz

def generate_calendar_event(retrospective):
    """Generate .ics file for retrospective"""
    cal = Calendar()
    event = Event()
    
    event.add('summary', retrospective.title)
    event.add('description', f"Retrospective: {retrospective.sprint_name}")
    event.add('dtstart', retrospective.scheduled_start_time)
    event.add('dtend', retrospective.scheduled_end_time)
    event.add('location', f"YodaAI - {retrospective.workspace.name}")
    
    # Add reminder
    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('trigger', timedelta(minutes=-15))
    alarm.add('description', 'Reminder: Retrospective starts in 15 minutes')
    
    event.add_component(alarm)
    cal.add_component(event)
    
    return cal.to_ical()

def send_calendar_invite_email(retrospective, participants):
    """Send email with calendar invite"""
    ics_content = generate_calendar_event(retrospective)
    
    email_service = EmailService()
    for participant in participants:
        email_service.send_email(
            to_email=participant.email,
            subject=f"{retrospective.title} - Calendar Invite",
            html_content=generate_invite_email_html(retrospective),
            attachments=[('event.ics', ics_content, 'text/calendar')]
        )
```

### **API Endpoint:**

```python
# app/api/routes/retrospectives_full.py

@router.get("/{retro_id}/calendar")
async def download_calendar_file(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download .ics calendar file for retrospective"""
    retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
    
    if not retro:
        raise HTTPException(status_code=404, detail="Retrospective not found")
    
    # Generate iCal file
    calendar_service = CalendarService()
    ics_content = calendar_service.generate_calendar_event(retro)
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=retro_{retro_id}.ics"
        }
    )
```

---

## ⏰ Reminder System

### **Background Task (Cron Job):**

```python
# app/services/reminder_service.py

async def send_retrospective_reminders():
    """Send reminders 15 minutes before retrospectives"""
    now = datetime.now(timezone.utc)
    reminder_time = now + timedelta(minutes=15)
    
    # Find retrospectives starting in 15 minutes
    retros = db.query(Retrospective).filter(
        Retrospective.status == 'scheduled',
        Retrospective.scheduled_start_time >= now,
        Retrospective.scheduled_start_time <= reminder_time
    ).all()
    
    for retro in retros:
        # Send reminder to all participants
        participants = get_retro_participants(retro.id)
        send_reminder_emails(retro, participants)

# Run every minute
# Using APScheduler or similar
```

---

## 📋 Step-by-Step Flow

### **1. User Creates Retro:**

```javascript
// Frontend: Create retrospective
POST /api/v1/retrospectives/
{
  "workspace_id": 1,
  "title": "Sprint 1 Retro",
  "sprint_name": "Sprint 1",
  "scheduled_start_time": "2025-11-05T14:00:00Z",
  "scheduled_end_time": "2025-11-05T15:00:00Z"
}

// Backend responds with retrospective ID
```

### **2. Backend Auto-Sends Invites:**

```python
# Backend automatically:
# 1. Generates iCal file
# 2. Sends email to all workspace members
# 3. Schedules reminder task
```

### **3. User Receives Email:**

```
"📅 Add to Calendar" button → Downloads .ics file
User opens file → Calendar event added ✅
```

### **4. 15 Min Before Start:**

```
Reminder email: "Your retrospective starts in 15 minutes!"
```

### **5. At Start Time:**

```
Notification: "Your retrospective is starting now!"
Link to join: http://yodaai.com/retro/123
```

---

## 🔧 Dependencies to Add

```bash
pip install icalendar
pip install apscheduler  # For reminder scheduling
```

---

## ✅ MVP Implementation Order

1. ✅ **Generate iCal file** - Basic calendar event
2. ✅ **Email with attachment** - Send .ics file
3. ✅ **Reminder system** - Background task
4. ⏳ **Google Calendar API** - Future enhancement
5. ⏳ **Outlook integration** - Future enhancement

---

## 📧 Email Templates Needed

1. **Calendar Invite Email** - With .ics attachment
2. **Reminder Email** - 15 min before
3. **Start Notification** - Right when it starts

---

## 🎯 Summary

**For MVP, we recommend:**

1. **iCal file generation** - Works with all calendars
2. **Email with .ics attachment** - Automatic invite
3. **Reminder emails** - 15 min before
4. **Start notification** - Right at start time

**No OAuth needed!** Works with every calendar app.

---

## Next Steps

1. Install `icalendar` package
2. Create calendar service
3. Update email templates
4. Add reminder background task
5. Test calendar integration

Want me to implement this? 🚀
