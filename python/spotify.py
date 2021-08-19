import json
import numpy as np
import os.path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys

# This reads the spotify API client ID and client secret from the
# SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    "a5a06f90f9a04b259024dfdeebd837b6",
    "8143816647f94d36aba4bd1fceb203be"
))

bts = '3Nrfpe0tUJi4K4DXYWgMUX' # BTS
kpop_artists = [
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
    # 'instrumentalness',
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

artist_audio_features_cache = {}
# Returns the mean audio features for an artist, in the form of a numpy array.
# This only returns the features in `features_of_interest`. This is calculated
# by getting the audio features for every track returned by
# `artist_top_tracks`, and taking the average.
def artist_audio_features(artist_id):
    cached = artist_audio_features_cache.get(artist_id) 
    if cached is not None:
        return cached
    top_tracks = artist_top_tracks(artist_id)
    assert len(top_tracks) <= 100
    mean_features = np.zeros(len(features_of_interest))
    for track_features in sp.audio_features(top_tracks):
        for i, key in enumerate(features_of_interest):
            mean_features[i] += track_features[key]
    mean_features /= len(top_tracks)
    artist_audio_features_cache[artist_id] = mean_features
    return mean_features

# Builds a JSON file with the mean audio features for a series of artists.
def build_artist_features_json(artists, out_file, verbose=False):
    # This function takes around 30 secs per artist
    result = {
        'labels': features_of_interest,
        'artists': []
    }
    mean_features = np.zeros(len(features_of_interest))
    for artist_id in artists:
        name = sp.artist(artist_id)['name']
        if verbose:
            print(f'getting {artist_id} ({name})... ', end='')
            sys.stdout.flush()
        features = artist_audio_features(artist_id)
        mean_features += features
        result['artists'].append({
            'name': name,
            'features': list(features),
        })
        if verbose:
            print('finished')
    mean_features /= len(artists)
    result['meanFeatures'] = list(mean_features)

    with open(out_file, 'w') as out_file:
        json.dump(result, out_file)

# If the file already exists, we don't try to create it again
if not os.path.isfile('kpop-artist-features.json'):
    build_artist_features_json([bts] + kpop_artists,
        'kpop-artist-features.json', verbose=True)

if not os.path.isfile('general-artist-features.json'):
    build_artist_features_json([bts] + general_artists,
        'general-artist-features.json', verbose=True)

if not os.path.isfile('all-artist-features.json'):
    build_artist_features_json([bts] + kpop_artists + general_artists,
        'all-artist-features.json', verbose=True)

