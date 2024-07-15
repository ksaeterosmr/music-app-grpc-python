import grpc
import music_pb2
import music_pb2_grpc
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO)

def get_grpc_channel():
    """Crea y devuelve un canal gRPC."""
    return grpc.insecure_channel('localhost:50051')

def get_song(song_name):
    """Obtiene información de una canción por su nombre."""
    try:
        with get_grpc_channel() as channel:
            stub = music_pb2_grpc.MusicServiceStub(channel)
            request = music_pb2.SongRequest(song_name=song_name)
            response = stub.GetSong(request)
            if response.song_name:
                logging.info(f"Canción encontrada: {response.song_name}")
                return {
                    'song_name': response.song_name,
                    'artist': response.artist,
                    'album': response.album,
                    'album_image': response.album_image,
                    'url': response.url
                }
            logging.info("Canción no encontrada.")
            return None
    except grpc.RpcError as e:
        logging.error(f"Fallo de RPC: {e}")
        return None

def get_featured_albums():
    """Obtiene una lista de álbumes destacados."""
    try:
        with get_grpc_channel() as channel:
            stub = music_pb2_grpc.MusicServiceStub(channel)
            request = music_pb2.Empty()
            response = stub.GetFeaturedAlbums(request)
            albums = []
            for album in response.albums:
                albums.append({
                    'album_name': album.album_name,
                    'artist': album.artist,
                    'album_image': album.album_image
                })
            logging.info(f"{len(albums)} álbumes destacados obtenidos.")
            return albums
    except grpc.RpcError as e:
        logging.error(f"Fallo de RPC: {e}")
        return []

if __name__ == '__main__':
    song_name = 'Shape of You'
    song = get_song(song_name)
    if song:
        logging.info(f"Song: {song['song_name']}, Artist: {song['artist']}, Album: {song['album']}, URL: {song['url']}, Album Image: {song['album_image']}")
    else:
        logging.info("Song not found.")

    albums = get_featured_albums()
    for album in albums:
        logging.info(f"Album: {album['album_name']}, Artist: {album['artist']}, Album Image: {album['album_image']}")
