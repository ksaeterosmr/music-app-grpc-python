import sys
import os

# Añadir el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask import Flask, flash, render_template, request, redirect, send_from_directory, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from client.client import get_song, get_featured_albums
from web.models import User, db, Playlist, Song
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO)

# Configuración de la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:123@localhost/music_app')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '123')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    song = None
    albums = get_featured_albums()  # Obtenemos los álbumes destacados desde Spotify

    if request.method == 'POST':
        song_name = request.form['song_name']
        song = get_song(song_name)

    return render_template('index.html', song=song, albums=albums)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    song = None
    if request.method == 'POST':
        song_name = request.form['song_name']
        song = get_song(song_name)

        if song:
            flash('Canción encontrada.', 'success')  # Mensaje de éxito
        else:
            flash('No se encontró la canción.', 'error')  # Mensaje de error

    return render_template('search.html', song=song)


@app.route('/like', methods=['POST'])
@login_required
def like():
    song_name = request.form['song_name']
    artist = request.form['artist']
    album = request.form['album']
    album_image = request.form['album_image']
    url = request.form['url']

    # Verifica si el usuario tiene una lista de reproducción, si no, crea una nueva
    playlist = Playlist.query.filter_by(user_id=current_user.id).first()
    if not playlist:
        playlist = Playlist(name="Mi Playlist", user_id=current_user.id)  # Asigna un nombre predeterminado
        db.session.add(playlist)
        db.session.commit()

    # Verifica si la canción ya existe en la lista de reproducción
    existing_song = Song.query.filter_by(
        playlist_id=playlist.id,
        song_name=song_name,
        artist=artist
    ).first()

    if existing_song:
        flash('Esta canción ya está en tu lista de reproducción.')
        return redirect(url_for('search'))

    # Agrega la nueva canción a la lista de reproducción
    new_song = Song(
        song_name=song_name,
        artist=artist,
        album=album,
        album_image=album_image,
        url=url,
        playlist_id=playlist.id
    )
    db.session.add(new_song)
    db.session.commit()

    flash('Canción agregada a tu lista de reproducción exitosamente.')
    return redirect(url_for('search'))

@app.route('/playlist')
@login_required
def playlist():
    playlist = Playlist.query.filter_by(user_id=current_user.id).first()
    songs = playlist.songs if playlist else []
    return render_template('playlist.html', songs=songs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrecta.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user_by_username = User.query.filter_by(username=username).first()
        existing_user_by_email = User.query.filter_by(email=email).first()

        if existing_user_by_username:
            flash('Ya existe un usuario con ese nombre.')
        elif existing_user_by_email:
            flash('Ya existe un usuario con ese email.')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso, por favor inicia sesión.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/delete/<int:song_id>', methods=['POST'])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    if song.playlist.user_id == current_user.id:  # Verificar que la canción pertenece al usuario
        db.session.delete(song)
        db.session.commit()
        flash('Canción eliminada de tu lista de reproducción.')
    return redirect(url_for('playlist'))


@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
