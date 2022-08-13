# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import func

from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(session_options={"expire_on_commit": False})
db.init_app(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database
from models import *
# ----------------------------------------------------------------------------#
# Models. Venue, Artist, Show
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

# View for displaying all venues
@app.route('/venues')
def venues():
    data = []
    city_state = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    for cs in city_state:
        city = cs[0]
        state = cs[1]
        venues = Venue.query.filter_by(city=city, state=state).all()
        shows = venues[0].upcoming_shows
        data.append({
            "city": city,
            "state": state,
            "venues": venues,
            "shows": shows
        })

    return render_template('pages/venues.html', areas=data)


# View for displaying all venue searches
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', None)
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.num_upcoming_shows
        })
    count_venues = len(data)
    response = {
        "count": count_venues,
        "data": data
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=search_term)


# Venue view with specific Id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    data = []
    if venue:
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows_count": venue.num_past_shows,
            "upcoming_shows_count": venue.num_upcoming_shows,
        }

    past_shows = []
    for show in venue.past_shows:
        artist = Artist.query.get(show.artist_id)
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })

    upcoming_shows = []
    for show in venue.upcoming_shows:
        artist = Artist.query.get(show.artist_id)
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
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
    venue_form = VenueForm(request.form)
    try:
        venues = Venue(
            name=venue_form.name.data,
            genres=','.join(venue_form.genres.data),
            address=venue_form.address.data,
            city=venue_form.city.data,
            state=venue_form.state.data,
            phone=venue_form.phone.data,
            facebook_link=venue_form.facebook_link.data,
            image_link=venue_form.image_link.data,
            website=venue_form.website_link.data,
            seeking_talent=venue_form.seeking_talent.data,
            seeking_description=venue_form.seeking_description.data)

        db.session.add(venues)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Got an error during insertion')
        abort(400)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Got an error during Deletion of record')
        abort(400)
    else:
        flash('Venue Deleted successfully')
        return render_template('pages/home.html')
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artist = Artist.query.all()
    return render_template('pages/artists.html', artists=artist)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    count_artists = len(artists)
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.num_upcoming_shows
        })

    response = {
        "count": count_artists,
        "data": data
    }

    return render_template('pages/search_artists.html', results=response,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.filter_by(id=artist_id).first()
    if artist == None:
        abort(404)
    past_shows = []
    for show in artist.past_shows:
        venue = Venue.query.get(show.venue_id)
        past_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
        })
    upcoming_shows = []
    for show in artist.upcoming_shows:
        venue = Venue.query.get(show.venue_id)
        upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
        })
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "website_link": artist.website,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": artist.num_past_shows,
        "upcoming_shows_count": artist.num_upcoming_shows
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.filter_by(id=artist_id).first()
    form = ArtistForm(obj=artist)
    if artist == None:
        return f"Artist with id = {artist_id} Does nit exist"
    else:
        return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = form.name.data,
        artist.genres = json.dumps(form.genres.data),  # array json
        artist.city = form.city.data,
        artist.state = form.state.data,
        artist.phone = form.phone.data,
        artist.facebook_link = form.facebook_link.data,
        artist.image_link = form.image_link.data,
        artist.update()
        # on successful db insert, flash success
    except:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    venues = Venue.query.filter_by(id=venue_id).first()
    form = VenueForm(obj=venues)
    if venues == None:
        return f"Venue with id = {venue_id} Does nit exist"
    else:
        return render_template('forms/edit_venue.html', form=form, venue=venues)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    form = VenueForm(request.form)
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = form.name.data,
        venue.address = form.address.data,
        venue.genres = '.'.join(form.genres.data),  # array json
        venue.city = form.city.data,
        venue.state = form.state.data,
        venue.phone = form.phone.data,
        venue.facebook_link = form.facebook_link.data,
        venue.image_link = form.image_link.data,
        venue.website = form.website_link.data,
        venue.seeking_talent = form.seeking_talent.data,
        venue.seeking_description = form.seeking_description.data,

        venue.update()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

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
    artist_form = ArtistForm(request.form)

    try:
        artist = Artist(
            name=artist_form.name.data,
            genres=','.join(artist_form.genres.data),
            city=artist_form.city.data,
            state=artist_form.state.data,
            phone=artist_form.phone.data,
            facebook_link=artist_form.facebook_link.data,
            image_link=artist_form.image_link.data,
            website=artist_form.website_link.data,
            seeking_venue=artist_form.seeking_venue.data,
            seeking_description=artist_form.seeking_description.data)

        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('Got an error during insertion')
        abort(400)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

    # # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # # TODO: on unsuccessful db insert, flash an error instead.
    # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    query = Show.query.join(
        Venue, (Venue.id == Show.venue_id)
    ).join(
        Artist, (Artist.id == Show.artist_id)
    ).with_entities(Show.venue_id, Venue.name.label('venue_name'), Show.artist_id, Artist.name.label('artist_name'),
                    Artist.image_link, Show.start_time)

    data = []
    for venues in query:
        data.append({
            "venue_id": venues.venue_id,
            "venue_name": venues.venue_name,
            "artist_id": venues.artist_id,
            "artist_name": venues.artist_name,
            "artist_image_link": venues.image_link,
            "start_time": venues.start_time
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
    form = ShowForm()
    try:
        if form.validate_on_submit():
            artist_id = form.artist_id.data
            venue_id = form.venue_id.data
            start_time = form.start_time.data

            shows = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

            print(shows)
            db.session.add(shows)
            db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())

    finally:
        db.session.close()
    if error:
        flash('Got an error during insertion, show could not be listed!')
        abort(400)
    else:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')

    # # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # # TODO: on unsuccessful db insert, flash an error instead.
    # # e.g., flash('An error occurred. Show could not be listed.')
    # # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # return render_template('pages/home.html')


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
