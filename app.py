#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
 data=[]
 all_area= Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
 for area in all_area:
  venues_list=[] 
  venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()

  for venue in venues:
   num_upcoming_shows = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.now()).count()
   venues_list.append({
   'id': venue.id,
   'name': venue.name,
   'num_upcoming_shows': num_upcoming_shows })
  data.append({
  'city': area.city,
  'state': area.state,
  'venues': venues_list})
 return render_template('pages/venues.html', areas=data)

  
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 
  search_term= request.form.get('search_term')
  search = "%{}%".format(search_term)  #from stack overflow
  venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.like(search)).all()

  data_venues = []
  for venue in venues:
   num_upcoming_shows = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.now()).count()
   data_venues.append({
   'id': venue.id,
   'name': venue.name,
   'num_upcoming_shows': num_upcoming_shows })
  response = {'data': data_venues,'count': len(venues)}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  
  data = Venue.query.filter(Venue.id == venue_id).first()

  upcoming_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  if len(upcoming_shows) > 0:
   upcoming_shows_info = []
   for upcoming_show in upcoming_shows:
     artist = Artist.query.filter(Artist.id == upcoming_show.artist_id).first()

     upcoming_shows_info.append({
     'artist_id': artist.id,
     'artist_name': artist.name,
     'artist_image_link': artist.image_link,
     'start_time': str(upcoming_show.start_time)})

   data.upcoming_shows = upcoming_shows_info
   data.upcoming_shows_count = len(upcoming_shows_info)

  past_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

  if len(past_shows) > 0:
    past_shows_info = []

    for past_show in past_shows:

     artist = Artist.query.filter(Artist.id == past_show.artist_id).first()

     past_shows_info.append({
     'artist_id': artist.id,
     'artist_name': artist.name,
     'artist_image_link': artist.image_link,
     'start_time': str(past_show.start_time),})

    data.past_shows = past_shows_info
    data.past_shows_count = len(past_shows_info)

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

  error = False
  form = VenueForm()
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  seeking_talent = True if 'seeking_talent' in request.form else False

  try:
   venue = Venue(
   name=name,
   city=city,
   state=state,
   address=address,
   phone=phone,
   genres=genres,
   seeking_talent=seeking_talent)
   db.session.add(venue)
   db.session.commit()
  except():
   error = True
   db.session.rollback()
   print(sys.exc_info())
  finally:
   db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  if error:
   abort(400)
   flash('An error occurred. Venue '+ request.form['name']+ ' could not be listed.')
  # on successful db insert, flash success

  if not error:
   flash('Venue ' + request.form['name'] + ' was successfully listed!')
        
  return render_template('pages/home.html')





