from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    playlists = db.relationship('Playlist', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    total_videos = db.Column(db.Integer, default=0)
    completed_videos = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def progress_percent(self):
        if self.total_videos <= 0:
            return 0
        return int((self.completed_videos / self.total_videos) * 100)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# @app.before_first_request
# def create_tables():
#     db.create_all()
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Please provide username and password', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # sorting/filtering params
    sort = request.args.get('sort', 'created')  # created, name, progress
    filter_q = request.args.get('filter', '')   # text filter by title
    playlists = Playlist.query.filter_by(owner=current_user)
    if filter_q:
        playlists = playlists.filter(Playlist.title.ilike(f"%{filter_q}%"))
    if sort == 'name':
        playlists = playlists.order_by(Playlist.title.asc())
    elif sort == 'progress':
        # order by progress percent (computed) - fallback to total_videos desc
        playlists = playlists.order_by((Playlist.completed_videos*1.0/ (Playlist.total_videos+1)).desc())
    else:
        playlists = playlists.order_by(Playlist.id.desc())
    playlists = playlists.all()

    # total progress
    total_videos = sum(p.total_videos for p in playlists)
    total_completed = sum(p.completed_videos for p in playlists)
    total_progress = int((total_completed/total_videos)*100) if total_videos>0 else 0

    return render_template('dashboard.html', playlists=playlists, total_progress=total_progress, total_videos=total_videos, total_completed=total_completed, sort=sort, filter_q=filter_q)

@app.route('/add_playlist', methods=['POST'])
@login_required
def add_playlist():
    title = request.form.get('title','').strip() or 'Untitled Playlist'
    url = request.form.get('url','').strip()
    try:
        total_videos = int(request.form.get('total_videos',0))
    except ValueError:
        total_videos = 0
    if not url:
        flash('Please provide playlist URL', 'danger')
        return redirect(url_for('dashboard'))
    playlist = Playlist(title=title, url=url, total_videos=max(total_videos,0), completed_videos=0, owner=current_user)
    db.session.add(playlist)
    db.session.commit()
    flash('Playlist added', 'success')
    return redirect(url_for('dashboard'))

@app.route('/playlist/<int:p_id>/increment', methods=['POST'])
@login_required
def increment(p_id):
    p = Playlist.query.get_or_404(p_id)
    if p.owner != current_user:
        return jsonify({'error':'unauthorized'}), 403
    if p.completed_videos < p.total_videos:
        p.completed_videos += 1
        db.session.commit()
    return jsonify({'completed': p.completed_videos, 'percent': p.progress_percent})

@app.route('/playlist/<int:p_id>/decrement', methods=['POST'])
@login_required
def decrement(p_id):
    p = Playlist.query.get_or_404(p_id)
    if p.owner != current_user:
        return jsonify({'error':'unauthorized'}), 403
    if p.completed_videos > 0:
        p.completed_videos -= 1
        db.session.commit()
    return jsonify({'completed': p.completed_videos, 'percent': p.progress_percent})

@app.route('/playlist/<int:p_id>/remove', methods=['POST'])
@login_required
def remove(p_id):
    p = Playlist.query.get_or_404(p_id)
    if p.owner != current_user:
        return jsonify({'error':'unauthorized'}), 403
    db.session.delete(p)
    db.session.commit()
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True)
