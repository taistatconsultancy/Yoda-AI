"""
Calendar service for generating iCal files and managing calendar events
"""

from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta, timezone
from typing import Optional
import pytz


class CalendarService:
    """Service for generating calendar events"""
    
    def generate_calendar_event(
        self,
        title: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        location: str = "YodaAI",
        reminder_minutes: int = 15
    ) -> bytes:
        """
        Generate iCal file for a calendar event
        
        Args:
            title: Event title
            description: Event description
            start_time: Start time (timezone-aware)
            end_time: End time (timezone-aware)
            location: Event location
            reminder_minutes: Minutes before event to send reminder
            
        Returns:
            iCal file content as bytes
        """
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//YodaAI//Retrospective Calendar//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'REQUEST')
        
        # Create event
        event = Event()
        event.add('summary', title)
        event.add('description', description)
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('dtstamp', datetime.now(timezone.utc))
        event.add('location', location)
        event.add('uid', f"{title}-{start_time.isoformat()}@yodaai.com")
        event.add('status', 'CONFIRMED')
        event.add('organizer', 'YodaAI <noreply@yodaai.com>')
        
        # Add reminder
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('trigger', timedelta(minutes=-reminder_minutes))
        alarm.add('description', f'Reminder: {title} starts in {reminder_minutes} minutes')
        
        event.add_component(alarm)
        cal.add_component(event)
        
        # Generate iCal content
        ical_content = cal.to_ical()
        
        # Debug: Check for null bytes
        if b'\x00' in ical_content:
            print("⚠️ Warning: iCal content contains null bytes")
            # Remove null bytes
            ical_content = ical_content.replace(b'\x00', b'')
        
        return ical_content
    
    def generate_retrospective_calendar(
        self,
        retrospective_id: int,
        title: str,
        sprint_name: str,
        start_time: datetime,
        end_time: datetime,
        workspace_name: str,
        facilitator_name: str = None
    ) -> bytes:
        """
        Generate calendar event for a retrospective
        
        Args:
            retrospective_id: Retrospective ID
            title: Retrospective title
            sprint_name: Sprint name
            start_time: Start time (timezone-aware)
            end_time: End time (timezone-aware)
            workspace_name: Workspace name
            facilitator_name: Facilitator name (optional)
            
        Returns:
            iCal file content as bytes
        """
        # Build description
        description = f"Retrospective: {title}\n\n"
        description += f"Sprint: {sprint_name}\n"
        description += f"Workspace: {workspace_name}\n"
        if facilitator_name:
            description += f"Facilitator: {facilitator_name}\n"
        description += f"\nJoin the retrospective at YodaAI to discuss:\n"
        description += f"• What we liked\n"
        description += f"• What we learned\n"
        description += f"• What we lacked\n"
        description += f"• What we longed for"
        
        return self.generate_calendar_event(
            title=f"{title} - Retrospective",
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=f"YodaAI - {workspace_name}",
            reminder_minutes=15
        )
    
    def generate_google_calendar_url(
        self,
        title: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        location: str = "YodaAI"
    ) -> str:
        """
        Generate Google Calendar URL for adding event
        
        Args:
            title: Event title
            description: Event description
            start_time: Start time (timezone-aware)
            end_time: End time (timezone-aware)
            location: Event location
            
        Returns:
            Google Calendar URL
        """
        import urllib.parse
        
        # Format times for Google Calendar (YYYYMMDDTHHMMSSZ)
        start_str = start_time.strftime('%Y%m%dT%H%M%SZ')
        end_str = end_time.strftime('%Y%m%dT%H%M%SZ')
        
        params = {
            'action': 'TEMPLATE',
            'text': title,
            'dates': f"{start_str}/{end_str}",
            'details': description,
            'location': location
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://calendar.google.com/calendar/render?{query_string}"
    
    def parse_datetime(self, dt_string: str) -> datetime:
        """
        Parse datetime string to timezone-aware datetime
        
        Args:
            dt_string: ISO format datetime string
            
        Returns:
            Timezone-aware datetime
        """
        if isinstance(dt_string, str):
            # Try parsing ISO format
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        else:
            dt = dt_string
            
        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
