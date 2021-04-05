import requests
import re
from urllib.parse import urljoin, urlsplit
from requests import exceptions
from contextlib import suppress
from threading import Thread, Lock
import sqlite3



class Crawler():


    def open_db(self):
        conn = sqlite3.connect('jobs.db', check_same_thread=False)
        cur = conn.cursor()
        query = 'select distinct url from offerts where email is NULL;'
        cursor = cur.execute(query)
        tuple_url=cursor.fetchall() 
        for url in tuple_url:
            self.tmp_list.append(url[0])

        return conn



    def __init__(self):
        self.tmp_list= []
        self.conn = self.open_db() 
        self.mail_list = []
        self.parsed_links = []



    def extract_link_from_url(self, lock, url):
        agent = {'User-Agent': 'Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        with suppress(requests.exceptions.InvalidSchema , requests.exceptions.ConnectionError):
            response=requests.get(url,headers=agent)
            mails = re.findall('([a-zA-Z0-9-_.]{1,20}?@[a-zA-Z0-9-._+]+?\.[a-zA-Z]{3})', str(response.content))


            if mails:
                for mail in mails:
                    if '.png'   not in mail and '.jpg' not in mail:
                        splitted = urlsplit(url)
                        base_url = splitted[1]
                        tuple = ( mail, base_url )
                        query = "update offerts set email=(?) where url like '%'||(?)||'%';"
                        lock.acquire()
                        try:
                            cur = self.conn.cursor()
                            cur.execute(query, tuple)
                            self.conn.commit()
                            lock.release()
                        except sqlite3.DatabaseError as e :
                            print(e)
                            lock.release()
                            return re.findall('(?:href=")(.*?)"',str(response.content) )

                        self.mail_list.append(mail)
                        return False 

            return re.findall('(?:href=")(.*?)"',str(response.content) )


    def crawl(self, lock, url):
        href_links=self.extract_link_from_url(lock, url)

        if href_links:
            for link in href_links:
                link = urljoin(url,str(link))
                if "#" in link:
                    link = link.split("#")[0]
                page = re.search('p=\d+$',link)
                if url in link and page is None:
                    if '.css' not in link and '.js' not in link and 'start=' not in link:
                        if '.png' not in link and '.jpg' not in link:
                            if 'page' not in link and 'offerte-lavoro' not in link:
                                if len(link) < 1000:
                                    if link not in self.parsed_links:
                                        self.parsed_links.append(link)
                                        self.crawl(lock, link)


    def lunch_threads( self, domains):
        
        threads = []
        lock = Lock()

        for url in domains:
            tr = Thread( target = self.crawl, args=( lock, url ) )
            threads.append(tr)
            threads[-1].start()

        for thread in threads:
            thread.join()



    def main(self):
        self.lunch_threads(self.tmp_list)
        query_update = "update offerts set email='unknown' where email is null;"
        try:
            cur = self.conn.cursor()
            cur.execute(query_update)
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            print(e)
        self.conn.close()






