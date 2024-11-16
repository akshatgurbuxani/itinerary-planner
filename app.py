import streamlit as st
import json
from format_prompt import get_events_string, get_final_prompt
from gemini_prompt import get_response
import re
from datetime import datetime, timedelta



def set_background_image(image_url):
    st.markdown(
        f"""
        <style>
        /* Ensure the background image covers the entire app */
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.6)), url({image_url}); /* Adding a white overlay */
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            min-height: 100vh; /* Ensure minimum height for the background */
        }}


        /* Specific targeting for input placeholders */
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
            color: black; /* Placeholder text color */
        }}

        /* Customizing button to be black */
        .stButton > button {{
            background-color: black !important; /* Button background color */
            color: white !important; /* Button text color */
            border: 1px solid white; /* Adding a subtle white border */
        }}
        .stButton > button:hover {{
            background-color: #333 !important; /* Darker shade on hover */
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def parse_llm_response(response_text):
    """
    Parse the LLM response and extract the JSON content.
    
    Args:
        response_text (str): The raw response from the LLM
        
    Returns:
        dict: Parsed JSON object
    """
    # Extract content between triple backticks and 'json' marker
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, response_text)
    
    if match:
        json_str = match.group(1)
    else:
        # If no backticks, try to find the JSON object directly
        json_str = response_text
    
    try:
        # Clean up any potential formatting issues
        json_str = json_str.strip()
        # Parse the JSON
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None


def get_trip_plan(food_prefs, event_types, budget_range, start_date, end_date):
    user_preference = f"food preferences: {food_prefs}, type of places or events preferred to go: {event_types}, budget range: {budget_range}, start date: {start_date}, end date: {end_date}"
    events_text = get_events_string("events.csv")
    events_free_text = get_events_string("eventsFree.csv")
    events_week_text = get_events_string("eventsWeek.csv")

    events_text = events_text + "\n\n" + events_free_text + "\n\n" + events_week_text + "\n\n"

    # Generate a list of dates between start_date and end_date
    date_list = [(start_date + timedelta(days=i)).strftime("%b %d") for i in range((end_date - start_date).days + 1)]
    
    # Pass date_list to the prompt
    prompt = get_final_prompt(user_preference, events_text, date_list)
    
    response = get_response(prompt)
    plan = parse_llm_response(response)
    return plan


def display_trip_plan(plan):
    # Create tabs for each day in the plan
    days = list(plan.keys())
    tabs = st.tabs(days)  # Create tabs for each day

    for i, day in enumerate(days):
        with tabs[i]:
            st.header(day)
            for time_slot, details in plan[day].items():
                with st.expander(f"{time_slot}: {details['time']}", expanded=True):
                    if 'restaurant' in details:
                        st.markdown(f"""
                            🍽️ **{details['restaurant']}** - {details['cuisine']}  
                            💰 **Price:** {details['price_per_person']}  
                            📍 {details['location']}  
                            ℹ️ {details['details']}
                        """)
                    else:
                        st.markdown(f"""
                            🎯 **{details['activity']}**  
                            💰 **Price:** {details['price_per_person']}  
                            📍 {details['location']}  
                            ℹ️ {details['details']}
                        """)


def main():

    st.set_page_config(page_title="Boston Event Planner", page_icon="📅", layout="wide")  # Move this to the top
    background_image_url = "https://images.unsplash.com/photo-1516803169923-cf5fd5f6858e?q=80&w=2938&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"  # Replace with your image URL
    set_background_image(background_image_url)
    
    
    st.title("🌟 PlanAsYouGo: Real-Time Itinerary Builder")
    st.markdown("We don’t just plan. We make spontaneity look organized.")
    
    st.markdown("---")  # Add a divider
    
    # User Preferences
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🍽️ Food & Budget")
        food_prefs = st.text_input(
            "What are your food preferences?",
            placeholder="e.g., vegetarian, seafood, Italian",
            help="Tell us about your dietary preferences or favorite cuisines"
        )
        
        budget_range = st.select_slider(
            "💰 What's your budget per person for the trip?",
            options=['$0-50', '$50-100', '$100-200', '$200-300', '$300+'],
            value='$100-200'
        )
    
    with col2:
        st.subheader("📅 Trip Dates")
        start_date = st.date_input("Select your start date", datetime.today())
        end_date = st.date_input("Select your end date", datetime.today())
        
        st.subheader("🎯 Interests")
        event_options = [
            "🎨 Arts and Culture",
            "🎵 Music and Nightlife",
            "🍷 Food and Drink",
            "🌳 Outdoor and Recreation",
            "📚 Educational and Workshops",
            "🎪 Seasonal and Special Events",
            "👨‍👩‍👧‍👦 Family and Community"
        ]
        selected_events = st.multiselect(
            "What interests you?",
            event_options,
            help="Select multiple interests to personalize your itinerary"
        )

    # Check the difference between start and end dates
    if (end_date - start_date).days > 10:
        st.warning("⚠️ The difference between the start date and end date should not exceed 10 days.")
    else:
        if st.button("🗓️ Generate Trip Plan", type="primary", use_container_width=True):
            if not food_prefs or not selected_events:
                st.warning("⚠️ Please enter both food preferences and interests")
            else:
                with st.spinner('✨ Creating your perfect trip plan...'):
                    cleaned_events = [event.split(' ', 1)[1] for event in selected_events]
                    trip_plan = get_trip_plan(food_prefs, cleaned_events, budget_range, start_date, end_date)
                    
                    # Display the trip plan using tabs
                    display_trip_plan(trip_plan)


if __name__ == "__main__":
    main() 