@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
 error = False
 try:
  venue = Venue.query.get(venue_id)
  db.session.delete(venue)
  db.session.commit()
 except():
  db.session.rollback()
  error = True
 finally:
  db.session.close()
 if error:
   abort(500)
 else:
   return None

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

 data = []
 artists = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()

 for artist in artists:
   count = db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).count()
   data.append({
   'id': artist.id,
   'name': artist.name,
   'num_upcoming_shows': count })
 return render_template('pages/artists.html', artists=data )



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form['search_term']
  search = "%{}%".format(search_term)

  artists = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.like(search)).all()

  data = []
  for artist in artists:
   num_upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).count()

   data.append({
   'id': artist.id,
   'name': artist.name,
   'num_upcoming_shows': num_upcoming_shows })

  response = {
  'data': data,
  'count': len(artists)}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''), )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


 data = Artist.query.filter(Artist.id == artist_id).first()
 upcoming_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

 if len(upcoming_shows) > 0:
   upcoming_shows_info = []
   
   for upcoming_show in upcoming_shows:
   
     venue = Venue.query.filter(Venue.id == upcoming_show.venue_id).first()
     upcoming_shows_info.append({
     'venue_id': venue.id,
     'venue_name': venue.name,
     'venue_image_link': venue.image_link,
     'start_time': upcoming_show.start_time.strftime('%c')})

   data.upcoming_shows = upcoming_shows_info
   data.upcoming_shows_count = len(upcoming_shows_info)

 past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

 if len(past_shows) > 0:
   past_shows_info = []

   for past_show in past_shows:
     venue = Venue.query.filter(Venue.id == past_show.venue_id).first()
     past_shows_info.append({
     'venue_id': venue.id,
     'venue_name': venue.name,
     'venue_image_link': venue.image_link,
     'start_time': past_show.start_time.strftime('%c')})

   data.past_shows = past_shows_info
   data.past_shows_count = len(past_shows_info)

 return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

  
  
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
 form = ArtistForm()   
 artist = Artist.query.filter(Artist.id == artist_id).first()
 
 form.name.data = artist.name
 form.city.data = artist.city
 form.state.data = artist.state
 form.phone.data = artist.phone
 form.genres.data = artist.genres
 form.image_link.data = artist.image_link
 form.facebook_link.data = artist.facebook_link
 form.website.data = artist.website
 form.seeking_venue.data = artist.seeking_venue
 form.seeking_description.data = artist.seeking_description
 # TODO: populate form with fields from artist with ID <artist_id>
 return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

 error = False

 name = request.form['name']
 city = request.form['city']
 state = request.form['state']
 phone = request.form['phone']
 genres = request.form.getlist('genres')
 image_link = request.form['image_link']
 facebook_link = request.form['facebook_link']
 website = request.form['website']
 seeking_talent = True if 'seeking_talent' in request.form else False
 seeking_description = request.form['seeking_description']

 try:

   artist = Artist.query.get(artist_id)
   artist.name = name
   artist.city = city
   artist.state = state
   artist.phone = phone
   artist.genres = genres
   artist.image_link = image_link
   artist.facebook_link = facebook_link
   artist.website = website
   artist.seeking_talent = seeking_talent
   artist.seeking_description = seeking_description

   db.session.commit()
 except():
   error = True
   db.session.rollback()
   print(sys.exc_info())
 finally:
   db.session.close()

 return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()

  form = VenueForm()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
 
  error = False

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']

  try:
   venue = Venue.query.get(venue_id)

   venue.name = name
   venue.city = city
   venue.state = state
   venue.address = address
   venue.phone = phone
   venue.genres = genres
   venue.image_link = image_link
   venue.facebook_link = facebook_link
   venue.website = website
   venue.seeking_talent = seeking_talent
   venue.seeking_description = seeking_description

   db.session.commit()
  except():
   error = True
   db.session.rollback()
   print(sys.exc_info())
  finally:
   db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))


  

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
 
  error = False
  form = ArtistForm()
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  seeking_venue = True if 'seeking_venue' in request.form else False

  try:
        
   artist = Artist(
   name=name,
   city=city,
   state=state,
   phone=phone,
   genres=genres,
   seeking_venue=seeking_venue)

        
   db.session.add(artist)
   db.session.commit()
  except():
   error = True
   db.session.rollback()
   print(sys.exc_info())
  finally:
   db.session.close()
  # on successful db insert, flash success
 
  if not error:
   flash('Artist ' + request.form['name'] + ' was successfully listed!')    
   
  if error:
   abort(400)
   flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.' )
      
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')
   
 
  
 


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  

  data = []

  shows = db.session.query(Venue.name, Artist.name, Artist.image_link, Show.venue_id, Show.artist_id, Show.start_time ).filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id)

  for show in shows:
    data.append({
    'venue_name': show[0],
    'artist_name': show[1],
    'artist_image_link': show[2],
    'venue_id': show[3],
    'artist_id': show[4],
    'start_time': str(show[5]) 
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

  error = False

   
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  try:

   show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

        
   db.session.add(show)
   db.session.commit()
  except():
   error = True
   db.session.rollback()
   print(sys.exc_info())
  finally:
   db.session.close()

  # on successful db insert, flash success
  
  if not error:
   flash('Show was successfully listed!')
        
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  if error:
   abort(400)
   flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
