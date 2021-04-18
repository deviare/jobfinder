import sqlite3
from sys import exit
from time import sleep
from datetime import date
from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait



class linkedin():

    
    def set_driver(self,headless):
        opt =Options()
        opt.headless = headless
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", "Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident    /7.0; rv:11.0) like Gecko") 
        profile.set_preference("media.peerconnection.enabled", False)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.set_preference('use.automation.extension', False)
        profile.set_preference('webdriver_accept_untrusted_certs', 'undefined' )
        profile.set_preference('webdriver_assume_untrusted_issuer', 'undefined')
        profile.set_preference('webdriver_enable_native_events', 'undefined')
        
        return webdriver.Firefox(profile, options=opt, firefox_binary='/usr/bin/firefox-esr',executable_path='/usr/local/bin/geckodriver')


    def create_db(self):
        try:
            conn = sqlite3.connect('jobs.db') 
            cur = conn.cursor()
            query = ' create table if not exists offerts ( title CHAR(100), email CHAR(50), apply BOOLEAN DEFAULT 0, search CHAR(100), url char(200), date_add CHAR(20), date_apply CHAR(20), id INTEGER PRIMARY KEY);'
            cur.execute(query)
        except sqlite3.DatabaseError as r:
            print('[-] Error connecting with database [-]', r) 
            exit(1)
        return conn
   
   
    def __init__(self, usr, passwd, headless ):
        self.br= self.set_driver(headless) 
        self.conn = self.create_db()
        self.username = usr
        self.password = passwd
        self.city=''
        self.job=''

              
    def login(self):
        
        self.br.set_window_size(1000,650)
        print('[+] Starting reserch for website company on linkedin.com [+]')
        self.br.get('https://www.linkedin.com/login')
        usr_input=WebDriverWait(self.br, 30).until( lambda br : br.find_element_by_xpath('//*[@id="username"]') )
        pass_input=self.br.find_element_by_xpath('//*[@id="password"]')
        buttons_in_page = self.br.find_elements_by_tag_name('button')
        login_btn = [ btn for btn in buttons_in_page if 'Sign in' in btn.text ][0]

        usr_input.send_keys(self.username)
        pass_input.send_keys(self.password)
        login_btn.click()
        sleep(5)

        try:
            search_tab = WebDriverWait(self.br, 30).until( lambda br  : br.find_element_by_xpath('/html/body/div[9]/header/div[2]/nav/ul/li[3]'))
        except TimeoutException as e:
            search_tab = WebDriverWait(self.br, 30).until( lambda br :  br.find_element_by_xpath('/html/body/div[8]/header/div[2]/nav/ul/li[3]'))

        self.close_stuff()
        search_tab.click()


    def look_for_jobs(self, job, city):
        sleep(3)
        job_id, location_id=self.get_inputs_ids()
        input_job=self.br.find_element_by_id(job_id)
        input_place=self.br.find_element_by_id(location_id)
        btn_search = self.find_button()
        input_job.clear()
        input_place.clear()
        input_job.send_keys(job) 
        input_place.send_keys(city)
        self.job=job
        self.city=city
        btn_search.click()
        sleep(3) 
       

    def close_stuff(self):
        
        # closing chat 
        sleep(10)
        spans_in_page = WebDriverWait(self.br, 30).until( lambda br : br.find_elements_by_tag_name('span'))

        #start_span = [ span for span in spans_in_page if 'Messaggistica' in span.text]

        for span in spans_in_page:
            if 'Messaging' in span.text:
                if span.get_attribute('aria-hidden') == 'true':
                    start_span=span
    
        close_chat_btn = start_span.find_element_by_xpath('./../../../../section[2]/button[2]')

        try:
            close_chat_btn.click()
        except:
            print('[-] chat not close [-]')


    def go_to_bottom(self):
        sleep(2)
        jobs_list= self.find_ul()
        action_chain=ActionChains(self.br)
        self.br.execute_script("window.focus();")
        action_chain.move_to_element(jobs_list).pause(3).send_keys(Keys.SHIFT).perform()
        scroll_div=jobs_list.find_element_by_xpath("./..")
        for x in range(20):
            scroll_div.send_keys(Keys.PAGE_DOWN)
            sleep(1) 


    def find_pages(self):
        pages_btn = []
        try:
            pages_ul = self.br.find_element_by_css_selector('.artdeco-pagination__pages')
        except NoSuchElementException:
            print('[-] No more page found [-]')
            return []
        pages_li_list = pages_ul.find_elements_by_tag_name('li')
        for li in pages_li_list:
            page_btn = li.find_element_by_tag_name('button')
            pages_btn.append(page_btn)

        return pages_btn

        
    def get_company_urls(self):
        link_list = []
        jobs_list= self.find_ul()
        li_elements=jobs_list.find_elements_by_tag_name("li")
        for ele in li_elements:
            links=ele.find_elements_by_tag_name("a")
            for link in links:
                href=link.get_attribute("href")
                if "company" in href:
                   link_list.append(link)
        link_list=self.unique(link_list)
        return link_list



    def extract_company(self):
        page_btns = self.find_pages() 
        if len(page_btns) > 0:
            for index in range(1,len(page_btns)):
                self.go_to_bottom()
                page_btns = self.find_pages() 
                link_list = self.get_company_urls()
                self.get_urls(link_list)
                page_btns[index].click()
        else:
            self.go_to_bottom()
            link_list = self.get_company_urls()
            self.get_urls(link_list)



    def switch_to_wind0(self):
        wind_1=self.br.window_handles[1] 
        self.br.switch_to.window(wind_1)
        self.br.close()
        wind_0=self.br.window_handles[0]
        self.br.switch_to.window(wind_0)

    def get_urls(self, link_list):    
        ctrl = False
        job_dic = {}
        today = str(date.today())
        try:
            query = 'select title, url from offerts;'
            cur = self.conn.cursor()
            result = cur.execute(query).fetchall()
        except sqlite3.DatabaseError as e:
            title_list  = []
            print(e)

        for link in link_list:
            try:
                title_link =  WebDriverWait(link ,10).until( lambda link : link.find_element_by_xpath('./../../div/a') )
            except TimeoutException:
                print(f'[-] Error parsing current offert... passing to the next one [-]')
                continue


            title_href = title_link.get_attribute('href')
            if '/jobs' in title_href:
                title= title_link.text
            else:
                title = 'unknown'
            link.send_keys(Keys.CONTROL + Keys.RETURN)
            sleep(2)
            wind_1=self.br.window_handles[1] 
            self.br.switch_to.window(wind_1)
            a_link = self.find_link()

            self.check_ban()

            if a_link is None:
                self.switch_to_wind0()
                continue 
            
            next_offert  = False
            site_url = a_link.get_attribute('href')
            for touple in result:
                tit, url = touple
                if title == tit:
                    if site_url == url:
                        print(f' [-] Offert already in databese, passing to the next one [-]')
                        self.switch_to_wind0()
                        next_offert = True
                        break
            if next_offert:
                continue

            print(f'[+] found new offerts {title} by {site_url} [+]')
            try:
                offert = ( title , f'{self.job}:{self.city.strip()}', site_url, today, )
                c = self.conn.cursor()
                c.execute(
                        'INSERT INTO offerts (title, search, url, date_add) '+
                        'VALUES (?,?,?,?)', offert
                        )
                self.conn.commit()
            except sqlite3.DatabaseError as e:
                print(e)

            self.switch_to_wind0()

    def check_ban(self):
        try:
            h1_list = self.br.find_elements_by_tag_name('h1')
            canary = [ h1 for h1 in h1_list if h1.text == 'Sign up for free to get more' ]
            if canary:
                print('[-] Probably you have been banned... passing to crawling stage [-]')
                self.close_driver()
                self.conn.close()
                exit(1)
        except:
            pass

    def unique(self, list1): 
        unique_list = [] 
        text_list = []
        for x in list1: 
            if x.text not in text_list: 
                text_list.append(x.text)
                unique_list.append(x) 
        return unique_list


    def get_inputs_ids(self):
        job_id=""
        location_id=""
        inputs=self.br.find_elements_by_tag_name("input")
        for inputx in inputs:
            id_tmp=inputx.get_attribute("id")
            if "keyword" in id_tmp:
                job_id=id_tmp
            elif "location" in id_tmp:
                location_id=id_tmp

        return job_id, location_id


    def find_link(self):
        try:
            icon_external =  WebDriverWait(self.br, 30).until( lambda br : br.find_element_by_css_selector('[d="M15 1v6h-2V4.41L7.41 10 6 8.59 11.59 3H9V1zm-4 10a1 1 0 01-1 1H5a1 1 0 01-1-1V6a1 1 0 011-1h2V3H5a3 3 0 00-3 3v5a3 3 0 003 3h5a3 3 0 003-3V9h-2z"]'))
            parent_link = icon_external.find_element_by_xpath("./../../../..")
        except TimeoutException:
            print('[-] Company site not found [-]')
            return None
        return parent_link

    def find_ul(self):
        sleep(3)
        try:
            list2 = self.br.find_element_by_xpath('/html/body/div[9]/div[3]/div[3]/div/div/section[1]/div/div/ul')
            jobs_list=list2
        except:
            pass
        try:
            list2 = self.br.find_element_by_css_selector('.jobs-search-results__list')
            jobs_list=list2
        except:
            pass

        return jobs_list


    def find_button(self):

        try:
            btn1=self.br.find_element_by_xpath('/html/body/div[9]/div[3]/div/section/section[1]/div/div/button')
            btn_search = btn1
        except:
            pass
        try:
            btn3=self.br.find_element_by_xpath("/html/body/div[9]/header/div[2]/div/div/div/button")
            btn_search=btn3
        except:
            pass
        try:
            btns = self.br.find_elements_by_tag_name("button")
            btn_search = [ btn for btn in btns if btn.text == 'Search' ][0]
        except BaseException as e:
            pass

        return btn_search

    def close_driver(self):
        self.conn.close()
        self.br.quit()
        print('[+] Closing WebDriver [+]')
