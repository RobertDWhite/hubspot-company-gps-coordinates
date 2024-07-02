import requests
from geopy.geocoders import Nominatim
import googlemaps
import csv

# Set your HubSpot API key here
access_token = "xxxxx"
api_url = "https://api.hubapi.com/crm/v3/objects/companies"

hubspot_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Set up the geolocator
geolocator = Nominatim(user_agent="hubspot_geocoder")

# Function to get all companies from HubSpot
def get_hubspot_companies():
    url = f"{api_url}?properties=address,city,state,zip,country,name"
    all_companies = []
    while url:
        print(f"Fetching data from URL: {url}")
        response = requests.get(url, headers=hubspot_headers)
        if response.status_code != 200:
            print(f"Error fetching data from HubSpot API: {response.status_code} {response.text}")
            break

        data = response.json()
        print(f"Response JSON: {data}")

        if 'results' not in data:
            print(f"'results' key not found in response: {data}")
            break

        companies = data['results']
        all_companies.extend(companies)

        paging = data.get('paging', {})
        next_link = paging.get('next', {}).get('link', None)
        url = next_link if next_link else None

    return all_companies

# Function to get the address of a company
def get_company_address(company):
    properties = company.get('properties', {})
    # Debugging: Print all properties to find the correct address fields
    print(f"Company properties: {properties}")
    address = properties.get('address', '')
    city = properties.get('city', '')
    state = properties.get('state', '')
    zip_code = properties.get('zip', '')
    country = properties.get('country', '')
    full_address = f"{address}, {city}, {state}, {zip_code}, {country}"
    return full_address.strip(', ')

# Function to get GPS coordinates from an address using Geopy
def get_coordinates(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return (None, None)

# Main function to get companies and their GPS coordinates, and export to CSV
def main():
    companies = get_hubspot_companies()
    print(f"Total companies fetched: {len(companies)}")

    company_coords = []
    for company in companies:
        name = company.get('properties', {}).get('name', 'Unknown')
        address = get_company_address(company)
        print(f"Processing company: {name}, Address: {address}")

        if address:
            coords = get_coordinates(address)
            print(f"Coordinates: {coords}")
            company_coords.append({
                'name': name,
                'address': address,
                'latitude': coords[0],
                'longitude': coords[1]
            })

    # Write company coordinates to a CSV file
    with open('company_coordinates.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Address', 'Latitude', 'Longitude'])
        for company in company_coords:
            writer.writerow([company['name'], company['address'], company['latitude'], company['longitude']])

    print("Company coordinates have been exported to 'company_coordinates.csv'")

if __name__ == '__main__':
    main()