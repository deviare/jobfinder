import requests
import re
from urllib.parse import urljoin
from requests import exceptions
from contextlib import suppress

from concurrent.futures import ThreadPoolExecutor

target_links = []
tmp_list=[]

def extract_link_from_url(url):
    agent = {'User-Agent': 'Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    with suppress(requests.exceptions.InvalidSchema , requests.exceptions.ConnectionError):
        response=requests.get(url,headers=agent)
        mails = re.findall('([a-zA-Z0-9-_.]{1,20}?@[a-zA-Z0-9-._+]+?\.[a-zA-Z]{3})', str(response.content))
        if mails:
            for mail in mails:
                if '.png' not in mail and '.jpg' not in mail:
                    print(mail)
                    with open('emails.txt', 'a') as out:
                        out.write(mail+'\n')
        
        return re.findall('(?:href=")(.*?)"',str(response.content))


def crawl(url):
    href_links=extract_link_from_url(url)
    if href_links:
        for link in href_links:
            link = urljoin(url,str(link))
            if "#" in link:
                link = link.split("#")[0]
            
            page = re.search('p=\d+$',link)
            if url in link and page is None:
                if '.css' not in url and '.js' not in url and 'start=' not in url:
                    if '.png' not in url and '.jpg' not in url:
                        if 'page' not in link and 'offerte-lavoro' not in link:
                            if link not in target_links:
                                target_links.append(link)
                                crawl(link)


def lunch_threads(num,domains):
    with ThreadPoolExecutor(max_workers=num) as executor:
        executor.map(crawl, domains) 


def main():
    with open("url_list.txt","r") as url_list:
        for url in url_list.readlines():
            url= re.search('http.{0,1}://.+?/',url) 
            if url is not None:
                tmp_list.append(url.group(0).strip())

    thread_num = len(tmp_list)
    lunch_threads(thread_num,tmp_list)




