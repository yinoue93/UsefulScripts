# -*- coding: utf-8 -*-
import sys, os, shutil

import urllib
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
from posixpath import basename

import threading

def pdf_downloader(folderName,url,count):
    response = urllib2.urlopen(url)
    filename = str(count)+'_'+basename(url)
    file = open(folderName+'\\'+filename, 'wb')
    file.write(response.read())
    file.close()
    print(url+' completed')
    sema.release()
    exit()

if __name__ == "__main__":
    url = "http://web.stanford.edu/class/cs231a/schedule.html"
    folderName = "CS231A"

    # make the directory for the created files
    try:
        os.mkdir(folderName)
    except:
        pass
    
    max_thread = 5
    sema = threading.Semaphore(max_thread)

    # download the html
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")

    # download the pdfs
    thread_list = []
    count = 0
    for link in soup.findAll('a'):
        content = link.get('href')
        if '.pdf' in content:
            abs_url = urljoin(url,content)
            print abs_url
            sema.acquire(True)
            th = threading.Thread(target=pdf_downloader, args=(folderName,abs_url,count))
            thread_list.append(th)
            th.start()
            count = count+1
    
    for th in thread_list:
        th.join()
    
    print "done"
