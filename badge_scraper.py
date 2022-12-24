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
import time as t

app = Flask(__name__)

@app.errorhandler(404) 
def invalid_route(e): 
    return "Invalid route."

@app.route('/trailblazer/', methods=['GET'])
def respond():
    #Retrieve the name from the url parameter /trailblazer/?username=
    username = request.args.get("username", None)

    #Print username
    print(f"Username: {username}")

    response = {}
    flag = True

    #Check if the user sent a name at all
    if not username:
        response["ERROR"] = "No username provided"
    else:
        
        #SECTION: Variable declaration
        url = 'https://trailblazer.me/id/' + username

        #SECTION: Find HTML element that contains badge / point data
        driver = webdriver.Chrome()
        driver.get(url)
        delay = 10 #seconds

        try:
            shadow_host = WebDriverWait(driver, delay).until(EC.visibility_of_element_located(((By.CSS_SELECTOR, '#profile-sections-container'))))
            shadow_root = shadow_host.shadow_root
            t.sleep(3) #this will make it so page won't still be loading
            shadow_content = shadow_root.find_element(By.CLASS_NAME, 'root')
            print("Page contents are received")
        except TimeoutException: #this scenario will hit if trailhead ID is incorrect or if page takes too long to load
            print("Either the Trailhead ID is incorrect or the page took too long to load")
            response["Badges"] = '0'
            response["Points"] = '0'
            response["Flag"] = 'Failed'
            response["IsPrivate"] = 'false'
            response["IsURLInvalid"] = 'true'
            return jsonify(response)
        except:
            print("Unknown issue")
            return "Unknown issue"

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
        print('Array Response: ',l)
        arr = l
        number_of_badges = ''
        number_of_points = ''
        alternative_number_of_badges = '0'
        for i in range(len(arr)): 
            if i + 1 == len(arr):
                break
            elif arr[i + 1] == 'Badges':
                number_of_badges = arr[i]
            elif arr[i + 1] == 'Points':
                number_of_points = arr[i]
            elif arr[i].__contains__(' Badges') and arr[i][:arr[i].find(' ')].isnumeric():
                alternative_number_of_badges = arr[i][:arr[i].find(' ')]

            if arr[i].__contains__('Refresh the page') or arr[i].__contains__('Loading'):
                flag = False #flags if we get an invalid response
            
        #SECTION: Save & print final result
        number_of_badges = number_of_badges.replace(',','')
        number_of_points = number_of_points.replace(',','')
        alternative_number_of_badges = alternative_number_of_badges.replace(',','')
        response["Badges"] = number_of_badges
        #response["Badges"] = alternative_number_of_badges
        response["Points"] = number_of_points

        if (number_of_badges == '' and number_of_points == ''):
            response["IsPrivate"] = 'true'
            response["Badges"] = '-1'
            response["Points"] = '-1'
        else:
            response["IsPrivate"] = 'false'

        response['Flag'] = 'Succeeded'
        response['IsURLInvalid'] = 'false'

        print('Number of Badges:', number_of_badges)
        print('Number of Points:', number_of_points)
        print('Number of Alternative Badges:', alternative_number_of_badges)
        print('Flag:', flag)


    # Return the response in JSON format
    return jsonify(response)

@app.route('/')
def index():
    # A welcome message to test our server
    return "<h2>Welcome to the badge scraper API!</h2>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    # app.run(threaded=True, port=5000, debug=True) #temporarily commented out, this is original code
    from waitress import serve
    serve(app,host="0.0.0.0",port=5000)
