import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import numpy as np
import sqlite3 as sql
import pandas as pd
import time
from itertools import islice

# recuperation de toutes les marques de voitures
brands = ['audi','bmw', 'ford', 'mercedes-benz', 'opel', 'volkswagen', 'renault', '9ff', 'abarth', 'ac', 'acm', 'acura', 'aixam', 'alfa-romeo', 'alpina', 'alpine', 'amphicar', 'ariel-motor', 'artega', 'aspid', 'aston-martin', 'austin', 'autobianchi', 'auverland', 'baic', 'bedford', 'bellier', 'bentley', 'bolloré', 'borgward', 'brilliance', 'bugatti', 'buick', 'byd', 'cadillac', 'caravans-wohnm', 'casalini',
'caterham', 'changhe', 'chatenet', 'chery', 'chevrolet', 'chrysler', 'citroen', 'cityel', 'cmc', 'corvette', 'courb', 'cupra', 'dacia', 'daewoo', 'daf', 'daihatsu', 'daimler', 'dangel', 'de-tomaso', 'derways', 'dfsk', 'dodge', 'donkervoort', 'dr-motor', 'ds-automobiles', 'dutton', 'e.go', 'estrima', 'ferrari', 'fiat', 'fisker', 'gac-gonow', 'galloper', 'gaz', 'geely', 'gem', 'gemballa', 'genesis', 'gillet', 'giotti-victoria', 'gmc', 'goupil', 'great-wall', 'grevac', 'haima', 'hamann', 'haval', 'honda', 'hummer', 'hurtan', 'hyundai', 'infiniti', 'innocenti', 'iso-rivolta', 'isuzu', 'iveco', 'izh', 'jaguar', 'jeep', 'karabag', 'kia', 'koenigsegg', 'ktm', 'lada', 'lamborghini', 'lancia', 'land-rover', 'ldv', 'lexus', 'lifan', 'ligier', 'lincoln', 'lotus', 'mahindra', 'man', 'mansory', 'martin-motors', 'maserati', 'maxus', 'maybach', 'mazda', 'mclaren', 'melex', 'mg', 'microcar', 'minauto', 'mini', 'mitsubishi', 'mitsuoka', 'morgan', 'moskvich', 'mp-lafer', 'mpm-motors', 'nio', 'nissan', 'oldsmobile', 'oldtimer', 'pagani', 'panther-westwinds', 'peugeot', 'pgo', 'piaggio', 'plymouth', 'polestar', 'pontiac', 'proton', 'puch', 'qoros', 'qvale', 'ram', 'regis', 'reliant', 'renault', 'rolls-royce', 'rover', 'ruf', 'saab', 'santana', 'savel', 'sdg', 'seat','shuanghuan', 'skoda', 'smart', 'speedart', 'spyker', 'ssangyong', 'streetscooter', 'subaru', 'suzuki', 'tagaz', 'talbot', 'tasso', 'tata', 'tazzari-ev', 'techart', 'tesla', 'town-life', 'toyota', 'trabant', 'triumph', 'tvr', 'uaz', 'vanderhall', 'vaz', 'vem', 'volvo', 'vortex', 'wallys', 'wartburg', 'westfield', 'wiesmann', 'zastava', 'zaz', 'zhidou', 'zotye', 'others']
# selection des marques qui commercialisent les voitures éléctriques
brandselection = ['audi','bmw', 'mercedes-benz', 'volkswagen', 'citroen', 'honda', 'hyundai', 'kia', 'mini', 'nissan', 'peugeot', 'renault', 'smart', 'toyota', 'volvo']
# les pays disponibles& sur Autoscout24
countrylist = ['A', 'B', 'D', 'E', 'F', 'I', 'L', 'NL']
# on s'interesse à la France
countryselection = ['F']
# filtre des prix par tranche
fromprice = 5000
toprice =  100000
pricebracket = 2001

prices = np.arange(fromprice, toprice, pricebracket).tolist()

