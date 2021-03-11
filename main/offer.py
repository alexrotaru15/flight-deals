from flask_mail import Message
from datetime import datetime, timedelta
from main import mail
from main.utils import cities, get_iata_code, get_flights_data
from main.models import Users, Destinations

TOMORROW = datetime.now() + timedelta(days=1)
SIX_MONTHS_INTERVAL = datetime.now() + timedelta(days=6 * 30)


class SendFlightOffer:
    def __init__(self, user):
        self.user = user

    def send_email(self, final_email):
        msg = Message('Oferta zboruri', sender="testpythonemail3@gmail.com",
                      recipients=[self.user.email])
        msg.body = "Oferta zboruri"
        msg.html = final_email
        mail.send(msg)

    def create_email_form(self):
        destinations_data = []
        links = []
        email_section = []
        cities = Destinations.query.filter_by(user_id=self.user.id).all()
        for city in cities:
            check_flight = get_flights_data(self.user.home_iata, city.iata_code,
                                            TOMORROW.strftime("%d/%m/%Y"), SIX_MONTHS_INTERVAL.strftime("%d/%m/%Y"), city.min_no_days, city.max_no_days, city.max_price)
            destinations_data.append(check_flight)
            links.append(
                f"https://www.google.com/flights?hl=ro#flt={self.user.home_iata}.{city.iata_code}.{check_flight.departure_date}*{city.iata_code}.{self.user.home_iata}.{check_flight.arival_date}")

        for dest in destinations_data:
            email_section.append(
                f"""<p>Oraș plecare: {dest.origin_city}</p>
<p>Destinație: {dest.destination_city}</p>
<p>Dată plecare: {dest.departure_date}</p>
<p>Dată revenire: {dest.arival_date}</p>
<p>Preț: {dest.price} RON</p>
<p>link:{links[destinations_data.index(dest)]}</p><br>
""")
        final_email = ' '.join(email_section)
        self.send_email(final_email)
