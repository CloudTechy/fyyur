#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.policy import default
from enum import unique
from tokenize import String
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ARRAY, ForeignKey, func
from flask_marshmallow import Marshmallow

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

# TODO: connect to a local postgresql database
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    """Venue Model"""
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=True)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', back_populates = "venue")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=True)
    seeking_description = db.Column(db.String())
    available_dates = db.Column(ARRAY(db.DateTime(timezone=True)), nullable=True)
    shows = db.relationship('Show', back_populates="artist")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key = True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    datetime = db.Column(db.DateTime(timezone=True), nullable =False)
    venue = db.relationship("Venue", back_populates ="shows" )
    artist = db.relationship("Artist", back_populates ="shows")

    def __repr__(self):
        return f'artist name: {self.artist.name}, venue: {self.venue.name}'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

def main():
    print('this is fyyur model file, please import it to use it!!!')

if __name__ == '__main__':
    main()