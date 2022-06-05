#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import re
import sys
from unicodedata import category
import dateutil.parser
import babel
from flask import abort, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import false
from forms import *
from models import Venue, Artist, app, Show, db, func
from resource.modelschema import VenueSchema, ArtistSchema, ShowSchema, VenueGroupSchema

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venue_city_state = db.session.query(
      Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  venuegroupSchema = VenueGroupSchema()
  data = venuegroupSchema.dump(venue_city_state, many=True)
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  x = False
  search = request.form.get('search_term', '')
  venue_city_state = db.session.query(
      Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  for item in venue_city_state:
    city, state = item
    x = re.search(f"^{city}.+{state}$", search)
    if x:
      break
  if x:
    result = Venue.query.filter(
        Venue.city == city, Venue.state == state).all()
  else:
    result = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()
  marshallowSchemaInstance = VenueSchema()
  data_set = marshallowSchemaInstance.dump(result, many=True)
  data = []
  for item in data_set:
    venue = {
        "id": item['id'],
        "name": item['name'],
        "num_upcoming_shows": item['upcoming_shows_count'],
    }
    data.append(venue)

  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  result = Venue.query.get(venue_id)
  marshallowSchemaInstance = VenueSchema()
  data = marshallowSchemaInstance.dump(result, many=False)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    status = True
    form = request.form.to_dict(flat=False)
    form = {k: form[k][0] if len(form[k]) <= 1 else form[k] for k in form}
    marshallowSchemaInstance = VenueSchema()
    transientData = marshallowSchemaInstance.load(form, session=db.session, many=False)
    db.session.add(transientData)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!', category='message')
  except:
    status - False
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed.', category='error')
    print(sys.exc_info())
  finally:
    db.session.close()
    if status:
      return redirect(url_for('index'))
    else:
      return redirect(url_for('create_venue_form'))


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    status = True
    Show.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ID:' + venue_id +
          ' was successfully deleted!', category='message')
  except:
    db.rollback()
    flash('An error occurred. Venue ID:' +
          venue_id + ' could not be deleted.', category='error')
    print(sys.exc_info)
    status = False
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    if status:
      return redirect(url_for('venues'), 303)
    else:
      return redirect(url_for('edit_venue', venue_id = venue_id, _method='GET'), 303)

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  x = False
  search = request.form.get('search_term', '')
  artist_city_state = db.session.query(
      Artist.city, Artist.state).group_by(Artist.city, Artist.state).all()

  for item in artist_city_state:
    city, state = item 
    x = re.search(f"^{city}.+{state}$", search)
    if x : 
      break
  if x :
    result = Artist.query.filter(Artist.city == city, Artist.state == state).all()
  else:
    result = Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()

  marshallowSchemaInstance = ArtistSchema()
  data_set = marshallowSchemaInstance.dump(result, many=True)
  data = []
  for item in data_set:
    artist = {
        "id": item['id'],
        "name": item['name'],
        "num_upcoming_shows": item['upcoming_shows_count'],
    }
    data.append(artist)

  response = {
      "count": len(data),
      "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  result = Artist.query.get(artist_id)
  marshallowSchemaInstance = ArtistSchema()
  data = marshallowSchemaInstance.dump(result, many=False)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist, seeking_venue = False)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    status = True
    form = request.form.to_dict(flat=False)
    form = {k: form[k][0] if len(form[k]) <= 1 else form[k] for k in form}
    db.session.query(Artist).filter(Artist.id == artist_id).update(
        form, synchronize_session=False)
    db.session.commit()
    flash('Artist ID: ' + str(artist_id) +
          ' was successfully edited!', category='message')
  except:
    status = False
    db.session.rollback()
    flash('An error occurred. Artist ID: ' +
          str(artist_id) + ' could not be edited.', category='error')
    print(sys.exc_info())
  finally:
    db.session.close()
    if status:
      return redirect(url_for('show_artist', artist_id=artist_id))
    else:
      return redirect(url_for('edit_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    status = True
    form = request.form.to_dict(flat=False)
    form = {k: form[k][0] if len(form[k]) <= 1 else form[k] for k in form}
    db.session.query(Venue).filter(Venue.id == venue_id).update(
        form, synchronize_session=False)
    db.session.commit()
    flash('Venue ID: ' + str(venue_id) +
          ' was successfully edited!', category='message')
  except:
    status = False
    db.session.rollback()
    flash('An error occurred. Venue ID: ' +
          str(venue_id) + ' could not be edited.', category='error')
    print(sys.exc_info())
  finally:
    db.session.close()
    if status:
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      return redirect(url_for('edit_venue', venue_id=venue_id))
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    status = True
    form = request.form.to_dict(flat=False)
    form = {k: form[k][0] if len(form[k]) <= 1 else form[k] for k in form}
    marshallowSchemaInstance = ArtistSchema()
    transientData = marshallowSchemaInstance.load(
        form, session=db.session, many=False)
    db.session.add(transientData)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!', category='message')
  except:
    status = False
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' +
          request.form['name'] + ' could not be listed.', category='error')
    print(sys.exc_info())
  finally:
    db.session.close()
    if status:
      return redirect(url_for('index'))
    else:
      return redirect(url_for('create_artist_form'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  result = Show.query.all()
  marshallowSchemaInstance = ShowSchema()
  data = marshallowSchemaInstance.dump(result, many=True)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    status = True
    form =  request.form
    date_time = datetime.strptime(
        request.form['start_time'], "%Y-%m-%d %H:%M:%S")
    show = Show(artist_id =  form['artist_id'],venue_id =  form['venue_id'], datetime = date_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    status = False
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    if status:
      return redirect(url_for('index'))
    else:
      return redirect(url_for('create_shows'))
  


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
