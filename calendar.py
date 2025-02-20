import streamlit as st
from O365 import Account
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from streamlit_calendar import calendar

# MongoDB setup
def get_mongo_collection():
    client = MongoClient('mongodb://localhost:27017/')
    return client['calendar_db']['events']

# Outlook setup
def get_outlook_account():
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    account = Account((client_id, client_secret))
    if not account.is_authenticated:
        account.authenticate()
    return account

def fetch_outlook_events(account):
    schedule = account.schedule()
    calendar = schedule.get_default_calendar()
    
    start = datetime.now(pytz.UTC)
    end = start + timedelta(days=30)
    events = calendar.get_events(start=start, end=end, include_recurring=True)
    
    event_list = []
    for event in events:
        event_type = 'Patching' if 'patch' in event.subject.lower() else \
                    'Deployment' if 'deploy' in event.subject.lower() else \
                    'Release' if 'release' in event.subject.lower() else \
                    'Certificate' if 'certificate' in event.subject.lower() else 'Other'
        
        event_data = {
            'event_id': event.object_id,
            'title': f"[{event_type}] {event.subject}",
            'start': event.start.isoformat(),
            'end': event.end.isoformat(),
            'description': event.body.content if event.body else '',
            'location': event.location.get('displayName', '') if event.location else '',
            'organizer': event.organizer.address if event.organizer else '',
            'type': event_type
        }
        event_list.append(event_data)
    return event_list

def store_events(collection, events):
    for event in events:
        collection.update_one(
            {'event_id': event['event_id']},
            {'$set': event},
            upsert=True
        )

def get_calendar_events(collection):
    events = list(collection.find({}, {'_id': 0}))
    # Format events for streamlit-calendar
    calendar_events = []
    for event in events:
        calendar_events.append({
            'id': event['event_id'],
            'title': event['title'],
            'start': event['start'],
            'end': event['end'],
            'extendedProps': {
                'description': event['description'],
                'location': event['location'],
                'organizer': event['organizer'],
                'type': event['type']
            }
        })
    return calendar_events

def main():
    st.title('Infrastructure Event Calendar')
    
    collection = get_mongo_collection()
    
    # Refresh events button
    if st.button('Refresh Calendar Events'):
        with st.spinner('Fetching events from Outlook...'):
            account = get_outlook_account()
            events = fetch_outlook_events(account)
            store_events(collection, events)
            st.success('Calendar events updated successfully!')
    
    # Event type filter
    event_types = ['All', 'Patching', 'Deployment', 'Release', 'Certificate', 'Other']
    selected_type = st.selectbox('Filter by event type:', event_types)
    
    # Get events and filter if needed
    events = get_calendar_events(collection)
    if selected_type != 'All':
        events = [e for e in events if e['extendedProps']['type'] == selected_type]
    
    # Calendar options
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "editable": False,
        "displayEventTime": True,
        "eventClick": True
    }
    
    # Render calendar
    calendar_data = calendar(events=events, options=calendar_options)
    
    # Display event details when clicked
    if calendar_data.get("eventClick"):
        event_id = calendar_data["eventClick"]["event"]["id"]
        event = next((e for e in events if e["id"] == event_id), None)
        if event:
            with st.sidebar:
                st.header("Event Details")
                st.write(f"**Title:** {event['title']}")
                st.write(f"**Type:** {event['extendedProps']['type']}")
                st.write(f"**Location:** {event['extendedProps']['location']}")
                st.write(f"**Organizer:** {event['extendedProps']['organizer']}")
                st.write("**Description:**")
                st.write(event['extendedProps']['description'])

if __name__ == "__main__":
    main()
