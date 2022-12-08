#NOTE: The commented out packages don't work for shadow DOM parsing
#import requests
#from bs4 import BeautifulSoup

#SECTION: Package imports
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/trailblazer/', methods=['GET'])
def respond():
    # Retrieve the name from the url parameter /trailblazer/?username=
    username = request.args.get("username", None)

    # For debugging
    print(f"Received: {username}")

    response = {}
    loaded = False
    count = 0


    # Check if the user sent a name at all
    if not username:
        response["ERROR"] = "No username provided"
    else:
        while loaded == False and count < 5: #continue to run if scraper doesn't pull right data, but limit reruns to 5 to avoid infinite loops
            #SECTION: Variable declaration
            loaded = True
            url = 'https://trailblazer.me/id/' + username

            #SECTION: Find HTML element that contains badge / point data
            driver = webdriver.Chrome()
            driver.get(url)
            delay = 100 # seconds
            try:
                shadow_host = WebDriverWait(driver, delay).until(EC.presence_of_element_located(((By.CSS_SELECTOR, '#profile-sections-container'))))
                #shadow_host = driver.find_element(By.CSS_SELECTOR, '#profile-sections-container')
                shadow_root = shadow_host.shadow_root
                shadow_content = shadow_root.find_element(By.CLASS_NAME, 'root')
                print("Page is ready!")
            except TimeoutException:
                print("Timeout error, took too long to load")

            #NOTE: The below print statement shows what the full root string looks like
            print(shadow_content.text)

            #SECTION: Parse raw result to get the badge / point values
            l = []
            item = ''
            for x in shadow_content.text:
                if x == '\n':
                    l.append(item)
                    item = ''
                else:
                    item += x
            print('Array Response',l)
            arr = l
            number_of_badges = ''
            number_of_points = ''
            for i in range(len(arr)): 
                if arr[i].__contains__('Refresh the page'): # check to confirm whether we need to run the code again and reload the page
                    loaded = False
                    break
                if i + 1 == len(arr):
                    break
                elif arr[i + 1] == 'Badges':
                    number_of_badges = arr[i]
                elif arr[i + 1] == 'Points':
                    number_of_points = arr[i]
                
                

            #SECTION: Save & print final result
            response["Badges"] = number_of_badges
            response["Points"] = number_of_points

            print('Number of Badges:', number_of_badges)
            print('Number of Points:', number_of_points)

            count += 1

    # Return the response in JSON format
    return jsonify(response)

@app.route('/')
def index():
    # A welcome message to test our server
    return "<h2>Welcome to the badge scraper API!</h2>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)