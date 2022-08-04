#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime, timedelta
from models import db, Venue, Artist, Show
from seeder import init_data
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
app.cli.add_command(init_data)

# TODO: connect to a local postgresql database

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
  limit = 10
  artists = Artist.query.order_by(db.desc(Artist.id)).limit(limit)
  venues = Venue.query.order_by(db.desc(Venue.id)).limit(limit)
  return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  cities = Venue.query.options(db.load_only('city', 'state')).distinct('city')
  for city in cities:
    
    venues = Venue.query.filter(Venue.city==city.city).order_by(Venue.id).all()
    city_venues = []
    for venue in venues:
      num_upcoming_shows = Show.query.join(Venue, Show.venue_id == Venue.id).filter(Show.start_time>datetime.now()).count()
      #num_upcoming_shows = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).count()
      city_venues.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows,
      })
    data.append({
      "city": city.city,
      "state": city.state,
      "venues": city_venues
    })
   
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  venues = Venue.query.filter(db.or_(
                                  Venue.name.ilike('%' + search_term + '%'),
                                  Venue.city.like('%' + search_term + '%'),
                                  Venue.state.like('%' + search_term + '%'),
                                )).all()
  
  data = []
  
  for venue in venues:
      num_upcoming_shows = Show.query.join(Venue, Show.venue_id==Venue.id).filter(Show.start_time>datetime.now()).count()
      
      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows,
      })
      
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.options(
      db.load_only(
      'id',
      'name',
      'genres',
      'city',
      'address',
      'state',
      'phone',
      'facebook_link',
      'seeking_talent',
      'seeking_description',
      'image_link',
      'website_link',
    )
  ).get(venue_id)
  
  past_shows = []
  upcoming_shows = []
  
  shows = Show.query.join(Artist).add_columns(
    Artist.id.label("artist_id"),
    Artist.name.label("artist_name"),
    Artist.image_link.label("artist_image_link"),
    Show.start_time.label("start_time")
  ).filter(Show.venue_id==venue.id).all();
  
  for show in shows:
    if show.start_time < datetime.now():
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist_image_link,
        "start_time": show.start_time.isoformat(),
      })
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist_image_link,
        "start_time": show.start_time.isoformat(),
      })
  
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(","),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "website": venue.website_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

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
  form = VenueForm(formdata=request.form)
  venue = {}
  is_valid = True
  try:
    venue = Venue()
    if form.validate():
      form.populate_obj(venue)
      venue.genres = ', '.join(form.genres.data)
      
      db.session.add(venue)
      db.session.commit()
    
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      is_valid = False
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  except:
    db.session.rollback()
    
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if is_valid:
    return redirect(url_for('index'))
  else:
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    for show in venue.shows:
      db.session.delete(show)
      
    db.session.delete(venue)
    db.session.commit()
    
    flash('Venue ' + name + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  data = Artist.query.order_by(Artist.id).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  artists = Artist.query.filter(db.or_(
                                  Artist.name.ilike('%' + search_term + '%'),
                                  Artist.city.like('%' + search_term + '%'),
                                  Artist.state.like('%' + search_term + '%'),
                                )).all()
  data = []
  
  for artist in artists:
      #num_upcoming_shows = Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).count()
      num_upcoming_shows = Show.query.join(Artist, Show.artist_id == Artist.id).filter(Show.start_time>datetime.now()).count()
      
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": num_upcoming_shows,
      })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.options(
      db.load_only(
      'id',
      'name',
      'genres',
      'city',
      'state',
      'phone',
      'website_link',
      'facebook_link',
      'seeking_venue',
      'seeking_description',
      'image_link',
    )
  ).get(artist_id)
  
  past_shows = []
  upcoming_shows = []
  shows = Show.query.join(Venue).add_columns(
    Venue.id.label("venue_id"),
    Venue.name.label("venue_name"),
    Venue.image_link.label("venue_image_link"),
    Show.start_time.label("start_time")
  ).filter(Show.artist_id==artist.id).all();
  
  for show in shows:
    if show.start_time < datetime.now():
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue_name,
        "venue_image_link": show.venue_image_link,
        "start_time": show.start_time.isoformat(),
      })
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue_name,
        "venue_image_link": show.venue_image_link,
        "start_time": show.start_time.isoformat(),
      })
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(","),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  form.genres.data=artist.genres 
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(formdata=request.form)
  artist = {}
  is_valid = True
  try:
    artist = Artist.query.get(artist_id)
    if form.validate():
      form.populate_obj(artist)
      artist.genres = ', '.join(form.genres.data)
      
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    else:
      is_valid = False
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  if is_valid:
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
      return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  form.genres.data = venue.genres
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(formdata=request.form)
  venue = {}
  is_valid = True
  try:
  
    venue = Venue.query.get(venue_id)
    if form.validate():
      form.populate_obj(venue)
      venue.genres = ', '.join(form.genres.data)
    
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    else:
      is_valid = False
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  if is_valid:
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(formdata=request.form)
  artist = {}
  is_valid = True
  try:
    artist = Artist()
    if form.validate():
      form.populate_obj(artist)
      artist.genres = ', '.join(form.genres.data)
 
      db.session.add(artist)
      db.session.commit()
    
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      is_valid = False
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if is_valid:
     return redirect(url_for('index'))
  else:
    return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.join(Venue).join(Artist).add_columns(
    Venue.id.label("venue_id"),
    Venue.name.label("venue_name"),
    Artist.id.label("artist_id"),
    Artist.name.label("artist_name"),
    Artist.image_link.label("artist_image_link"),
    Show.start_time.label("start_time")
  ).order_by(Show.id).all()
  
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.start_time.isoformat(),
    })
    
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
  form = ShowForm(formdata=request.form)
  show = {}
  is_valid = True
  try:
    show = Show()
    
    if form.validate():
      form.populate_obj(show)
        
      db.session.add(show)
      db.session.commit()
        
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    else:
      is_valid = False
      flash('An error occurred. Show could not be listed.')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  if is_valid:
    return redirect(url_for('index'))
  else:
    return render_template('forms/new_show.html', form=form)

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
