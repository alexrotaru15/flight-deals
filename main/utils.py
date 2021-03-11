import os
import requests

KIWI_ENDPOINT = 'https://tequila-api.kiwi.com'
KIWI_API_KEY = os.environ.get('KIWI_API_KEY')

headers = {
    'apikey': KIWI_API_KEY
}


def get_iata_code(city):
    query = {
        'term': city,
        'location_types': 'city'
    }
    response = requests.get(
        url=f"{KIWI_ENDPOINT}/locations/query", headers=headers, params=query)
    return response.json()['locations'][0]['code']
    # return "OTP"


def get_flights_data(departure, fly_to, date_now, date_six_months, min_no_days, max_no_days, max_price):
    query = {
        "fly_from": departure,
        'fly_to': fly_to,
        'date_from': date_now,
        'date_to': date_six_months,
        'nights_in_dst_from': min_no_days,
        'nights_in_dst_to': max_no_days,
        'flight_type': 'round',
        'one_for_city': 1,
        'curr': 'RON',
        'price_to': max_price,
        'max_stopovers': 1
    }
    # response = requests.get(
    #     url=f"{KIWI_ENDPOINT}/v2/search", headers=headers, params=query)
    response = requests.get(
        url=f"{KIWI_ENDPOINT}/v2/search", headers={
            'apikey': 'fMaIBpz7Nr32ha7PJd-x81qLWljBGzAA'
        }, params=query)
    try:
        data = response.json()['data'][0]
    except IndexError:
        print(f"No flight to {fly_to}")
        return None

    flight_data = FlightData(
        price=data['price'],
        origin_city=data['route'][0]['cityFrom'],
        destination_city=data['route'][0]['cityTo'],
        destination_airport=data['route'][0]['flyTo'],
        departure_date=data["route"][0]["local_departure"].split("T")[0],
        arival_date=data["route"][1]["local_departure"].split("T")[0]
    )
    return flight_data


class FlightData:
    def __init__(self, price, origin_city, destination_city, destination_airport, departure_date, arival_date):
        self.price = price
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.destination_airport = destination_airport
        self.departure_date = departure_date
        self.arival_date = arival_date


cities = ["Moscow", "Saint Petersburg", "Kyiv", "Paris", "Marseille", "Lyon",
          "Toulouse", "Nice", "Nantes", "Montpellier", "Strasbourg", "Bordeaux",
          "Lille", "Madrid", "Barcelona", "Seville", "Valencia", "Zaragoza", "Malaga",
          "Murcia", "Palma", "Las Palmas", "Bilbao", "Stockholm", "Gothenburg", "Malmo",
          "Oslo", "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart",
          "Dusseldorf", "Leipzig", "Dortmund", "Helsinki", "Warsaw", "Krakow", "Rome",
          "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "London",
          "Birmingham", "Glasgow", "Edinburgh", "Leeds", "Liverpool", "Manchester", "Cluj-Napoca",
          "Timisoara", "Iasi", "Minsk", "Almaty", "Athens", "Thessaloniki", "Sofia", "Reykjavik",
          "Budapest", "Lisbon", "Porto", "Braga", "Vienna", "Graz", "Linz", "Salzburg", "Prague",
          "Belgrade", "Dublin", "Vilnius", "Riga", "Zagreb", "Split", "Rijeka", "Sarajevo", "Bratislava",
          "Tallinn", "Copenhagen", "Aarhus", "Zurich", "Geneva", "Basel", "Amsterdam", "Rotterdam",
          "Chisinau", "Brussels", "Antwerp", "Yerevan", "Tirana", "Skopje", "Istanbul", "Ankara", "Ljubljana",
          "Podgorica", "Pristina", "Baku", "Nicosia", "Limassol", "Luxembourg", "Tbilisi", "Andorra la Vella",
          "Valletta", "Doncaster"]
