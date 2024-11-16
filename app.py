import streamlit as st
import json
from format_prompt import get_events_string, get_final_prompt
from gemini_prompt import get_response
import re


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


def get_weekend_plan(food_prefs, event_types, budget_range):
    # This is a placeholder that simulates the LLM response
    # Later, replace this with actual LLM API call

    user_preference = f"food preferences: {food_prefs}, type of places or events preferred to go: {event_types} and budget range: {budget_range}"
    events_text = get_events_string("events.csv")
    prompt = get_final_prompt(user_preference, events_text)

    response = get_response(prompt)
    plan = parse_llm_response(response)


    # sample_plan = {
    #     "Saturday": {
    #         "Morning": {
    #             "time": "10:00 AM",
    #             "activity": "Museum of Fine Arts Exhibition",
    #             "location": "465 Huntington Avenue",
    #             "details": "Special Exhibition on Modern Art"
    #         },
    #         "Lunch": {
    #             "time": "1:00 PM",
    #             "restaurant": "Toro",
    #             "cuisine": "Spanish",
    #             "location": "1704 Washington St",
    #             "details": "Barcelona-style tapas restaurant"
    #         },
    #         "Afternoon": {
    #             "time": "3:00 PM",
    #             "activity": "Boston Public Garden",
    #             "location": "4 Charles St",
    #             "details": "Swan boat rides and garden tours"
    #         },
    #         "Dinner": {
    #             "time": "7:00 PM",
    #             "restaurant": "Neptune Oyster",
    #             "cuisine": "Seafood",
    #             "location": "63 Salem St",
    #             "details": "Famous for fresh seafood and lobster rolls"
    #         },
    #         "Evening": {
    #             "time": "9:00 PM",
    #             "activity": "Live Jazz at Beehive",
    #             "location": "541 Tremont St",
    #             "details": "Live music and cocktails"
    #         }
    #     },
    #     "Sunday": {
    #         "Morning": {
    #             "time": "11:00 AM",
    #             "activity": "SoWa Open Market",
    #             "location": "460 Harrison Ave",
    #             "details": "Local artisans and food vendors"
    #         },
    #         "Lunch": {
    #             "time": "1:30 PM",
    #             "restaurant": "Time Out Market",
    #             "cuisine": "Food Hall",
    #             "location": "401 Park Drive",
    #             "details": "Multiple local food vendors"
    #         },
    #         "Afternoon": {
    #             "time": "3:30 PM",
    #             "activity": "Freedom Trail Walk",
    #             "location": "Boston Common",
    #             "details": "Historical walking tour"
    #         },
    #         "Dinner": {
    #             "time": "6:30 PM",
    #             "restaurant": "Giacomo's",
    #             "cuisine": "Italian",
    #             "location": "355 Hanover St",
    #             "details": "Popular North End Italian restaurant"
    #         },
    #         "Evening": {
    #             "time": "8:00 PM",
    #             "activity": "Sunset Harbor Cruise",
    #             "location": "Long Wharf",
    #             "details": "Evening harbor tour with city views"
    #         }
    #     }
    # }
    return plan

def main():
    st.set_page_config(page_title="Boston Weekend Planner", page_icon="📅", layout="wide")
    
    # Add a small markdown to reduce space above the title
    st.markdown("<style>h1 {margin-top: -50px;}</style>", unsafe_allow_html=True)
    
    st.title("🌟 Boston Weekend Planner")
    st.markdown("Plan your perfect weekend in Boston with personalized activities and dining recommendations!")
    
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
        
        # Minimal vertical space
        st.markdown("")  # Add minimal vertical space
        
        budget_range = st.select_slider(
            "💰 What's your budget per person for the weekend?",
            options=['$0-50', '$50-100', '$100-200', '$200-300', '$300+'],
            value='$100-200'
        )
    
    with col2:
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

    # Minimal vertical space
    st.markdown("")  # Add minimal vertical space
    
    if st.button("🗓️ Generate Weekend Plan", type="primary", use_container_width=True):
        if not food_prefs or not selected_events:
            st.warning("⚠️ Please enter both food preferences and interests")
        else:
            with st.spinner('✨ Creating your perfect weekend plan...'):
                # Clean up selected events (remove emojis for processing)
                cleaned_events = [event.split(' ', 1)[1] for event in selected_events]
                weekend_plan = get_weekend_plan(food_prefs, cleaned_events, budget_range)
            
            # Display the weekend plan
            tab1, tab2 = st.tabs(["Saturday", "Sunday"])
            
            with tab1:
                st.header("Saturday")
                for time_slot, details in weekend_plan["Saturday"].items():
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

            with tab2:
                st.header("Sunday")
                for time_slot, details in weekend_plan["Sunday"].items():
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

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center'>
            <p>🌟 Plan your perfect Boston weekend! 🌟</p>
            <p style='font-size: small'>Recommendations based on real-time events and attractions</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 