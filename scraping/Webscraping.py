from bs4 import BeautifulSoup
import requests

url = 'https://www.londonfa.com/cups-and-competitions/cups/2022-2023/london-u-13-youth-cup-saturday/results'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

matches_data = []

match_divs = soup.find_all('div', class_='cfa-match-accordion')  # Replace with the actual class name

for match_div in match_divs:
    match_info = {'Round': match_div.find_previous('h3').text.strip(),
                  'Date': match_div.find('div', class_='cfa-match-accordion__date').find_all('span')[0].text.strip(),
                  'Time': match_div.find('div', class_='cfa-match-accordion__date').find_all('span')[1].text.strip(),
                  'Home Team': match_div.find('div', class_='cfa-match-accordion__team--home').text.strip(),
                  'Away Team': match_div.find('div', class_='cfa-match-accordion__team--away').text.strip(),
                  'Score': match_div.find('div', class_='cfa-match-accordion__box').text.strip(),
                  'Referee': 'Dynamic content - use Selenium to extract',
                  'Assistant Referee 1': 'Dynamic content - use Selenium to extract',
                  'Assistant Referee 2': 'Dynamic content - use Selenium to extract',
                  'Fourth Official': 'Dynamic content - use Selenium to extract',
                  'Ground': 'Dynamic content - use Selenium to extract'}

    matches_data.append(match_info)

# Output the scraped data
for match in matches_data:
    print(match)
