from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__, template_folder='templates')

# 🔹 Secure Secret Key
app.secret_key = "supersecretkey"

# 🔹 Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Be1+iever@localhost/movie recondation'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔹 Initialize Database
db = SQLAlchemy(app)

# 🔹 User Model
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    favorite_genre = db.Column(db.String(100), nullable=True)

# 🔹 Movie Model
class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Float)
    year = db.Column(db.Integer)
    duration = db.Column(db.Integer)

# 🔹 Home Route (Redirects to Signup)
@app.route('/')
def home():
    return redirect(url_for('signup'))

# 🔹 Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['fullName']
        email = request.form['email']
        genre = request.form['genre']

        existing_user = Users.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        new_user = Users(full_name=full_name, email=email, favorite_genre=genre)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# 🔹 Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = Users.query.filter_by(email=email).first()
        
        if user:
            session['user'] = user.full_name  # Set session for authentication
            flash(f'Welcome, {user.full_name}!', 'success')
            return redirect(url_for('findmovie'))
        else:
            flash('Email not found. Please sign up.', 'danger')

    return render_template('login.html')

# 🔹 Movie Search Form
@app.route('/findmovie', methods=['GET', 'POST'])
def findmovie():
    if request.method == 'POST':
        return redirect(url_for('search'))
    return render_template('find-movie.html')

# 🔹 Search Movies in Database
@app.route('/search', methods=['POST'])
@app.route('/search', methods=['POST'])
def search():
    try:
        genres = request.form.getlist('genre')
        start_year = int(request.form['start_year'])
        end_year = int(request.form['end_year'])

        print(f"User Search - Genres: {genres}, Start Year: {start_year}, End Year: {end_year}")  # Debugging

        # Improved genre filtering
        movies = Movies.query.filter(
            or_(*[Movies.genre.ilike(f"%{genre}%") for genre in genres]),  # Partial match for genres
            Movies.year >= start_year,
            Movies.year <= end_year
        ).all()

        print(f"Movies Found: {[m.title for m in movies]}")  # Debugging

        if not movies:
            flash("No movies found matching the criteria.", "warning")

        return render_template('results.html', movies=movies)

    except ValueError:
        flash("Invalid year range. Please enter valid years.", "danger")
        return redirect(url_for('findmovie'))
# 🔹 Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
