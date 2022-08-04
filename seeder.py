import click
from flask.cli import with_appcontext
from models import db, Venue, Artist, Show

# data
dataVenue=[
    {
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    },
    {
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    },
    {
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    }
]
dataShow=[
    {
        "venue_name": "The Musical Hop",
        "artist_name": "Guns N Petals",
        "start_time": "2019-05-21T21:30:00.000Z"
    },
    {
        "venue_name": "Park Square Live Music & Coffee",
        "artist_name": "The Wild Sax Band",
        "start_time": "2035-04-01T20:00:00.000Z"
    },
    {
        "venue_name": "Park Square Live Music & Coffee",
        "artist_name": "The Wild Sax Band",
        "start_time": "2035-04-08T20:00:00.000Z"
    },
    {
        "venue_name": "Park Square Live Music & Coffee",
        "artist_name": "The Wild Sax Band",
        "start_time": "2035-04-15T20:00:00.000Z"
    },
    {
        "venue_name": "Park Square Live Music & Coffee",
        "artist_name": "Matt Quevedo",
        "start_time": "2019-06-15T23:00:00.000Z"
    },
]

dataArtist=[
    {
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    },
    {
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    },
    {
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    }
]

# create command function
@click.command(name='init_data')
@with_appcontext
def init_data():
    try:
        Show.query.filter(Show.id>0).delete()
        Venue.query.filter(Venue.id>0).delete()
        Artist.query.filter(Artist.id>0).delete()
        
        for data in dataVenue:
            venue = Venue(
                name=data['name'],
                genres=', '.join(data['genres']),
                address=data['address'],
                city=data['city'],
                state=data['state'],
                phone=data['phone'],
                website_link=data['website'],
                facebook_link=data['facebook_link'],
                seeking_talent=data['seeking_talent'],
                seeking_description=data['seeking_description'],
                image_link=data['image_link'],
            )
            db.session.add(venue)
            
        for data in dataArtist:
            artist = Artist(
                name=data['name'],
                city=data['city'],
                state=data['state'],
                phone=data['phone'],
                genres=', '.join(data['genres']),
                image_link=data['image_link'],
                website_link=data['website'],
                seeking_venue=data['seeking_venue'],
                seeking_description=data['seeking_description'],
                facebook_link=data['facebook_link'],
            )
            db.session.add(artist)
            
        for data in dataShow:
            artist = Artist.query.filter(Artist.name==data['artist_name']).first()
            venue = Venue.query.filter(Venue.name==data['venue_name']).first()
            if artist and venue:
                show = Show(
                    venue_id=venue.id,
                    artist_id=artist.id,
                    start_time=data['start_time'],
                )
                db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()