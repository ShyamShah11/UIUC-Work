from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import re 
import urllib
import time

#create a webdriver object and set options for headless browsing
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

#uses webdriver object to execute javascript code and get dynamically loaded webcontent
def get_js_soup(url,driver):
    driver.get(url)
    res_html = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
    return soup

#tidies extracted text 
def process_bio(bio):
    bio = bio.encode('ascii',errors='ignore').decode('utf-8')       #removes non-ascii characters
    bio = re.sub('\s+',' ',bio)       #repalces repeated whitespace characters with single space
    return bio

''' More tidying
Sometimes the text extracted HTML webpage may contain javascript code and some style elements. 
This function removes script and style tags from HTML so that extracted text does not contain them.
'''
def remove_script(soup):
    for script in soup(["script", "style"]):
        script.decompose()
    return soup


#Checks if bio_url is a valid faculty homepage
def is_valid_homepage(bio_url,dir_url):
    if bio_url.endswith('.pdf'): #we're not parsing pdfs
        return False
    try:
        #sometimes the homepage url points to the same page as the faculty profile page
        #which should be treated differently from an actual homepage
        ret_url = urllib.request.urlopen(bio_url).geturl() 
    except:
        return False       #unable to access bio_url
    urls = [re.sub('((https?://)|(www.))','',url) for url in [ret_url,dir_url]] #removes url scheme (https,http or www) 
    return not(urls[0]== urls[1])

#extracts all Faculty Profile page urls from the Directory Listing Page
def scrape_dir_page(dir_url,driver):
    print ('-'*20,'Scraping directory page','-'*20)
    faculty_links = []
    faculty_base_url = 'https://www.eng.mcmaster.ca'
    #execute js on webpage to load faculty listings on webpage and get ready to parse the loaded HTML 
    soup = get_js_soup(dir_url,driver)     
    for link_holder in soup.find_all('h3',class_='card-title'): #get list of all <div> of class 'name'
        rel_link = link_holder.find('a')['href'] #get url
        #url returned is relative, so we need to add base url
        faculty_links.append(faculty_base_url+rel_link) 
    print ('-'*20,'Found {} faculty profile urls'.format(len(faculty_links)),'-'*20)
    return faculty_links


def scrape_faculty_page(fac_url,driver):
    soup = get_js_soup(fac_url,driver)
    homepage_found = False
    bio_url = ''
    bio = ''
    
    #add their name to the bio for the ones with empty bios
    name_sec = soup.find('h1', class_='media-heading')
    bio = bio + process_bio(name_sec.text) + " "
    #add their titles to the bio
    pos_sec = soup.find('div', class_='media-body')
    titles = pos_sec.find_all('p')
    for row in titles:
        bio = bio + process_bio(row.getText())+ " "


    #check if there is an overview tab
    nav_sec = soup.find('nav',class_='navbar navbar-expand-md navigation-menu page-tabs')
    if nav_sec == None: #the profile page is empty
        return (fac_url, bio)
        
    selected_sec = nav_sec.find('li', class_='active')
    selected_tab = ""
    for link in selected_sec.find_all('a'):
        selected_tab = link['href']
    if selected_tab == "#overview": #there is an overview tab
        bio_sec = soup.find('div', class_='tab-content')
        bio_text = bio_sec.find_all('p',class_=False)
        bio_url=fac_url+"#overview"
        bio = bio + process_bio(bio_text[0].getText()) #add overview text to bio
    else: #there is no overview tab
        bio_url=fac_url


    return bio_url,bio


def write_lst(lst,file_):
    with open(file_,'w') as f:
        for l in lst:
            f.write(l)
            f.write('\n')




bio_urls_file = './bio_urls.txt'
bios_file = './bios.txt'

dir_url = 'https://www.eng.mcmaster.ca/civil/people/faculty' #url of directory listings of civil eng faculty
faculty_links = scrape_dir_page(dir_url,driver)

bio_urls, bios = [],[]
tot_urls = len(faculty_links)
for i,link in enumerate(faculty_links):
    print ('-'*20,'Scraping faculty url {}/{}'.format(i+1,tot_urls),'-'*20)
    bio_url,bio = scrape_faculty_page(link,driver)
    bio_urls.append(bio_url.strip())
    bios.append(bio)
driver.close()


write_lst(bio_urls,bio_urls_file)
write_lst(bios,bios_file)