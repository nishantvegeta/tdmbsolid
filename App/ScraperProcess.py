from App.db import Database
from App.excel import Excel
from App.browser import Browser

class ScraperProcess:
    def __init__(self):
        self.db = Database()  # Initialize Database
        self.excel = Excel()  # Initialize Excel
        self.browser = Browser()  # Initialize Browser
        self.movies = []

    def before_run(self):
        self.movies = self.excel.read_movies_from_excel()
        self.db.connect()
        self.db.create_table()
        self.browser.open_tmdb()
        
        print("Setup completed")

    def run(self):
        self.before_run()
        for movie in self.movies:
            self.run_item(movie)
            
        self.after_run()

    def after_run(self):
        self.db.close()
        self.browser.close()
        self.excel.close_excel()
        print("Process completed")

    def before_run_item(self, movie):
        print(f"Starting to process movie: {movie}")

    def run_item(self, movie):
        self.before_run_item(movie)

        try:
            self.browser.search_movie(movie_name=movie)
            self.browser.scroll_to_load_movies()

            movie_found = self.browser.click_and_extract_movie_details(movie_name=movie)
            if not movie_found:
                print(f"No exact match found for movie: {movie}")
                return

            user_score, storyline, genres, reviews = self.browser.extract_movie_details(movie_name=movie)

            movie_data = (
                movie,
                user_score,
                storyline,
                ', '.join(genres) if genres else None,
                reviews[0] if len(reviews) > 0 else None,
                reviews[1] if len(reviews) > 1 else None,
                reviews[2] if len(reviews) > 2 else None,
                reviews[3] if len(reviews) > 3 else None,
                reviews[4] if len(reviews) > 4 else None,
                "Success"
            )

            self.db.insert_movie_data(*movie_data)

        except Exception as e:
            print(f"Error processing movie {movie}: {e}")

        self.after_run_item(movie)

    def after_run_item(self, movie):
        print(f"Finished processing movie: {movie}")
