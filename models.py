from wtforms.fields import datetime

from app import db


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=False)
    shows = db.relationship('Show', backref='Venue', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'Venue: {self.id} {self.name}'

    @property
    def upcoming_shows(self):
        upcoming_shows = [show for show in self.shows if
                          show.start_time > datetime.now()]
        return upcoming_shows

    @property
    def num_upcoming_shows(self):
        return len(self.upcoming_shows)

    @property
    def past_shows(self):
        past_shows = [show for show in self.shows if show.start_time < datetime.now()]
        return past_shows

    @property
    def num_past_shows(self):
        return len(self.past_shows)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='Artist', lazy=True)

    @property
    def upcoming_shows(self):
        upcoming_shows = [show for show in self.shows if show.start_time > datetime.now()]
        return upcoming_shows

    @property
    def num_upcoming_shows(self):
        return len(self.upcoming_shows)

    @property
    def past_shows(self):
        past_shows = [show for show in self.shows if show.start_time < datetime.now()]

        return past_shows

    @property
    def num_past_shows(self):
        return len(self.past_shows)

    def __repr__(self):
        return f'Artist: {self.id} {self.name}'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True, index=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True, index=True)
    start_time = db.Column(db.DateTime, nullable=True)