class Searchlink_generator:
  # cette fonction permet de sortir l'url avec les marques selectionnés
  def createBrandlinks(self):
        allbrandlinks = []
        for brand in brandselection:
                brandlinks = 'https://www.autoscout24.com/lst/' + brand
                allbrandlinks.append(brandlinks)
        return allbrandlinks
  # ici on defeni l'url des voitures éléctriques + le pays
  def createBrandCountrylinks(self, allbrandlinks):
        allbrandcountrylinks = []
        for country in countryselection:
            for link in allbrandlinks:
                brandcountrylinks = link + '?sort=standard&desc=0&fuel=E&ustate=N%2CU&size=20&page=1&cy=' + country
                allbrandcountrylinks.append(brandcountrylinks) 
        return allbrandcountrylinks
  # ici on filtre les prix 
  def createBrandCountryPricelinks(self, allbrandcountrylinks):
        allbrandcountrypricelinks = []
        for price in prices:
            for link in allbrandcountrylinks:
                brandcountrylinks = link + '&pricefrom=' + str(price) + '&priceto=' + str(price+pricebracket-1)
                allbrandcountrypricelinks.append(brandcountrylinks) 
        return allbrandcountrypricelinks
  # ici extraction des liens avec un maximum de 20 pages
  def createBrandCountryPricePagelinks(self, allbrandcountrypricelinks):
        allbrandcountrypricepagelinks = []
        pages = range(1,21)
        for link in allbrandcountrypricelinks:
            for page in pages:
                brandcountrylinks = link + '&page=' + str(page)
                allbrandcountrypricepagelinks.append(brandcountrylinks) 
        return allbrandcountrypricepagelinks

searchlinks = Searchlink_generator()
allbrandcountrypricepagelinks = searchlinks.createBrandCountryPricePagelinks(searchlinks.createBrandCountryPricelinks(searchlinks.createBrandCountrylinks(searchlinks.createBrandlinks())))
allbrandcountrypricepagelinks
# sauvegarde des liens de recherche sous SQL
database = 'Frenchdatabase.db'
connection = sql.connect(database)

searchlinks = pd.DataFrame(allbrandcountrypricepagelinks)
searchlinks.to_sql('Frenchsearchlinks', connection)
# lecture dans les liens de recherche de la base de donnée
query = '''SELECT * from Frenchsearchlinks'''
searchlinks = pd.read_sql_query(query, connection).iloc[:,1].values.tolist()

class Carlink_Scraper:
  def getSoup(self, link):
        # retourne beautifulsoup sur l'url donnée
        r = requests.get(link)
        r.encoding = 'UTF-8'
        return BeautifulSoup(r.text,'lxml')

  def getAllLinks(self, link):
        # renvoi tout les liens de voitures qu'il peut trouver sur les liens de recherche.
        soup = self.getSoup(link)
        tds = soup.findAll('div', {'class':'cldt-summary-titles'})
        return ['https://www.autoscout24.com/' + td.find('a')['href'] for td in tds]

  def carlinkScraper(self):
        # la boucle passe a travers les annonces et les stock dans la DB SQL, la fonction vérifie s'il y a un max 20 voitures si non elle continue. 
        start = time.time()
        allcarlinks = []
        tracker = 0
        iterator = iter(searchlinks)
        for link in iterator:
            carlinks = self.getAllLinks(link)
            tracker = tracker + 1
            if not not carlinks:
                allcarlinks.extend(carlinks)
            if link[-2:] == '=2' and len(carlinks) !=20:
                next(islice(iterator, 17, 18), None)
                tracker = tracker + 18
            if tracker % 1000 == 0:
                autolinks = pd.DataFrame(allcarlinks)
                autolinks.to_sql('Frenchautolinks', connection, if_exists= 'append')
                allcarlinks = []

        autolinks = pd.DataFrame(allcarlinks)
        autolinks.to_sql('Frenchautolinks', connection, if_exists= 'append')
        allcarlinks = []    

        print(tracker)
        end = time.time()
        print(end - start)

getallcarlinks = Carlink_Scraper()
getallcarlinks.carlinkScraper()