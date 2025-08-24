Playlist Tracker - Full Stack Flask App
=======================================
Features included:
- User accounts (register / login) using Flask-Login
- Add playlists (URL + total videos)
- Progress bar per playlist, mark videos completed (increment/decrement)
- Remove playlist from card
- Track total watch progress across all playlists (for the logged-in user)
- Sorting & filtering (by name, progress)
- Basic responsive UI with glassmorphism, animations, and dark mode
- Uses SQLite (Flask-SQLAlchemy) for data persistence

To run locally:
1. python -m venv venv
2. source venv/bin/activate  (or venv\Scripts\activate on Windows)
3. pip install -r requirements.txt
4. export FLASK_APP=app.py
   export FLASK_ENV=development   (optional)
5. flask run
Default DB file will be `site.db` in project folder.

Notes:
- This is a simple, ready-to-run sample app. It focuses on core features and UI.
- You can extend it to fetch playlist metadata from YouTube Data API if you want.
