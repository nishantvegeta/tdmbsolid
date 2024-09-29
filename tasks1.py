from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
import time
import psycopg2

def movies_name_from_excel():
    excel = Files()          
    excel.open_workbook("Movies.xlsx")
    movies = excel.read_worksheet(name="Sheet1", header=True)
    movie_list = [row["Movie"] for row in movies]
    excel.close_workbook()
    return movie_list

class TmdbScrapper:
    def __init__(self):
        self.browser = Selenium()
        self.tmdb_url = 'https://www.themoviedb.org/search/movie?query='
        self.browser.open_browser(browser="chrome")
        self.browser.maximize_browser_window()

    def setup_database(self):
        """Establish a connection to the PostgreSQL database."""
        # PostgreSQL connection details
        db_host = 'localhost'
        db_name = 'movie'
        db_user = 'postgres'
        db_password = 'postgres'

        try:
            # Connect to PostgreSQL database
            self.connection = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )
            print("Database connection established.")
            self.cursor = self.connection.cursor()
            self.create_table()
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            self.connection = None  # Ensure connection is None if there was an error

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

    def extract_movie_data(self, movie_name):

        if not self.connection:
            print("No database connection available")
            return 

        try:
            self.search_movie(movie_name)
            self.click_and_extract_movie_details(movie_name)
        except Exception as e:
            print(f"Error processing {movie_name}: {e}")

    # Function to search a movie on TMDb
    def search_movie(self, movie_name):
        url = self.tmdb_url + movie_name
        time.sleep(3)
        self.browser.go_to(url)  # Go to the search page

    def handle_overlays(self):
        """Dismiss any overlays or popups (e.g., cookie banners)."""
        try:
            # Example for handling cookie consent banner (adjust XPath or CSS selector as needed)
            consent_button_xpath = '//*[@id="onetrust-accept-btn-handler"]'  # Replace with the correct button XPath
            if self.browser.is_element_visible(consent_button_xpath):
                print("Dismissing cookie consent overlay...")
                self.browser.click_element(consent_button_xpath)
                time.sleep(3)  # Wait for the banner to disappear
        except Exception as e:
            print(f"Error dismissing overlay: {e}")



    def click_and_extract_movie_details(self, movie_name):
        """Click on the movie with the latest release year and exact name match, then extract its details."""
        self.handle_overlays()  # Dismiss any overlays before clicking

        movie_titles_xpath = f"//div[@class='title']//a[@data-media-type='movie']/h2[text()='{movie_name}']"
        movie_titles_elements = self.browser.get_webelements(movie_titles_xpath)
        print("----------------------------------------",movie_titles_elements)
        movie_years_xpath = f"//div[@class='title']//h2[text()='{movie_name}']//ancestor::div[@class='title']//span"
        movie_years_elements = self.browser.get_webelements(movie_years_xpath)

        movie_data = []
        for index, element in enumerate(movie_years_elements):
            year_text = element.text.strip()[-4:]
            print(year_text)
            try:
                year = int(year_text)
                title = movie_titles_elements[index].text.strip()  # Use .strip() to remove whitespace
                
                # Check for exact match with the movie name (ignoring case)
                if title == movie_name:
                    movie_data.append((title, year, index))  # Store the index for later use

                # print(f"found movie: '{title}' with year: {year}")
            except ValueError:
                continue
        print("MOIVE daTA----------------------", movie_data)
        movie_data.sort(key=lambda x: x[1], reverse=True)

        print(f"Matching movies found: {movie_data}")

        if not movie_data:
            print(f"No matching movies found for {movie_name}\n")
            self.insert_movie_data(movie_name, None, None, None, [], status="Not Found")
            return

        # Find the movie with the latest year among the exact matches
        # latest_movie = max(movie_data, key=lambda x: x[1])
        latest_movie = movie_data[0]
        print('latest movies is-->',latest_movie)
        latest_index = latest_movie[2]

        print(f"Clicking on the latest movie: {latest_movie[0]} ({latest_movie[1]})")

        # Dismiss overlays again before clicking, if necessary
        # self.handle_overlays()

        # Click on the movie with the latest year
        # self.browser.wait_until_element_is_visible(movie_titles_xpath)
        self.browser.scroll_element_into_view(movie_titles_elements[latest_index])
        self.scroll_to_load_movies()
        self.browser.click_element(movie_titles_elements[latest_index])
        time.sleep(2)

        # Extract movie details
        self.extract_movie_details(movie_name)



    def scroll_to_load_movies(self):
        """
        Scrolls down the page slowly using 'PAGE_DOWN' to load more movie results,
        then scrolls back up using 'PAGE_UP'.
        """
        scroll_pause_time = 1  # Adjust the pause time as needed

        for _ in range(2):  # You can increase or decrease the number of scrolls
            # Scroll down
            self.browser.press_keys(None, "PAGE_DOWN")
            time.sleep(scroll_pause_time)

        for _ in range(2):
            self.browser.press_keys(None, "PAGE_UP")
            time.sleep(scroll_pause_time)


   

    def extract_movie_details(self, movie_name):
        """Extract TMDB score, Storyline, Genres, and Reviews."""
         # Step 1: Extract details using appropriate XPaths
        user_score_xpath = '//div[@class="user_score_chart"]'
        storyline_xpath = '//div[@class="overview"]//p'
        genres_xpath = '//span[@class="genres"]'

        try:
            user_score = self.browser.get_element_attribute(user_score_xpath, "data-percent")
            storyline = self.browser.get_text(storyline_xpath)
            genres = self.browser.get_text(genres_xpath)

            
            self.scroll_to_load_movies()

            print(f"Movie: {movie_name}")
            print(f"TMDB Score: {user_score}")
            print(f"Storyline: {storyline}")
            print(f"Genres: {genres}")

            # Step 2: Scroll to and click on "Read All Reviews"
            self.click_read_all_reviews()

            # Step 3: Extract reviews after the "Read All Reviews" page loads
            reviews_xpath = '//section[@class="panel review"]//div[@class="review_container"]//div[@class="content"]//p'
            reviews = self.extract_reviews(reviews_xpath)

            self.insert_movie_data(movie_name, user_score, storyline, genres, reviews)
        
        except Exception as e:
            print(f"Error while extracting details for '{movie_name}': {e}")

        

    def click_read_all_reviews(self):
        read_reviews_xpath = '//a[contains(text(),"Read All Reviews")]'
        self.handle_overlays()
        try:
            if self.browser.is_element_visible(read_reviews_xpath):
                print("Clicking on 'Read All Reviews")
                self.browser.click_element(read_reviews_xpath)
                time.sleep(3)
            else:
                print("No Reviews...")
        except Exception as e:
            print(f"Error while extracting reviews: {e}")

    def extract_reviews(self,reviews_xpath):
        try:
            self.scroll_to_load_movies()
            reviews_elements = self.browser.get_webelements(reviews_xpath)

            top_reviews = [review.text.strip() for review in reviews_elements[:5]]

            print("Top 5 Reviews:\n")
            for index, review in enumerate(top_reviews, 1):
                print(f"Review {index}: {review}\n")

            return top_reviews
        
        except Exception as e:
            print(f"Error while extracting reviews: {e}")
            return []


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
            'Success'  # status
        )

        try:
            self.cursor.execute(sql_query, parameters)
            self.connection.commit()
            print(f"{movie_name} inserted successfully into database with status: {status}.")
        except Exception as e:
            print(f"Error while inserting {movie_name} into database: {e}")

    def close(self):      
        if self.connection:
            self.cursor.close()
            self.connection.close()
        self.browser.close_browser()

@task
def scrape_movies():
    movie_names = movies_name_from_excel()

    scrapper = TmdbScrapper()
    scrapper.setup_database()

    for movie in movie_names:
        print(f"Processing movie: {movie}\n")
        scrapper.extract_movie_data(movie)
        # scrapper.search_movie(movie)
        # scrapper.scroll_to_load_movies()
        # scrapper.click_and_extract_movie_details(movie)

    print("Scraping completed!")
    scrapper.close()

if __name__ == "__main__":
    scrape_movies()



# review_xpath = //a[contains(text(),'Read All Reviews')]







