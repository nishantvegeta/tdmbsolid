from RPA.Excel.Files import Files

class Excel:
    def __init__(self, file_name="Movies.xlsx"):
        self.file_name = file_name
        self.excel = Files()

    def read_movies_from_excel(self):
        """Read movie names from the Excel file."""
        self.excel.open_workbook(self.file_name)
        movies = self.excel.read_worksheet(name="Sheet1", header=True)
        movie_list = [row["Movie"] for row in movies]
        self.excel.close_workbook()
        return movie_list

    def close_excel(self):
        self.excel.close_workbook()
        print("Excel file closed.")
