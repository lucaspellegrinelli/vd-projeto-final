import csv
import numpy as np
import os.path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# This reads the spotify API client ID and client secret from the
# SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

kpop_artists = [
    '3Nrfpe0tUJi4K4DXYWgMUX', # BTS
    '4Kxlr1PRlDKEB0ekOCyHgX', # BIGBANG
    '41MozSoPIsD1dJM0CLPjZF', # BLACKPINK
    '3cjEqqelV9zb4BYE3qDQ4O', # EXO
    '0qlWcS66ohOIi0M8JZwPft', # GFRIEND
    '0Sadg1vgvaPqGTOjxu0N6c', # Girls' Generation
    '1z4g3DjTBBZKhvAroFlhOM', # Red Velvet
    '7nqOGRxlXj7N2JYbgNEjYH', # SEVENTEEN
    '2hRQKC0gqlZGPrmUKbcchR', # SHINee
    '6gzXCdfYfFe5XKhPKkYqxV', # SUPER JUNIOR
    '7n2Ycct7Beij7Dj7meI4X0', # TWICE
]

# Based on the top 10 artists in
# https://www.billboard.com/charts/decade-end/top-artists
general_artists = [
    '3TVXtAsR1Inumwj472S9r4', # Drake
    '06HL4z0CvFAxyc27GXpf02', # Taylor Swift
    '0du5cEVh5yTK9QJze8zA0C', # Bruno Mars
    '5pKCCKE2ajJHZ9KAiaK11H', # Rihanna
    '4dpARuHxo51G3z768sgnrY', # Adele
    '6eUKZXaKkcviH0Ku9w2n3V', # Ed Sheeran
    '1uNFoZAHBGtllmzznpCI3s', # Justin Bieber
    '6jJ0s89eD6GaHleKKya26X', # Katy Perry
    '04gDigrS5kc9YWfZHwBETP', # Maroon 5
    '246dkjvS1zLTtiykXe5h60', # Post Malone
]

# These are the audio features that are numerical and have values between 0.0
# and 1.0
features_of_interest = [
    'acousticness',
    'danceability',
    'energy',
    'instrumentalness',
    'liveness',
    'speechiness',
    'valence',
]

# Returns the union of the top 10 tracks for an artist for every possible
# region. That is, if a track is in the top 10 for the given artist in any
# region, it will be in the returned list.
def artist_top_tracks(artist_id):
    all_regions = sp.available_markets()['markets']
    top_tracks = set()
    for region in all_regions:
        for track in sp.artist_top_tracks(artist_id, region)['tracks']:
            top_tracks.add(track['id'])
    return list(top_tracks)

# Returns the mean audio features for an artist, in the form of a numpy array.
# This only returns the features in `features_of_interest`. This is calculated
# by getting the audio features for every track returned by
# `artist_top_tracks`, and taking the average.
def artist_audio_features(artist_id):
    top_tracks = artist_top_tracks(artist_id)
    assert len(top_tracks) <= 100
    mean_features = np.zeros(len(features_of_interest))
    for track_features in sp.audio_features(top_tracks):
        for i, key in enumerate(features_of_interest):
            mean_features[i] += track_features[key]
    mean_features /= len(top_tracks)
    return mean_features

# Builds a CSV file with the mean audio features for a series of artists.
def build_artist_features_csv(artists, out_file, verbose=False):
    # This function takes around 30 secs per artist
    with open(out_file, 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(['id', 'name'] + features_of_interest)
        for artist_id in artists:
            name = sp.artist(artist_id)['name']
            features = list(artist_audio_features(artist_id))
            writer.writerow([artist_id, name] + features)
            if verbose:
                print(f'finished {artist_id} ({name})')

# If the file already exists, we don't try to create it again
if not os.path.isfile('kpop-artist-features.csv'):
    build_artist_features_csv(kpop_artists, 'kpop-artist-features.csv', verbose=True)

if not os.path.isfile('general-artist-features.csv'):
    build_artist_features_csv(general_artists, 'general-artist-features.csv', verbose=True)
