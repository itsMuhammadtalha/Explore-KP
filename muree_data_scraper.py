import time
import pandas as pd
import random
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import re
from geopy.geocoders import Nominatim
import concurrent.futures

class SwatHotelDataCollector:
    def __init__(self):
        self.destinations = {
            "Murree": {"lat": 33.9072, "lng": 73.3925},
            "Pindi Point": {"lat": 33.9060, "lng": 73.3920},
            "Mall Road": {"lat": 33.9075, "lng": 73.3928},
            "Patriata": {"lat": 33.9080, "lng": 73.3922},
            "Kashmir Point": {"lat": 33.9065, "lng": 73.3923},
            "Ayubia": {"lat": 33.9110, "lng": 73.3927},
            "Nathiagali": {"lat": 34.0020, "lng": 73.3925}
        }
        self.amenities_pool = [
            "Restaurant", "Free WiFi", "Parking", "Room Service", "24-hour Front Desk", 
            "Airport Shuttle", "Mountain View", "River View", "Terrace", "Garden", 
            "Non-smoking Rooms", "Family Rooms", "Heating", "Tour Desk", "Currency Exchange",
            "Bicycle Rental", "Laundry", "Dry Cleaning", "Ironing Service", "Meeting Facilities",
            "Business Center", "Fax/Photocopying", "Honeymoon Suite", "VIP Room Facilities",
            "Breakfast", "Packed Lunches", "Bar", "Snack Bar", "Special Diet Menus",
            "Indoor Pool", "Outdoor Pool", "Fitness Center", "Spa", "Massage", "Hot Tub", 
            "Turkish Bath", "Solarium", "Sauna", "Games Room", "Library", "Evening Entertainment",
            "Daily Housekeeping", "Luggage Storage", "Safe", "Elevator", "Gift Shop",
            "Bonfire Area", "BBQ Facilities", "Ski Storage", "Car Hire", "Tour Arrangements"
        ]
        self.nearby_attractions = {
            "Murree": ["Mall Road", "Pindi Point", "Kashmir Point", "Patriata Chairlift", "Ayubia National Park"],
            "Pindi Point": ["Pindi Point Viewpoint", "Mushkpuri Trek", "Patriata Chairlift"],
            "Mall Road": ["Shopping Areas", "Restaurants", "Cafes", "Local Markets"],
            "Patriata": ["Chairlift", "Cable Car", "Hiking Trails"],
            "Kashmir Point": ["Viewpoint", "Photography Spots", "Nature Walks"],
            "Ayubia": ["Ayubia National Park", "Hiking Trails", "Bird Watching"],
            "Nathiagali": ["Nathiagali Church", "Mukshpuri Trek", "Dunga Gali"]
        }
        self.hotel_descriptions = [
            "Nestled amidst lush green valleys, this hotel offers spectacular mountain views with traditional architecture and modern amenities.",
            "Located in the heart of {location}, this hotel combines comfort and convenience with easy access to local attractions.",
            "A riverside retreat offering tranquil surroundings and panoramic views of the Swat Valley's natural beauty.",
            "This family-run hotel provides warm hospitality and authentic local experiences, perfect for exploring {location}.",
            "Featuring traditional Swati architecture with modern comforts, this hotel is an ideal base for mountain adventures.",
            "Set against the backdrop of snow-capped peaks, this hotel offers comfortable accommodation with stunning natural vistas.",
            "A cozy mountain lodge providing intimate settings and personalized service for an unforgettable Swat Valley experience.",
            "This boutique hotel combines local charm with contemporary amenities, offering a unique stay in the heart of {location}.",
            "Perched on a hillside with sweeping valley views, this hotel provides a peaceful escape from urban life.",
            "A recently renovated property offering modern facilities while maintaining the cultural heritage of the Swat region."
        ]
        self.user_names = [
            "NatureLover", "MountainExplorer", "PakistanTraveler", "AdventureSoul", "PeacefulWanderer", 
            "ValleyHiker", "KarakoramTrekker", "SwatExplorer", "SerenitySeeker", "MountainView",
            "RiversideWanderer", "HillsAndValleys", "PakVoyager", "NorthernEscapes", "TravelEnthusiast",
            "NomadHeart", "ViewSeeker", "TrailBlazer", "CultureExplorer", "MountainDreamer"
        ]
        self.positive_comments = [
            "Excellent location with breathtaking views of the mountains.",
            "Friendly staff who went above and beyond to make our stay comfortable.",
            "Clean and spacious rooms with all the necessary amenities.",
            "Perfect base for exploring the beautiful Swat Valley.",
            "Great value for money with excellent service.",
            "The food at the hotel restaurant was delicious and authentic.",
            "Comfortable beds and peaceful surroundings for a good night's sleep.",
            "The manager personally helped arrange our local tours.",
            "Stunning views from the terrace - perfect for morning tea.",
            "Warm hospitality that made us feel like family."
        ]
        self.mixed_comments = [
            "Nice property but the Wi-Fi was a bit unreliable.",
            "Good location, though some rooms need updating.",
            "Friendly staff, but service was sometimes slow during busy hours.",
            "Comfortable stay overall, but the bathroom facilities could be improved.",
            "Beautiful views but limited dining options.",
            "Clean rooms, though a bit smaller than expected.",
            "Good value, but hot water was inconsistent.",
            "Helpful staff, though they had limited English proficiency.",
            "Pleasant stay, but the road to reach the hotel is quite rough.",
            "Decent experience, but noise from nearby rooms was sometimes an issue."
        ]
        self.hotel_name_parts = {
            "prefixes": ["Royal", "Grand", "Mountain", "Luxury", "Paradise", "Pearl", "Crystal", "Golden", "Silver", "Green", "Blue", "Riverside", "Valley", "Peak", "Serene", "Crown", "Imperial"],
            "mids": ["View", "Retreat", "Resort", "Lodge", "Inn", "Hotel", "Residency", "Heights", "Palace", "Suites", "Continental", "Plaza", "Hideaway", "Haven", "Comfort"],
            "suffixes": ["& Spa", "& Restaurant", "& Resort", "& Suites", "International", "Deluxe", "Premium", "Exclusive", "Executive"]
        }
        self.image_filenames = [
            "exterior_view.jpg", "lobby.jpg", "standard_room.jpg", "deluxe_room.jpg", 
            "restaurant.jpg", "mountain_view.jpg", "river_view.jpg", "garden.jpg", 
            "terrace.jpg", "reception.jpg", "dining_area.jpg", "suite.jpg", 
            "bathroom.jpg", "lounge.jpg", "conference_room.jpg", "night_view.jpg"
        ]
        self.room_types = [
            "Standard Single Room", "Standard Double Room", "Deluxe Room", 
            "Executive Room", "Family Suite", "Mountain View Room", "River View Room", 
            "Royal Suite", "Economy Room", "Premium Room", "Honeymoon Suite", "Twin Room"
        ]
        self.geolocator = Nominatim(user_agent="swat_tourism_app")

    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options to mimic a real user."""
        chrome_options = Options()
        # Comment out headless mode for debugging
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def random_delay(self, min_seconds=2, max_seconds=5):
        """Add random delay to mimic human behavior."""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def get_coordinates(self, location):
        """Get coordinates for a location using GeoPy."""
        if location in self.destinations:
            return self.destinations[location]
        
        try:
            # Try to get a more precise location
            loc_str = f"{location}, Swat, Khyber Pakhtunkhwa, Pakistan"
            location_info = self.geolocator.geocode(loc_str)
            if location_info:
                return {"lat": location_info.latitude, "lng": location_info.longitude}
        except Exception as e:
            print(f"Error getting coordinates: {str(e)}")
        
        # Return coordinates of a random destination as fallback
        return random.choice(list(self.destinations.values()))

    def generate_price_range(self, location):
        """Generate a realistic price range based on location."""
        base_prices = {
            "Murree": (8000, 15000),
            "Pindi Point": (5000, 12000),
            "Mall Road": (10000, 20000),
            "Patriata": (6000, 11000),
            "Kashmir Point": (5000, 10000),
            "Ayubia": (7000, 13000),
            "Nathiagali": (5000, 10000)
        }
        
        # Get price range for the specific location or use a default range
        low, high = base_prices.get(location, (5000, 15000))
        
        # Add some randomization
        low = int(low * random.uniform(0.8, 1.2))
        high = int(high * random.uniform(0.9, 1.3))
        
        # Round to nearest 500
        low = round(low / 500) * 500
        high = round(high / 500) * 500
        
        return f"{low:,} - {high:,} PKR"

    def generate_phone_number(self):
        """Generate a realistic Pakistani phone number."""
        formats = [
            "+92-{}-{}", # +92-300-1234567
            "0{}-{}", # 0300-1234567
            "+92{}{}" # +923001234567
        ]
        
        # Mobile network codes in Pakistan
        network_codes = ["30", "31", "32", "33", "34", "35", "36", "94", "99"]
        
        format_choice = random.choice(formats)
        network = random.choice(network_codes)
        
        if format_choice == "+92-{}-{}":
            return format_choice.format(network, str(random.randint(1000000, 9999999)))
        elif format_choice == "0{}-{}":
            return format_choice.format(network, str(random.randint(1000000, 9999999)))
        else:  # +92{}{}
            return format_choice.format(network, str(random.randint(10000000, 99999999)))

    def generate_website(self, hotel_name):
        """Generate a plausible website URL for the hotel."""
        domains = ["com", "pk", "net", "travel", "hotels"]
        
        # Clean the hotel name for a URL
        clean_name = hotel_name.lower().replace(" ", "").replace("&", "and")
        clean_name = re.sub(r'[^a-z0-9]', '', clean_name)
        
        domain_choice = random.choice(domains)
        format_options = [
            f"http://www.{clean_name}.{domain_choice}",
            f"https://{clean_name}.{domain_choice}",
            f"http://www.{clean_name}hotel.{domain_choice}",
            f"https://{clean_name}resort.{domain_choice}"
        ]
        
        return random.choice(format_options)

    def generate_email(self, hotel_name):
        """Generate a plausible email for the hotel."""
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", f"{hotel_name.lower().replace(' ', '')}.pk"]
        
        # Clean the hotel name for an email
        clean_name = hotel_name.lower().replace(" ", "").replace("&", "and")
        clean_name = re.sub(r'[^a-z0-9]', '', clean_name)
        
        format_options = [
            f"info@{clean_name}.com",
            f"{clean_name}hotel@gmail.com",
            f"reservations@{clean_name}.pk",
            f"contact@{clean_name}.com",
            f"{clean_name}resort@yahoo.com"
        ]
        
        return random.choice(format_options)

    def get_random_hotel_name(self, location=None):
        """Generate a random hotel name, optionally incorporating the location."""
        prefix = random.choice(self.hotel_name_parts["prefixes"])
        mid = random.choice(self.hotel_name_parts["mids"])
        
        # Decide whether to include a suffix or location
        use_suffix = random.random() < 0.3
        use_location = random.random() < 0.5 and location is not None
        
        if use_suffix:
            suffix = random.choice(self.hotel_name_parts["suffixes"])
            return f"{prefix} {mid} {suffix}"
        elif use_location:
            return f"{prefix} {mid} {location}"
        else:
            return f"{prefix} {mid}"

    def get_random_amenities(self, min_count=4, max_count=10):
        """Get a random selection of amenities."""
        count = random.randint(min_count, max_count)
        return sorted(random.sample(self.amenities_pool, count))

    def get_nearby_attractions(self, location):
        """Get nearby attractions for a specific location."""
        # Find the closest known location in our data
        if location in self.nearby_attractions:
            attractions = self.nearby_attractions[location]
        else:
            # Find best match or use a random location
            attractions = random.choice(list(self.nearby_attractions.values()))
        
        # Return a subset of attractions
        count = random.randint(3, 5)
        return sorted(random.sample(attractions, min(count, len(attractions))))

    def get_description(self, location):
        """Generate a hotel description, incorporating the location."""
        desc = random.choice(self.hotel_descriptions)
        return desc.replace("{location}", location)

    def generate_user_reviews(self, min_reviews=2, max_reviews=5):
        """Generate random user reviews."""
        reviews = []
        num_reviews = random.randint(min_reviews, max_reviews)
        
        for _ in range(num_reviews):
            # Randomize if it's a positive or mixed review
            is_positive = random.random() < 0.7
            comment = random.choice(self.positive_comments if is_positive else self.mixed_comments)
            
            # Generate a rating that aligns with the sentiment
            if is_positive:
                rating = round(random.uniform(4.0, 5.0), 1)
            else:
                rating = round(random.uniform(3.0, 4.0), 1)
            
            reviews.append({
                "user": random.choice(self.user_names),
                "rating": rating,
                "comment": comment
            })
        
        return reviews

    def get_random_images(self, hotel_name, min_count=3, max_count=5):
        """Generate random image filenames."""
        count = random.randint(min_count, max_count)
        
        # Clean hotel name for filename use
        clean_name = re.sub(r'[^a-z0-9]', '_', hotel_name.lower().replace(' ', '_'))
        
        images = []
        selected_images = random.sample(self.image_filenames, count)
        
        for img in selected_images:
            images.append(f"{clean_name}_{img}")
        
        return images

    def get_booking_options(self, min_count=2, max_count=5):
        """Generate random room booking options."""
        count = random.randint(min_count, max_count)
        return sorted(random.sample(self.room_types, count))

    def calculate_average_rating(self, reviews):
        """Calculate average rating from reviews."""
        if not reviews:
            return round(random.uniform(3.5, 4.8), 1)
        
        total = sum(review["rating"] for review in reviews)
        return round(total / len(reviews), 1)

    def enrich_hotel_data(self, basic_hotel):
        """Enrich a basic hotel entry with detailed information."""
        # Extract location or use a random one
        location = basic_hotel.get("location", "").split(",")[0].strip()
        if not location or location == "Pakistan" or location == "Bahrain":
            location = random.choice(list(self.destinations.keys()))
        
        # Keep the original name or generate if it's not useful
        name = basic_hotel.get("name", "")
        if "photo gallery" in name.lower() or not name:
            name = self.get_random_hotel_name(location)
        
        # Generate user reviews
        reviews = self.generate_user_reviews()
        
        # Use provided rating or calculate from reviews, or generate random
        rating = basic_hotel.get("rating")
        if rating is None:
            rating = self.calculate_average_rating(reviews)
        
        # Create the enriched hotel data
        enriched_hotel = {
            "name": name,
            "price_range": self.generate_price_range(location),
            "rating": rating,
            "location": f"{location}, Swat, Khyber Pakhtunkhwa",
            "coordinates": self.get_coordinates(location),
            "description": self.get_description(location),
            "amenities": self.get_random_amenities(),
            "nearby_attractions": self.get_nearby_attractions(location),
            "images": self.get_random_images(name),
            "contact": {
                "phone": self.generate_phone_number(),
                "email": self.generate_email(name),
                "website": self.generate_website(name)
            },
            "booking_options": self.get_booking_options(),
            "user_reviews": reviews
        }
        
        return enriched_hotel

    def scrape_hotel_info(self, url):
        """Attempt to scrape basic hotel info from Expedia or another site."""
        try:
            driver = self.setup_driver()
            print(f"Accessing URL: {url}")
            driver.get(url)
            
            self.random_delay(5, 10)
            
            # Try to accept any cookie dialogs
            try:
                cookie_buttons = driver.find_elements(By.CSS_SELECTOR, 
                    "button[id='onetrust-accept-btn-handler'], button.accept-cookies, button.cookie-consent-accept")
                if cookie_buttons:
                    cookie_buttons[0].click()
                    self.random_delay(1, 3)
            except Exception as e:
                print(f"Cookie handling exception: {str(e)}")
            
            # Try multiple selectors to find hotel containers
            hotel_elements = []
            selectors = [
                "div[data-stid='property-listing-card']",
                "div.uitk-card",
                "div.uitk-card-container",
                "div[data-testid='property-card']",
                "div.HotelCardstyles__HotelCardContainer"
            ]
            
            for selector in selectors:
                hotel_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if hotel_elements:
                    print(f"Found {len(hotel_elements)} hotels using selector: {selector}")
                    break
            
            print(f"Found {len(hotel_elements)} hotel elements")
            
            hotels_data = []
            
            # Get at least some basic data for each hotel
            for hotel_element in hotel_elements:
                try:
                    hotel_data = {}
                    
                    # Extract hotel name
                    name_selectors = ["h2", "h3", "h4", "div[data-stid='content-hotel-title']"]
                    for selector in name_selectors:
                        try:
                            name_elem = hotel_element.find_element(By.CSS_SELECTOR, selector)
                            hotel_data["name"] = name_elem.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    
                    # If we couldn't find a name, skip this hotel
                    if "name" not in hotel_data:
                        continue
                    
                    # Try to get location
                    try:
                        location_elem = hotel_element.find_element(By.CSS_SELECTOR, 
                            "div[data-stid='content-hotel-neighborhood'], span.uitk-text.address")
                        hotel_data["location"] = location_elem.text.strip()
                    except NoSuchElementException:
                        hotel_data["location"] = "Swat, Pakistan"
                    
                    # Try to get rating
                    try:
                        rating_elem = hotel_element.find_element(By.CSS_SELECTOR, 
                            "span.uitk-rating-average, span.uitk-badge-base-text")
                        rating_text = rating_elem.text.strip()
                        if '/' in rating_text:
                            hotel_data["rating"] = float(rating_text.split('/')[0])
                        else:
                            hotel_data["rating"] = float(rating_text)
                    except (NoSuchElementException, ValueError):
                        hotel_data["rating"] = None
                    
                    hotels_data.append(hotel_data)
                    
                except Exception as e:
                    print(f"Error extracting hotel data: {e}")
            
            driver.quit()
            return hotels_data
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []

    def generate_complete_dataset(self, scraped_data=None, num_hotels=15):
        """Generate a complete dataset with detailed hotel information."""
        if scraped_data and len(scraped_data) > 0:
            print(f"Enriching {len(scraped_data)} scraped hotels")
            hotels = [self.enrich_hotel_data(hotel) for hotel in scraped_data]
            
            # If we didn't get enough hotels from scraping, add some generated ones
            if len(hotels) < num_hotels:
                additional_needed = num_hotels - len(hotels)
                print(f"Adding {additional_needed} generated hotels to complete the dataset")
                
                for _ in range(additional_needed):
                    location = random.choice(list(self.destinations.keys()))
                    name = self.get_random_hotel_name(location)
                    basic_hotel = {"name": name, "location": location}
                    hotels.append(self.enrich_hotel_data(basic_hotel))
        else:
            print(f"Generating {num_hotels} hotels from scratch")
            hotels = []
            
            # Use ThreadPoolExecutor for parallel generation
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                
                for _ in range(num_hotels):
                    location = random.choice(list(self.destinations.keys()))
                    basic_hotel = {"name": self.get_random_hotel_name(location), "location": location}
                    futures.append(executor.submit(self.enrich_hotel_data, basic_hotel))
                
                for future in concurrent.futures.as_completed(futures):
                    hotels.append(future.result())
        
        return hotels

if __name__ == "__main__":
    collector = SwatHotelDataCollector()
    
    
    print("Attempting to scrape hotel data...")
    url = "https://www.expedia.com/Hotel-Search?adults=2&children=&destination=Murree%2C%20Punjab%2C%20Pakistan&endDate=2025-03-21&gad_source=1&gclid=CjwKCAiAiaC-BhBEEiwAjY99qGJ9I5N6MC5Sm3cYocwpaLU_9Zk58BJqsF_-7YOe1l8xtKlFnimC6RoCshEQAvD_BwE&isInvalidatedDate=false&latLong=&locale=en_US&mapBounds=&regionId=6141511&semcid=US.UB.GOOGLE.DT-c-EN.HOTEL&semdtl=a114081201015.b1122171723701.g1kwd-253301984.e1c.m1CjwKCAiAiaC-BhBEEiwAjY99qGJ9I5N6MC5Sm3cYocwpaLU_9Zk58BJqsF_-7YOe1l8xtKlFnimC6RoCshEQAvD_BwE.r1b071f7f90b5ba01d07bedab70a81a71f01d17f72acad2a7914a3af3d5ba6f467.c1.j11011084.k1.d1674767317796.h1b.i1.l1.n1.o1.p1.q1.s1.t1.x1.f1.u1.v1.w1&siteid=1&sort=RECOMMENDED&startDate=2025-03-20&theme=&useRewards=false&userIntent=&pwaDialog="
    
    scraped_hotels = collector.scrape_hotel_info(url)
    print(f"Scraped {len(scraped_hotels)} hotels")
    
    # Generate a complete dataset with 20 hotels
    complete_dataset = collector.generate_complete_dataset(scraped_hotels, 20)
    print(f"Generated complete dataset with {len(complete_dataset)} hotels")
    
    # Save the data
    with open("murree_hotels.json", 'w', encoding='utf-8') as f:
        json.dump(complete_dataset, f, ensure_ascii=False, indent=4)
    
    print("Data saved to muree_complete_hotels.json")