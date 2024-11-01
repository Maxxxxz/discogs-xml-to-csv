import xml.etree.ElementTree as elemTree
import csv

from glob import glob

def get_discogs_releases_filename():
    """
    Get the discogs releases.xml filename
    """
    matching_files = glob("discogs_*releases.xml")
    if len(matching_files) == 0:
        raise ValueError("No discogs releases.xml file found")
    return matching_files[0]

def read_discogs_releases(filename):
    """
    Reads the discogs releases.xml file and yields each release element
    Avoids loading the entire file into memory
    """
    context = elemTree.iterparse(filename, events=("start", "end"))
    context = iter(context)
    event, root = next(context)
    
    for event, elem in context:
        if event == "end" and elem.tag == "release":
            yield elem
            root.clear()

def extract_release_data(release):
    """
    Extracts the data from a release element
    Utilizes 5 bars to separate joined data for splitting or replacing later
    """
    release_id = release.get('id')
    title = release.findtext('title')
    country = release.findtext('country')
    data_quality = release.findtext('data_quality')
    
    artists = [artist.findtext('name') for artist in release.findall('.//artists/artist')]
    artist_names = ' ||||| '.join(artists)
    
    genres = [genre.text for genre in release.findall('.//genres/genre')]
    genre_names = ' ||||| '.join(genres)
    
    styles = [style.text for style in release.findall('.//styles/style')]
    style_names = ' ||||| '.join(styles)
    
    tracks = []
    for track in release.findall('.//tracklist/track'):
        position = track.findtext('position')
        track_title = track.findtext('title')
        tracks.append(f"{position}: {track_title}")
    tracklist = ' ||||| '.join(tracks)

    images = [image.get('uri') for image in release.findall('.//images/image')]
    image_list = ' ||||| '.join(images)

    return [release_id, title, artist_names, country, genre_names, style_names, data_quality, tracklist, image_list]

def main():
    filename = get_discogs_releases_filename()
    if filename:
        releases = read_discogs_releases(filename)
        
        csv_filename = filename.replace('.xml', '.csv')
        # Create the CSV file and write the header
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['id', 'titles', 'artists', 'country', 'genres', 'styles', 'dataQuality', 'trackList', 'images'])
            
            # Write the data for each release
            for release in releases:
                release_data = extract_release_data(release)
                csv_writer.writerow(release_data)

    print(f"Finished writing {csv_filename}")

if __name__ == "__main__":
    main()
