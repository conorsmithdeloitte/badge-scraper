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
from flask import Flask, request, jsonify
app = Flask(__name__)

# #SECTION: Variable declaration
# username = 'eszmigielski'
# #username = 'csmith288'
# url = 'https://trailblazer.me/id/' + username

# #SECTION: Find HTML element that contains badge / point data
# driver = webdriver.Chrome()
# driver.get(url)
# shadow_host = driver.find_element(By.CSS_SELECTOR, '#profile-sections-container')
# shadow_root = shadow_host.shadow_root
# shadow_content = shadow_root.find_element(By.CLASS_NAME, 'root')

# #NOTE: The goal of the below test code is to get to an element further down in the hierarchy so I don't have to string parse for the badge
# #test_root = shadow_content.shadow_root
# #badge = test_root.find_element(By.CLASS_NAME, 'card__header-title')

# #NOTE: The below print statement shows what the full root string looks like
# #print(shadow_content.text)

# #SECTION: Parse raw result to get the badge / point values
# total_new_lines = 0
# badge_and_point_new_line_location = 0
# number_of_badges = ''
# number_of_points = ''
# for x in shadow_content.text:
#     if x == '\n':
#         total_new_lines += 1
# for x in shadow_content.text:
#     if x == '\n':
#         badge_and_point_new_line_location += 1
#     elif badge_and_point_new_line_location == total_new_lines - 6:
#         number_of_badges += x
#     elif badge_and_point_new_line_location == total_new_lines - 4:
#         number_of_points += x

# #SECTION: Print final result
# print('Number of Badges:', number_of_badges)
# print('Number of Points:', number_of_points)

# # NOTE: Don't need below lines since this doesn't work for parsing shadow dom
# # page = requests.get(URL, verify=False)
# # soup = BeautifulSoup(page.content, 'html.parser')
# # print(soup.prettify())
# # print(soup.title)
# # s = soup.find('div', class_='card__header-title')
# # s = soup.find('div', class_='card__header-title')
# # print(s.find_all('h2'))
# # content = s.final_all('p')
# # print(content)

@app.route('/trailblazer/', methods=['GET'])
def respond():
    # Retrieve the name from the url parameter /trailblazer/?username=
    username = request.args.get("username", None)

    # For debugging
    print(f"Received: {username}")

    response = {}

    # Check if the user sent a name at all
    if not username:
        response["ERROR"] = "No username provided"
    else:
        #SECTION: Variable declaration
        url = 'https://trailblazer.me/id/' + username
        print('testing123')

        #SECTION: Find HTML element that contains badge / point data
        driver = webdriver.Chrome()
        driver.get(url)
        shadow_host = driver.find_element(By.CSS_SELECTOR, '#profile-sections-container')
        shadow_root = shadow_host.shadow_root
        shadow_content = shadow_root.find_element(By.CLASS_NAME, 'root')

        #NOTE: The goal of the below test code is to get to an element further down in the hierarchy so I don't have to string parse for the badge
        #test_root = shadow_content.shadow_root
        #badge = test_root.find_element(By.CLASS_NAME, 'card__header-title')

        #NOTE: The below print statement shows what the full root string looks like
        #print(shadow_content.text)

        #SECTION: Parse raw result to get the badge / point values
        total_new_lines = 0
        badge_and_point_new_line_location = 0
        number_of_badges = ''
        number_of_points = ''
        for x in shadow_content.text:
            if x == '\n':
                total_new_lines += 1
        for x in shadow_content.text:
            if x == '\n':
                badge_and_point_new_line_location += 1
            elif badge_and_point_new_line_location == total_new_lines - 6:
                number_of_badges += x
            elif badge_and_point_new_line_location == total_new_lines - 4:
                number_of_points += x

        #SECTION: Print final result
        response["Badges"] = number_of_badges
        response["Points"] = number_of_points
        #response["MESSAGE"] = f"Number of Badges Test: {username}"

        print('Number of Badges:', number_of_badges)
        print('Number of Points:', number_of_points)

    # Return the response in json format
    return jsonify(response)

@app.route('/')
def index():
    # A welcome message to test our server
    return "<h1>testaWelcome to the badge scraper API!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)