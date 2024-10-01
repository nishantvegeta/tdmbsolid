import psycopg2

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect_postgresql()

    def connect_postgresql(self):
        self.connect()

    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        db_host = 'localhost'
        db_name = 'movie'
        db_user = 'postgres'
        db_password = 'postgres'

        try:
            self.connection = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            self.cursor = self.connection.cursor()
            self.create_table()
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            self.connection = None

    def create_table(self):
        """Create the movies table if it doesn't exist."""
        if self.connection:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS movies (
                    id SERIAL PRIMARY KEY,
                    movie_name VARCHAR(255) NOT NULL,
                    user_score VARCHAR(10),
                    storyline TEXT,
                    genres TEXT,
                    review_1 TEXT,
                    review_2 TEXT,
                    review_3 TEXT,
                    review_4 TEXT,
                    review_5 TEXT,
                    status VARCHAR(50)
                )
                """
            )
            self.connection.commit()
        else:
            print("No connection available to create the table.")


    def insert_movie_data(self, movie_name, user_score, storyline, genres, reviews, status="success"):
        """Insert the extracted movie data into the PostgreSQL database."""
        if not self.connection:
            print("No database connection available for insertion.")
            return

        sql_query = """
        INSERT INTO movies (movie_name, user_score, storyline, genres, review_1, review_2, review_3, review_4, review_5, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        parameters = (
            movie_name,  # movie_name
            user_score,  # user_score
            storyline,   # storyline
            genres,  # genres
            reviews[0] if len(reviews) > 0 else None,  # review_1
            reviews[1] if len(reviews) > 1 else None,  # review_2
            reviews[2] if len(reviews) > 2 else None,  # review_3
            reviews[3] if len(reviews) > 3 else None,  # review_4
            reviews[4] if len(reviews) > 4 else None,  # review_5
            status  # status
        )

        try:
            self.cursor = self.connection.cursor()  # Ensure cursor is available for insertion
            self.cursor.execute(sql_query, parameters)
            self.connection.commit()
            print(f"{movie_name} inserted successfully into the database with status: {status}.")
        except Exception as e:
            print(f"Error while inserting {movie_name} into the database: {e}")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
