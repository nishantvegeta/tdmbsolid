from App.ScraperProcess import ScraperProcess

class Bot():
    def __init__(self):
        self.sp = ScraperProcess()
    
    def start(self):
        self.sp.before_run()
        self.sp.run()
        # self.sp.after_run()

    def teardown(self):
        self.sp.after_run()