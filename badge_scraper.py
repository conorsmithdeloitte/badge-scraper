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
    alternative_flag = False

    #Check if the user sent a name at all
    if not username:
        response["ERROR"] = "No username provided"
    else:
        
        #SECTION: Variable declaration
        url = 'https://www.salesforce.com/trailblazer/' + username

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
        
        #SECTION: Parse raw result to get the badge / point values
        l = []
        item = ''
        for x in shadow_content.text:
            if x == '\n':
                l.append(item)
                item = ''
            else:
                item += x
        print('Scraped Response: ',l)
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
            if arr[i].__contains__('Filter'):
                alternative_flag = True #flags if we get a valid alternative badge response
            # if arr[i].__contains__('Refresh the page') or arr[i].__contains__('Loading'): # commenting this out since this check isn't needed now
            #     flag = False #flags if we get an invalid response
            if arr[i].__contains__('Refresh the page') and arr[i + 2] == 'Badges': # need to monitor this because if site changes this code needs to be fixed
                flag = False #flags if we get an invalid response
            
        #SECTION: Save & print final result
        number_of_badges = number_of_badges.replace(',','')
        number_of_points = number_of_points.replace(',','')
        alternative_number_of_badges = alternative_number_of_badges.replace(',','')

        if (number_of_badges == '0' and alternative_number_of_badges != '0'):
            response["Badges"] = alternative_number_of_badges
        else:
            response["Badges"] = number_of_badges
        
        response["Points"] = number_of_points

        if (number_of_badges == '' and number_of_points == ''):
            response["IsPrivate"] = 'true'
            response["Badges"] = '-1'
            response["Points"] = '-1'
        else:
            response["IsPrivate"] = 'false'

        if (flag or alternative_flag or number_of_badges != '0' or number_of_points != '0' or alternative_number_of_badges != '0'):
            response['Flag'] = 'Succeeded' #need all of the above checks to minimize the chances of getting "Failed" when it's successful
        else:
            response['Flag'] = 'Failed'
        
        #response['Flag'] = 'Succeeded'
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

# Scenarios
# 	- Scraped response returns "Loading"
#       - Ignore this, if it's truly not working, then it should say to refresh the page in the line directly before number of badges / points 
#   - If alternative badge works and badge / points don't
# 		- Then, nullify points and use alternative badge
# 		- NOTE: In this scenario, badges and points will be 0 and alternative badge won't be 0 if it didn't work
# 	- If alternative badge doesn't work and badge / points do
# 		- Use the regular badge / points
# 	- If alternative badge and badge / points work
# 		- Use the regular badge / points
# 	- If neither alternative badge or badge / points work
# 		- Identify by whether there's refresh the page or loading AND there's NO "Filter" AND badges are 0 in the scraped response 
#       (note: sometimes points are still received when it says to refresh the page because it can be saying that for a different part of the page, 
#       but this check should still work in nearly all cases). Additionally, worst case is it marks batch as false when it shouldn't 
#       (if person actually has 0 badges and "refresh the page" shows up on a different part of the page)
