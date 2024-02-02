from bs4 import BeautifulSoup
import requests

html_text = requests.get('https://www.londonfa.com/cups-and-competitions/cups/2022-2023/london-u-13-youth-cup-saturday/results').text
soup = BeautifulSoup(html_text, 'lxml')

matches = soup.find('div', class_='cfa-match-table')
print(matches)

#matche_step = matches.find('h3', class_='cfa-match-table__title audience__background').text.replace(' ', '')



#print(matche_step)


