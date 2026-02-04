from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# ----------------------------
# Database helper
# ----------------------------
def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------
# Get movies (with filters)
# ----------------------------
@app.route('/movies', methods=['GET'])
def get_movies():
    min_rating = request.args.get('min_rating')
    year = request.args.get('year')
    title = request.args.get('title')

    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    if min_rating:
        query += " AND rating >= ?"
        params.append(float(min_rating))

    if year:
        query += " AND year = ?"
        params.append(int(year))

    if title:
        query += " AND title LIKE ?"
        params.append(f"%{title}%")

    conn = get_db_connection()
    movies = conn.execute(query, params).fetchall()
    conn.close()

    movies_list = [dict(movie) for movie in movies]
    return jsonify(movies_list)


# ----------------------------
# Add a movie
# ----------------------------
@app.route('/add', methods=['POST'])
def add_movie():
    data = request.get_json()

    title = data['title']
    year = data['year']
    rating = data['rating']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO movies (title, year, rating) VALUES (?, ?, ?)',
        (title, year, rating)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Movie added successfully!"})


# ----------------------------
# Update a movie rating
# ----------------------------
@app.route('/update/<int:id>', methods=['PUT'])
def update_movie(id):
    data = request.get_json()
    new_rating = data['rating']

    conn = get_db_connection()
    conn.execute(
        'UPDATE movies SET rating = ? WHERE id = ?',
        (new_rating, id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Movie updated successfully!"})


# ----------------------------
# Delete a movie
# ----------------------------
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_movie(id):
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE id = ?', (id,)).fetchone()

    if movie is None:
        conn.close()
        return jsonify({"message": "Movie not found"}), 404

    conn.execute('DELETE FROM movies WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Movie deleted successfully!"})


# ----------------------------
# Run the server
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)
