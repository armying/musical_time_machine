from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint


# date = input("What date would you like to travel to? (Enter in this format: YYYY-MM-DD): ")
date = "2012-07-28"
URL = f"https://www.billboard.com/charts/hot-100/{date}"
SPOTIFY_CLIENT_ID = "e1d203fbe64447238b48592a8f5834c1"
SPOTIFY_CLIENT_SECRET = "82748b35d0e643d286aadc072a92f6a5"


def scrape_song_titles(url):
    """Get the HTML code from the URL, and web scrape the 100 song billboard for the song titles,
     return the list of titles"""
    response = requests.get(url)
    html_code = response.text

    # Create a BeautifulSoup object and use it to extract the song titles
    soup = BeautifulSoup(html_code, "html.parser")
    song_title_tags = soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")
    song_titles = []
    for title in song_title_tags:
        song_titles.append(title.getText())
    return song_titles


def spotify_authorization():
    """ Perform Authorization for Spotify"""
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri="http://example.com",
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            show_dialog=True,
            cache_path="token.txt"
        )
    )
    user_id = sp.current_user()["id"]
    redirected_url = "http://example.com/?code=AQAXoHSPXhS5cpC7tKpo6oCxQTmulVWbtSQ-8SbeZIjDPKU4d6E7P8l67gGK_XKX3P" \
                     "DooFoGA0GviM69AIoNDdJl1fVoDiOgJ781bxOcj_NSQY-TGldZ4KJ089eKbPh7eCyKZbLbQse-uAjAVpucDx0hI50ZOHq8K" \
                     "EpyJsqAP2L92YKk9pSXHe0FxEvG3LU"
    return sp


def find_uri_for_titles(titles, spotify_obj, input_date):
    """Given a list of song titles and a spotipy object, return a list of uri for the songs"""
    song_uri_list = []
    title_to_uri = {}
    year = input_date.split("-")[0]
    for title in titles:
        result = spotify_obj.search(q=f"track:{title} year:{year}", type="track")
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uri_list.append(uri)
            title_to_uri[title] = uri
        except KeyError:
            print(f'"{title}" is not on Spotify...')
            continue
    pprint.pprint(title_to_uri)
    return song_uri_list


fav_titles = scrape_song_titles(URL)
spotify = spotify_authorization()
uri_list = find_uri_for_titles(fav_titles, spotify, date)
results = spotify.current_user_playlists(limit=50)

# Create a Spotify playlist
user_id = spotify.current_user()["id"]
print(user_id)
playlist = spotify.user_playlist_create(user=user_id, name=f"My name is Army", public=False)

# Add the songs to the playlist using the uri_list
spotify.playlist_add_items(playlist_id=playlist["id"], items=uri_list)


