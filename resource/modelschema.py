from ast import Return
from datetime import datetime, timezone, timedelta
from models import ma, db, Venue, Show, Artist
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, SQLAlchemyAutoSchema
from marshmallow import Schema, fields

class VenueGroupSchema(Schema):
    ordered = True
    city = fields.Str()
    state = fields.Str()
    venues = fields.Method('getVenues')

    def getVenues(self, obj):
        venues = []
        venueSet=  Venue.query.filter(Venue.city.like(f'%{obj.city}%'), Venue.state.like(f'%{obj.state}%')).all()
        for venue in venueSet:
            venues.append(
                {
                    'id' : venue.id,
                    'name' : venue.name,
                    'num_upcoming_shows': self.num_upcoming_shows(venue.shows)
                }
            )
        return venues

    def num_upcoming_shows(self, obj):
        shows = [show for show in obj if activeDate(
            show.datetime) == True]
        return len(shows)

class ShowSchema(SQLAlchemySchema):
    class Meta:
        model = Show
        ordered = True
        
    venue_id = ma.Method("venueId")
    venue_name = ma.Method("venueName")
    artist_id = ma.Method("artistId")
    artist_name = ma.Method("artistName")
    artist_image_link = ma.Method("artistImageLink")
    start_time = ma.Method("startTime")

    def venueId(self, obj):
        return obj.venue.id

    def venueName(self, obj):
        return obj.venue.name

    def artistId(self, obj):
        return obj.artist.id

    def artistName(self, obj):
        return obj.artist.name

    def artistImageLink(self, obj):
        return obj.artist.image_link

    def startTime(self, obj):
        return obj.datetime.strftime("%m/%d/%Y, %H:%M:%S")

class VenueSchema(SQLAlchemyAutoSchema):
    upcomingShowsCount = 0
    pastShowsCount = 0
    upcoming_shows = None
    past_shows = None
    class Meta:
        model = Venue
        include_fk = True
        include_relationships = False
        load_instance = True
        ordered = True
    past_shows = ma.Method("pastShows")
    upcoming_shows = ma.Method("upcomingShows")
    upcoming_shows_count = ma.Method("upcomingShowsCount")
    past_shows_count = ma.Method("pastShowsCount")
    # seeking_talent = ma.Method('checkVenueAvailability')

    def pastShows(self, obj):
        shows = [self.mockupShow(show) for show in obj.shows if activeDate(
            show.datetime) == False]
        self.past_shows = shows
        self.pastShowsCount = len(shows)
        return shows

    def upcomingShows(self, obj):
        shows = [self.mockupShow(show) for show in obj.shows if activeDate(
            show.datetime) == True]
        self.upcomingShowsCount = len(shows)
        self.upcoming_shows = shows
        return shows

    def upcomingShowsCount(self, obj):
        return self.upcomingShowsCount
    
    def pastShowsCount(self, obj):
        return self.pastShowsCount

    def checkVenueAvailability(self, obj):
        availaibility = True
        for show in self.upcoming_shows:
            current_time = datetime.now(timezone.utc)
            show['start_time'] = datetime.strptime(
                show['start_time'], "%m/%d/%Y, %H:%M:%S%z")
            show_duration = show['start_time'] + timedelta(hours=1)
            if current_time > show['start_time'] and current_time < show_duration:
                availaibility = False
        return availaibility

    def mockupShow(self, show):
        if show is not None:
            mock_show = {}
            mock_show['artist_id'] = show.artist_id
            mock_show['artist_name'] = show.artist.name
            mock_show['artist_image_link'] = show.artist.image_link
            mock_show['start_time'] = show.datetime.strftime(
                "%m/%d/%Y, %H:%M:%S%z")
            return mock_show
        return None


class ArtistSchema(SQLAlchemyAutoSchema):
    upcomingShowsCount = 0
    upcoming_shows = None
    past_shows = None
    class Meta:
        model = Artist
        include_fk = True
        include_relationships = False
        load_instance = True
        ordered = True
    past_shows = ma.Method("pastShows")
    upcoming_shows = ma.Method("upcomingShows")
    upcoming_shows_count = ma.Method("upcomingShowsCount")
    # seeking_venue = ma.Method('checkArtistAvailability')

    def pastShows(self, obj):
        shows = [self.mockupShow(show) for show in obj.shows if activeDate(
            show.datetime) == False]
        self.past_shows = shows
        return shows

    def upcomingShows(self, obj):
        shows = [self.mockupShow(show) for show in obj.shows if activeDate(
            show.datetime) == True]
        self.upcomingShowsCount = len(shows)
        self.upcoming_shows = shows
        return shows 

    def upcomingShowsCount(self, obj):
        return self.upcomingShowsCount

    def checkArtistAvailability(self, obj):
        availaibility = True
        for show in self.upcoming_shows:
            current_time = datetime.now(timezone.utc)
            show['start_time'] = datetime.strptime(
                show['start_time'], "%m/%d/%Y, %H:%M:%S%z")
            show_duration = show['start_time'] + timedelta(hours=1)
            if current_time > show['start_time'] and current_time < show_duration:
                availaibility = False
        return availaibility

    def mockupShow(self, show):
        if show is not None:
            mock_show = {}
            mock_show['venue_id'] = show.venue_id
            mock_show['venue_name'] = show.venue.name
            mock_show['venue_image_link'] = show.venue.image_link
            mock_show['start_time'] = show.datetime.strftime(
                "%m/%d/%Y, %H:%M:%S%z")
            return mock_show
        return None
      
def activeDate(a):
    """
    compares datetime aware object with current aware utc time
    it checks if the arg1 is lesser than arg 2.

    :param a : datetime.datetime, a datetime in utc you want to evaluate
    :return: boolean, returns True when the date is in the future or False when it is not
    """
    return a > datetime.now(timezone.utc)
def main():
    print('this is Marshmallow schema file, please import it to use it!!!')


if __name__ == "__main__":
    main()