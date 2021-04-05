from time import sleep
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
        conn = sqlite3.connect('jobs.db')
        query = ' create table if not exists offerts ( title CHAR(100), email CHAR(50), apply BOOLEAN DEFAULT 0, search CHAR(100), url char(200), id INTEGER PRIMARY KEY);'
        conn.execute(query)
        return conn
   
   
    def __init__(self, usr, passwd, headless ):
        self.br= self.set_driver(headless) 
        self.conn = self.create_db()
        self.username = usr
        self.password = passwd

              
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
            search_tab = WebDriverWait(self.br, 30).until( lambda br : br.find_element_by_xpath('/html/body/div[8]/header/div[2]/nav/ul/li[3]'))
        except TimeoutException as e:
            search_tab = WebDriverWait(self.br, 30).until( lambda br : br.find_element_by_xpath('/html/body/div[9]/header/div[2]/nav/ul/li[3]'))

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
        btn_search.click()
        sleep(3) 
       

    def close_stuff(self):
        
        # closing chat 
        sleep(10)
        spans_in_page = WebDriverWait(self.br, 30).until( lambda br : br.find_elements_by_tag_name('span'))

        start_span = [ span for span in spans_in_page if 'Messaggistica' in span.text]

        for span in spans_in_page:
            if 'Messaggistica' in span.text:
                if span.get_attribute('aria-hidden') == 'true':
                    start_span=span
    
        close_chat_btn = start_span.find_element_by_xpath('./../../../../section[2]/button[2]')

        try:
            close_chat_btn.click()
        except:
            print('[-] chat not close [-]')


    def go_to_bottom(self):
        jobs_list= self.find_ul()
        sleep(2)
        action_chain=ActionChains(self.br)
        self.br.execute_script("window.focus();")
        action_chain.move_to_element(jobs_list).pause(3).send_keys(Keys.SHIFT).perform()
        scroll_div=jobs_list.find_element_by_xpath("./..")
        for x in range(30):
            scroll_div.send_keys(Keys.PAGE_DOWN)
            sleep(1)

    def extract_company(self):
        urls_list=[]
        link_list=[]
        self.go_to_bottom()
        jobs_list= self.find_ul()
        li_elements=jobs_list.find_elements_by_tag_name("li")
        sleep(3)
        for ele in li_elements:
            links=ele.find_elements_by_tag_name("a")
            for link in links:
                href=link.get_attribute("href")
                if "company" in href:
                   link_list.append(link)
        link_list=self.unique(link_list)
        return link_list
       

    def get_urls(self, link_list):    
        urls_list = []
        ctrl = False
        try:
            query = 'select title from offerts;'
            cur = self.conn.cursor()
            title_list = cur.execute(query).fetchall()
        except sqlite3.DatabaseError as e:
            title_list = []
            print(e)

        for link in link_list:
            title_link = link.find_element_by_xpath('./../../div/a')
            title_href = title_link.get_attribute('href')
            if '/jobs' in title_href:
                title= title_link.text
                for title_job in title_list:
                    if title in title_job[0]:
                        ctrl=True            
            else:
                title = 'unknown'
            if ctrl:
                continue
            link.send_keys(Keys.CONTROL + Keys.RETURN)
            sleep(5)
            wind_1=self.br.window_handles[1] 
            self.br.switch_to.window(wind_1)
            a_link = self.find_link()        
            if a_link is None:
                self.br.switch_to.window(wind_1)
                self.br.close()
                wind_0=self.br.window_handles[0]
                self.br.switch_to.window(wind_0)
                continue
            site_url = a_link.get_attribute('href')     
            print(f'[+] found site -> {site_url} [+]')
            urls_list.append(site_url)
            try:
                offert = ( title , f'{self.job}:{self.city.strip()}', site_url, )
                c = self.conn.cursor()
                c.execute(
                        'INSERT INTO offerts (title, search, url) '+
                        'VALUES (?,?,?)', offert
                        )
                self.conn.commit()
            except sqlite3.DatabaseError as e:
                print(e)
            except BaseError as e:
                print(e)

            self.br.switch_to.window(wind_1)
            self.br.close()
            wind_0=self.br.window_handles[0]
            self.br.switch_to.window(wind_0)

                

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
        sleep(10)
        try:
            icon3=self.br.find_element_by_css_selector('[d="M15 1v6h-2V4.41L7.41 10 6 8.59 11.59 3H9V1zm-4 10a1 1 0 01-1 1H5a1 1 0 01-1-1V6a1 1 0 011-1h2V3H5a3 3 0 00-3 3v5a3 3 0 003 3h5a3 3 0 003-3V9h-2z"]')
            site_icon=icon3
        except:
            pass

        try:
            parent_link=site_icon.find_element_by_xpath("./../../../..")
        except:
            print('[-] Site of company not found [-]')
            return None
        return parent_link

    def find_ul(self):
        sleep(10)
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
            btn_search = [ btn for btn in btns if btn.text == 'Cerca' ][0]
        except BaseException as e:
            pass

        return btn_search

    def close_driver(self):
        self.conn.close()
        self.br.quit()
