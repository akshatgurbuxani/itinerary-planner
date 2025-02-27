import pandas as pd
from gemini_prompt import get_response

def get_events_string(url):

    events_df = pd.read_csv(url)

    formatted_events = []
    for idx, row in events_df.iterrows():
        event_str = f"Event: {row['name']}, Date: {row['start_date']} to {row['end_date']}, Time: {row['start_time']} to {row['end_time']}, Location: {row['location']}, Address: {row['street_address']}, Admission: {row['admission']}, Categories: {row['categories']}, Website: {row['event_website']}, Description: {row['description']}"
        formatted_events.append(event_str)

    # Combine all formatted strings into one big string
    big_string = "\n\n".join(formatted_events)

    return big_string

def get_final_prompt(user_preference, events_text=None, date_list=None):
    events_section = f"\nConsider these upcoming events in Boston:\n{events_text}\n" if events_text else ""
    
    # Create a formatted date string for the prompt
    date_string = ", ".join(date_list) if date_list else ""
    
    # Prepare the response format based on the number of dates
    response_format = ""
    if date_list:
        for date in date_list[:2]:
            response_format += f"""
            "{date}": {{
                "Morning/Lunch/Afternoon/Dinner/Evening": {{
                    "time": "HH:MM AM/PM",
                    "activity" or "restaurant": "name",
                    "location": "street address",
                    "type" or "cuisine": "category",
                    "price_per_person": "$XX" / FREE,
                    "details": "brief description"
                }}
            }},
            """
    
    prompt = f"""Please create a personalized itinerary in Boston for someone interested in {user_preference}. 

Requirements:
1. Include activities for the following dates: {date_string}.
2. Each day should have exactly 5 segments: Morning, Lunch, Afternoon, Dinner, and Evening.
3. Ensure all times are realistic and allow for travel between locations.
4. All locations must be within Boston proper or easily accessible by public transport.
5. Include specific street addresses for all locations.
6. Keep activity descriptions concise (under 100 characters){events_section}

Response Format:
Return ONLY a JSON object with the following structure:
{{
    {response_format}

    // Continue for additional dates as needed

}}


Additional Guidelines:
- Morning activities should start between 9:00 AM and 11:00 AM.
- Lunch times should be between 12:00 PM and 2:00 PM.
- Afternoon activities should be between 2:00 PM and 5:00 PM.
- Dinner times should be between 6:00 PM and 8:00 PM.
- Evening activities should start between 8:00 PM and 10:00 PM.
- Allow reasonable time gaps between activities for travel.
- Ensure restaurants suggested are currently operating.
"""
    return prompt


# def get_final_prompt(user_preference, events_text=None, date_list=None):
#     """
#     Generate a structured prompt for weekend planning in Boston.
    
#     Args:
#         user_preference (str): User's specific interests or preferences
#         events_text (str, optional): Current events happening in Boston
    
#     Returns:
#         str: Formatted prompt for the LLM
#     """

#     # Build the prompt with clear instructions and constraints
#     events_section = f"\nConsider these upcoming events in Boston:\n{events_text}\n" if events_text else ""
    
#     # Create a formatted date string for the prompt
#     date_string = ", ".join(date_list) if date_list else ""

#     prompt = f"""Please create a personalized itinerary in Boston for someone interested in {user_preference}. 

# Requirements:
# 1. Include activities for the following dates: {date_string}.
# 2. Each day should have exactly 5 segments: Morning, Lunch, Afternoon, Dinner, and Evening.
# 3. Ensure all times are realistic and allow for travel between locations.
# 4. All locations must be within Boston proper or easily accessible by public transport.
# 5. Include specific street addresses for all locations.
# 6. Keep activity descriptions concise (under 100 characters){events_section}

# Response Format:
# Return ONLY a JSON object with the following structure:
# {{
#     "{date_list[0]}": {{
#         "Morning/Lunch/Afternoon/Dinner/Evening": {{
#             "time": "HH:MM AM/PM",
#             "activity" or "restaurant": "name",
#             "location": "street address",
#             "type" or "cuisine": "category",
#             "price_per_person": "$XX" / FREE,
#             "details": "brief description"
#         }}
#     }},
#     "{date_list[1]}": {{
#         "Morning/Lunch/Afternoon/Dinner/Evening": {{
#             "time": "HH:MM AM/PM",
#             "activity" or "restaurant": "name",
#             "location": "street address",
#             "type" or "cuisine": "category",
#             "price_per_person": "$XX" / FREE,
#             "details": "brief description"
#         }}
#     }}
#     // Continue for additional dates as needed
# }}

# Additional Guidelines:
# - Morning activities should start between 9:00 AM and 11:00 AM.
# - Lunch times should be between 12:00 PM and 2:00 PM.
# - Afternoon activities should be between 2:00 PM and 5:00 PM.
# - Dinner times should be between 6:00 PM and 8:00 PM.
# - Evening activities should start between 8:00 PM and 10:00 PM.
# - Allow reasonable time gaps between activities for travel.
# - Ensure restaurants suggested are currently operating.
# """

#     return prompt

if __name__ == '__main__':

    event_str = get_events_string("events.csv")
    prompt = get_final_prompt("arts and food", event_str)

    print(prompt)

    print(get_response(prompt))
