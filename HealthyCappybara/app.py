"""
Code contributor:
Yijia (Gaga) He: all
"""
import sys
import os
from .dashboard import main_dash
from .scraping.scraping_healthgrades import crawl
from .scraping.clean import clean

url = "https://www.healthgrades.com/specialty-directory"

def current_direc():
    """
    Get current directory
    Written by: Yijia (Gaga) He
    """
    return os.getcwd()

def run_dashboard():
    """
    Running dashboard
    Written by: Yijia (Gaga) He
    """
    app = main_dash.app
    app.run_server(debug=False, port=8050, host='0.0.0.0')


def run_scraping(max_direc_to_crawl, max_city_to_crawl, max_pages_to_crawl, url):
    """
    Scrape data from healthgrades
    Written by: Yijia (Gaga) He
    """
    return crawl(max_direc_to_crawl, max_city_to_crawl, max_pages_to_crawl, url)

def run_clean():
    """
    Clean datasets in the data directory
    Written by: Yue (Luna) Jian
    """
    return clean(current_direc())

def run():
    """
    User enter an option and interact with the program
    """
    print("Welcome to Cook County Health Accessibility App!")
    user_input = input(
        """Please Enter: 
                (a) The Dashboard, 
                (b) Scraping Data, 
                (c) Clean Data,
                (d) Quit App.
                Option: """)
    if user_input == "a":
        print("running dashboard...")
        run_dashboard()
    elif user_input == "b":
        category_user_input = input(
            """Please Enter: 
                    How many medical category do you want to crawl?
                    (For better performance, please limit it to 2)""")
        city_user_input = input(
            """Please Enter: 
                    How many cities do you want to crawl? 
                    (For better performance, please limit it to 2)""")
        page_user_input = input(
            """Please Enter: 
                    How many pages do you want to crawl? """)   
        continue_user_input = input(
            """Do you want to crawl now? Please enter: 
                    (y) Yes, please start now! 
                    (n) No, thank you. I'd like to quit now.
                    Option: """)
        if continue_user_input == "y":   
            print("this might take a few minutes... (you will be notified once finished)")     
            run_scraping(int(category_user_input), int(city_user_input), int(page_user_input), url)
            print(f'Congratulations! The data has been successfully crawled and saved to {current_direc()}') 
        else:
            sys.exit()
    elif user_input == "c":
        print("file is cleaning now...")
        run_clean()
        print("the file is ready now")  
    else:
        sys.exit()

