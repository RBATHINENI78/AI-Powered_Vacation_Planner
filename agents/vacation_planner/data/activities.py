"""
Activity database with operating hours and booking URLs
"""

ACTIVITY_DATABASE = {
    "Paris": {
        "museums": [
            {
                "name": "Louvre Museum",
                "cost": 17,
                "duration_hours": 3.5,
                "rating": 4.8,
                "opening_hours": "09:00-18:00",
                "closed": "Tuesday",
                "best_time": "Early morning or late afternoon",
                "booking_url": "https://www.ticketlouvre.fr/",
                "address": "Rue de Rivoli, 75001 Paris",
                "tips": "Book timed entry in advance to skip lines"
            },
            {
                "name": "Musée d'Orsay",
                "cost": 16,
                "duration_hours": 2.5,
                "rating": 4.8,
                "opening_hours": "09:30-18:00",
                "closed": "Monday",
                "best_time": "Late afternoon for sunset views",
                "booking_url": "https://www.musee-orsay.fr/en/visit/tickets",
                "address": "1 Rue de la Légion d'Honneur, 75007 Paris",
                "tips": "Thursday evenings open until 21:45"
            },
            {
                "name": "Rodin Museum",
                "cost": 13,
                "duration_hours": 2,
                "rating": 4.6,
                "opening_hours": "10:00-18:30",
                "closed": "Monday",
                "best_time": "Morning",
                "booking_url": "https://www.musee-rodin.fr/en/visit/tickets",
                "address": "77 Rue de Varenne, 75007 Paris",
                "tips": "Beautiful gardens included"
            }
        ],
        "food": [
            {
                "name": "French Cooking Class",
                "cost": 100,
                "duration_hours": 3,
                "rating": 4.9,
                "opening_hours": "10:00-13:00, 15:00-18:00",
                "closed": "None",
                "best_time": "Morning session",
                "booking_url": "https://www.lacuisineparis.com/",
                "address": "80 Quai de l'Hôtel de Ville, 75004 Paris",
                "tips": "Book at least 3 days in advance"
            },
            {
                "name": "Wine Tasting Tour",
                "cost": 80,
                "duration_hours": 3,
                "rating": 4.7,
                "opening_hours": "14:00-17:00, 18:00-21:00",
                "closed": "None",
                "best_time": "Evening session",
                "booking_url": "https://www.o-chateau.com/",
                "address": "68 Rue Jean-Jacques Rousseau, 75001 Paris",
                "tips": "Learn about French wine regions"
            },
            {
                "name": "Market Food Tour",
                "cost": 60,
                "duration_hours": 3,
                "rating": 4.8,
                "opening_hours": "09:30-12:30",
                "closed": "Monday",
                "best_time": "Morning only",
                "booking_url": "https://www.contexttravel.com/paris-food-tours",
                "address": "Various markets in Paris",
                "tips": "Come hungry!"
            }
        ],
        "architecture": [
            {
                "name": "Eiffel Tower",
                "cost": 25,
                "duration_hours": 2.5,
                "rating": 4.7,
                "opening_hours": "09:00-00:45",
                "closed": "None",
                "best_time": "Sunset for best views",
                "booking_url": "https://www.toureiffel.paris/en/rates-opening-times",
                "address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris",
                "tips": "Book summit tickets 2 months ahead"
            },
            {
                "name": "Notre-Dame Area",
                "cost": 0,
                "duration_hours": 1.5,
                "rating": 4.6,
                "opening_hours": "24/7 (exterior)",
                "closed": "None",
                "best_time": "Morning for photos",
                "booking_url": None,
                "address": "6 Parvis Notre-Dame, 75004 Paris",
                "tips": "Cathedral under reconstruction, exterior only"
            },
            {
                "name": "Palace of Versailles",
                "cost": 20,
                "duration_hours": 4.5,
                "rating": 4.7,
                "opening_hours": "09:00-18:30",
                "closed": "Monday",
                "best_time": "Tuesday-Friday morning",
                "booking_url": "https://www.chateauversailles.fr/en/plan-your-visit/tickets-rates",
                "address": "Place d'Armes, 78000 Versailles",
                "tips": "Takes 45min by RER C from Paris"
            }
        ],
        "entertainment": [
            {
                "name": "Seine River Cruise",
                "cost": 15,
                "duration_hours": 1,
                "rating": 4.5,
                "opening_hours": "10:00-22:30",
                "closed": "None",
                "best_time": "Evening for illuminated monuments",
                "booking_url": "https://www.bateauxparisiens.com/",
                "address": "Port de la Bourdonnais, 75007 Paris",
                "tips": "Dinner cruises available for ~€80"
            },
            {
                "name": "Moulin Rouge Show",
                "cost": 100,
                "duration_hours": 2,
                "rating": 4.6,
                "opening_hours": "21:00, 23:00",
                "closed": "None",
                "best_time": "21:00 show",
                "booking_url": "https://www.moulinrouge.fr/en/booking",
                "address": "82 Boulevard de Clichy, 75018 Paris",
                "tips": "Book 2 weeks in advance, dress code smart casual"
            }
        ]
    },
    "Tokyo": {
        "culture": [
            {
                "name": "Senso-ji Temple",
                "cost": 0,
                "duration_hours": 1.5,
                "rating": 4.6,
                "opening_hours": "06:00-17:00",
                "closed": "None",
                "best_time": "Early morning to avoid crowds",
                "booking_url": None,
                "address": "2-3-1 Asakusa, Taito City, Tokyo",
                "tips": "Nakamise shopping street nearby"
            },
            {
                "name": "teamLab Borderless",
                "cost": 30,
                "duration_hours": 2.5,
                "rating": 4.8,
                "opening_hours": "10:00-19:00",
                "closed": "Varies",
                "best_time": "Weekday afternoon",
                "booking_url": "https://www.teamlab.art/e/borderless-azabudai/",
                "address": "Azabudai Hills, Minato City",
                "tips": "Wear white for best photo effects"
            },
            {
                "name": "Tea Ceremony Experience",
                "cost": 40,
                "duration_hours": 1,
                "rating": 4.7,
                "opening_hours": "10:00-17:00",
                "closed": "None",
                "best_time": "Afternoon",
                "booking_url": "https://www.viator.com/Tokyo-tours/Tea-Ceremony",
                "address": "Various locations in Tokyo",
                "tips": "Learn proper etiquette beforehand"
            }
        ],
        "food": [
            {
                "name": "Tsukiji Outer Market",
                "cost": 0,
                "duration_hours": 2,
                "rating": 4.6,
                "opening_hours": "05:00-14:00",
                "closed": "Some Sundays",
                "best_time": "7-9 AM for freshest items",
                "booking_url": None,
                "address": "4-16-2 Tsukiji, Chuo City, Tokyo",
                "tips": "Inner market moved to Toyosu"
            },
            {
                "name": "Ramen Tasting Tour",
                "cost": 70,
                "duration_hours": 3,
                "rating": 4.8,
                "opening_hours": "11:00-14:00, 18:00-21:00",
                "closed": "None",
                "best_time": "Lunch",
                "booking_url": "https://www.airbnb.com/experiences/tokyo-ramen",
                "address": "Various ramen shops",
                "tips": "Try different regional styles"
            },
            {
                "name": "Sushi Making Class",
                "cost": 80,
                "duration_hours": 2,
                "rating": 4.9,
                "opening_hours": "10:00-13:00, 14:00-17:00",
                "closed": "None",
                "best_time": "Lunch class",
                "booking_url": "https://www.airbnb.com/experiences/tokyo-sushi",
                "address": "Various cooking studios",
                "tips": "You'll make and eat 8-10 pieces"
            }
        ]
    },
    "London": {
        "museums": [
            {
                "name": "British Museum",
                "cost": 0,
                "duration_hours": 3.5,
                "rating": 4.8,
                "opening_hours": "10:00-17:00",
                "closed": "None",
                "best_time": "Weekday morning",
                "booking_url": "https://www.britishmuseum.org/visit",
                "address": "Great Russell St, London WC1B 3DG",
                "tips": "Free but donations appreciated"
            },
            {
                "name": "Tate Modern",
                "cost": 0,
                "duration_hours": 2.5,
                "rating": 4.6,
                "opening_hours": "10:00-18:00",
                "closed": "None",
                "best_time": "Late afternoon",
                "booking_url": "https://www.tate.org.uk/visit/tate-modern",
                "address": "Bankside, London SE1 9TG",
                "tips": "Free viewing level on 10th floor"
            }
        ],
        "history": [
            {
                "name": "Tower of London",
                "cost": 30,
                "duration_hours": 3,
                "rating": 4.7,
                "opening_hours": "09:00-17:30",
                "closed": "None",
                "best_time": "Morning for Crown Jewels",
                "booking_url": "https://www.hrp.org.uk/tower-of-london/",
                "address": "London EC3N 4AB",
                "tips": "Yeoman Warder tours every 30 min"
            },
            {
                "name": "Westminster Abbey",
                "cost": 25,
                "duration_hours": 2,
                "rating": 4.6,
                "opening_hours": "09:30-15:30",
                "closed": "Sunday (worship only)",
                "best_time": "Early morning",
                "booking_url": "https://www.westminster-abbey.org/visit-us",
                "address": "20 Deans Yd, London SW1P 3PA",
                "tips": "Audio guide included in ticket"
            }
        ]
    }
}
