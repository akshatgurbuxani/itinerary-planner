import requests
from bs4 import BeautifulSoup

import csv
from tqdm import tqdm

def write_events_to_csv(events):
    # Define the CSV file name
    filename = 'eventsWeek.csv'
    
    # Define the field names for the CSV
    fieldnames = ['name', 'start_date', 'start_time', 'end_date', 'end_time', 'location', 'street_address', 'admission', 'categories', 'event_website', 'description']
    
    # Open the file in write mode
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()
        
        # Write event data to CSV file
        for event in tqdm(events):
            # Get detailed event data by scraping each event's page
            event_details = scrape_event_details(event['link']) if "https://www.thebostoncalendar.com/events" in event['link'] else {}

            if event_details:
                        
            # Write the merged data to the CSV
                writer.writerow(event_details)



def find_paragraph_given_str(event_info, x):
    # Loop through each paragraph in the event_info section
    for p_tag in event_info.find_all('p'):
        # Check if 'Admission:' is in the text of the current paragraph
        if x in p_tag.text:
            return p_tag
    return None


def scrape_event_details(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        event_data = {}

        # Locate the container with event details
        event_name = soup.find('div', {'class': 'page-header'})

        # Extracting date and time details - with error handling
        try:
            event_data['name'] = event_name.find('h1').text.strip()

        except AttributeError:
            event_data['name'] = 'Not specified'
        
        # Locate the container with event details
        event_info = soup.find('div', {'id': 'event_info'})
        if not event_info:
            return None
        
            
        
        # Extracting date and time details - with error handling
        try:
            event_data['start_date'] = event_info.find('span', {'id': 'starting_date'}).text.strip()
            

        except AttributeError:
            event_data['start_date'] = 'Not specified'
            
        try:
            event_data['start_time'] = event_info.find('span', {'id': 'starting_time'}).text.strip()
        except AttributeError:
            event_data['start_time'] = 'Not specified'

            
        try:
            event_data['end_date'] = event_info.find('span', {'id': 'ending_date'}).text.strip()
        except AttributeError:
            event_data['end_date'] = 'Not specified'
            
        try:
            event_data['end_time'] = event_info.find('span', {'id': 'ending_time'}).text.strip()
        except AttributeError:
            event_data['end_time'] = 'Not specified'
        
        # Extracting location details
        try:
            event_data['location'] = event_info.find('span', itemprop='name').text.strip()
        except AttributeError:
            event_data['location'] = 'Not specified'
            

        try:
            event_data['street_address'] = event_info.find('span', itemprop='streetAddress').text.strip()
        except AttributeError:
            event_data['street_address'] = 'Not specified'
        
        # Extracting admission fee
        try:
            admission_p = find_paragraph_given_str(event_info, 'Admission:')
            if admission_p:
                event_data['admission'] = admission_p.text.split('Admission:')[1].strip() if 'Admission:' in admission_p.text else 'Not specified'
            else:
                event_data['admission'] = 'Not specified'
        except AttributeError:
            event_data['admission'] = 'Not specified'

        
        # Extracting categories
        try:
            categories_p = find_paragraph_given_str(event_info, 'Categories:')
            if categories_p:
                event_data['categories'] = categories_p.text.replace('Categories:', '').strip()
            else:
                event_data['categories'] = 'Not specified'
        except AttributeError:
            event_data['categories'] = 'Not specified'
        
        # Extracting event website
        try:
            website_p = find_paragraph_given_str(event_info, 'Event website:')
            event_data['event_website'] = website_p.find('a')['href'].strip()
        except AttributeError:
            event_data['event_website'] = 'Not specified'

        # Locate the main event container
        event_info = soup.find('div', {'id': 'event_info'})
        event_description_div = soup.find('div', {'id': 'event_description'})

        # Process event description if available
        if event_description_div:
            # Extract all text elements, ignoring empty paragraphs
            event_data['description'] = ' '.join([p.text.strip() for p in event_description_div.find_all('p') if p.text.strip()])
        else:
            event_data['description'] = 'No description available.'

        return event_data
              
    except Exception as e:
        print(f"Error scraping event details from {url}: {str(e)}")
        return None
        
def scrape_events(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Assuming 'div' with id 'event_description' contains the event details
    event_descriptions = soup.find('div', {'id': 'event_description'}).find_all('p')
    
    for event in event_descriptions:
        links = event.find_all('a', target="_blank")
        for link in links:
            title = link.text.strip() if link.text.strip() else "No Title"
            href = link['href']
            events.append({
                'title': title,
                'link': href
            })

    return events


# Example usage:
events_info = scrape_events('https://www.thebostoncalendar.com/events/73-free-things-to-do-in-boston-this-week-nov-12-17-2024')
write_events_to_csv(events_info)