#!/usr/bin/python3
###
# Given a list of URLs,
# scrape and extract content with structure
# so that it may be fed into Top2Vec
###

import os
import sys
import pickle
import math
import asyncio
import aiohttp
from aiohttp.resolver import AsyncResolver
from throttler import Throttler
from bs4 import BeautifulSoup

## Calculate human-friendly byte size string
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    if size_bytes is None:
        return "0B (None)"
    if isinstance(size_bytes, str):
        size_bytes = int(size_bytes)
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

## Extract text from HTML
def preprocess_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html5lib')
    text_content = soup.get_text(separator=' ', strip=True)
    return text_content

## Reverse ordering of domains in URL
def reverse_url(url):
    parts = url.split('.')
    reversed_parts = parts[::-1]  # Reverse the order of parts
    reversed_url = '.'.join(reversed_parts)
    return 'https://' + reversed_url

## Download HTML data from URL, async style
async def get_html(throttler, session, url, sslerrorfile, errorfile, redofile, timeoutfile):
    raw_html = ""
    try:
        async with throttler:
            async with session.get(reverse_url(url)) as resp:
                raw_html = await resp.content.read() #Read all content
    except aiohttp.ClientSSLError as se:
        print(url, se, file=sslerrorfile)
        return
    except aiohttp.ServerTimeoutError as te:
        print(url, te, file=timeoutfile)
        return
    except aiohttp.ClientError as ce:
        print(url, file=redofile)
        return
    except Exception as e:
        print(url, e, file=errorfile)
        return
    processed_html = preprocess_html(raw_html)
    if len(processed_html) == 0 or processed_html is None:
        print(url, "Length Zero!", file=errorfile)
        return;
    print("\t...", url)
    return { "url": url, "content": ' '.join(processed_html.split()) }

## Download HTML data from URL, async style
async def crawl_html(url_list, sslerrorfile, errorfile, redofile, timeoutfile ):
    print("Initializing crawler...")
    resolver = AsyncResolver(nameservers=["192.168.1.1"])
    connector = aiohttp.TCPConnector(limit=64, ttl_dns_cache=None, resolver=resolver)
    timeout = aiohttp.ClientTimeout(connect=120, sock_connect=30, sock_read=60)
    throttle = Throttler(rate_limit=1024, period=90)
    headers = { "Accept": "text/html",
                "Accept-Encodings": "gzip, deflate, br",
                "Accept-Language": "*",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"
              }
    async with aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers) as session:
        tasks = [get_html(throttle, session, url, sslerrorfile, errorfile, redofile, timeoutfile) for url in url_list]
        return await asyncio.gather(*tasks)

def crawl(urlFile):
    url_list = []  # List of URLs pointing to raw HTML documents
    preprocessed_data = []

    #Load preprocessed_data from file cache
    try:
      with open('cache.crawl', 'rb') as file:
        preprocessed_data = pickle.load(file)
        print('Crawl object loaded from cache', len(preprocessed_data))
    except IOError as e:
        print("Error reading crawler cache file:", e)
    
    #Load new URLs from input file
    if urlFile:
      with open(urlFile) as url_list_file:
        url_list = [line.strip() for line in url_list_file]
        
        #Remove cached URL from the crawl list
        url_list = [url for url in url_list if url not in [page["url"] for page in preprocessed_data] ]

        # Crawl the urls and store the content
        print("Starting crawler...")
        ssllog = open("ssl-error.log", 'w')
        errorlog = open("error.log", 'w')
        timeoutlog = open("timeout-error.log", 'w')
        redolog = open("redo.log", 'a')

        loop = asyncio.get_event_loop()
        preprocessed_data += loop.run_until_complete(crawl_html(url_list, ssllog, errorlog, redolog, timeoutlog))
        preprocessed_data = [page for page in preprocessed_data if page is not None]
        print("Crawling complete.", len(preprocessed_data))
      
        ##Save crawl cache to disk
        print("Caching crawl data to disk...")
        with open('cache.crawl', 'wb') as file:
          pickle.dump(preprocessed_data, file)
          print('Crawl object written to cache')

    #Make preprocessed data unique by URL
    url_list = []
    uniquelist = []
    for page in preprocessed_data:
        if page["url"] not in url_list:
            uniquelist.append(page)
            url_list.append(page["url"])
        
    return uniquelist
