import requests
import re
from urllib.parse import urljoin, urlsplit
from requests import exceptions
from contextlib import suppress
from threading import Thread, Lock
import sqlite3
from sys import exit
import csv
from datetime import date


class Crawler():


    def open_db(self):
        try:
            conn = sqlite3.connect('jobs.db', check_same_thread=False)
            cur = conn.cursor()
            query = 'select distinct url from offerts where email is NULL;'
            cursor = cur.execute(query)
            tuple_url=cursor.fetchall()
            cursor.close()

            for url in tuple_url:
                self.tmp_list.append(url[0])
        except sqlite3.DatabaseError:
            print('[-] Error connecting to database, clonsing [-]')

        return conn



    def __init__(self):
        self.tmp_list= []
        self.conn = self.open_db() 
        self.lock = Lock()
        self.mail_list = []
        self.parsed_links = []



    def extract_link_from_url(self, url):
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
                        self.lock.acquire()
                        try:
                            cur = self.conn.cursor()
                            cur.execute(query, tuple)
                            self.conn.commit()
                            cur.close()
                            self.lock.release()
                        except sqlite3.DatabaseError as e :
                            print(e)
                            self.lock.release()
                            return re.findall('(?:href=")(.*?)"',str(response.content) )

                        self.mail_list.append(mail)
                        print(f'[+] Found email address {mail} for {base_url} [+]')
                        return [] 

            return re.findall('(?:href=")(.*?)"',str(response.content) )


    def crawl(self, url):
        href_links=self.extract_link_from_url(url)

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
                                        self.crawl(link)
        else:
            exit()


    def lunch_threads( self, domains):
        threads = []
        for url in domains:
            tr = Thread( target = self.crawl, args=(url,) )
            threads.append(tr)
            threads[-1].start()

        for thread in threads:
            thread.join()


    
    def create_csv(self):
        
        today = str(date.today())
        query_email = "select title, url, email from offerts where email != 'unknown'"
        result_set=None
        try:
            cur = self.conn.cursor()
            result_set = cur.execute(query_email)
        except sqlite3.DataError as e:
            print(e)
        finally:
            if result_set:
                with open( f'jobs_{today}.csv', 'w' ) as file:
                    writer = csv.writer(file)
                    for row in result_set:
                        writer.writerow([ row[0], row[1], row[2] ])
                
                cur.close()





    def main(self):
        self.lunch_threads(self.tmp_list)
        query_update = "update offerts set email='unknown' where email is null;"
        try:
            cur = self.conn.cursor()
            cur.execute(query_update)
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            print(e)

        print('[+] Genereting csv file whit founded emails [+]')
        self.create_csv()
        self.conn.close()






