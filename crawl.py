"""
    This is a crawler for the following website:
"""
import os
import re
import urllib
import urllib2
import urlparse
import itertools
import multiprocessing as mp
from bs4 import BeautifulSoup

main_page = "https://www.farfetch.cn"
seed = "https://www.farfetch.cn/uk/shopping/women/clothing-1/items.aspx"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/61.0.3163.79 Safari/537.36"}
store_file = "fashion"
path = os.path.join(os.getcwd(), store_file)
cate_list = {   "category-136253": "All In One",
                "category-136293": "Beachwear",
                "category-136227": "Coats",
                "category-136043": "Denim",
                "category-135979": "Dresses",
                "category-136226": "Jackets",
                "category-136245": "Knits",
                "category-136071": "Lingerie & Hosiery",
                "category-136045": "Shorts",
                "category-135985": "Skirts",
                "category-136021": "Suits",
                "category-135983": "Tops",
                "category-135981": "Trousers"   }
lock = mp.Lock()

# The network sometimes breaks.
# Use this function to skip the page we have crawled
# when we have to restart the crawler.
def check_crawl(url, checked_file):
    with open(checked_file, "r") as f:
        return url+'\n' in f.readlines()


def get_catagory(url_seed):
    """ store all the categories we need. """
    content = urllib2.urlopen(url_seed)
    soup = BeautifulSoup(content, "lxml")
    cata_links = soup.findAll("a", {"id": re.compile(r"category-\d+"),
                                    "class": "tree-title"})
    print len(cata_links)
    for i in range(len(cata_links)):
        print "\""+cata_links[i].get('id')+"\": "+"\""+cata_links[i].get('title')+"\","

def get_product_page(url_seed):
    """
    Store all of the product page into a txt file
    :param url_seed: a BeautifulSoup object that represents the initial page url of Farfetch
    :return: a page queue
    """
    for category in cate_list.keys():
        to_crawl_url = url_seed+"?category="+category[-6:]
        content = urllib2.urlopen(to_crawl_url)
        soup = BeautifulSoup(content, "lxml")
        total_page = eval(soup.find("span", {"class": "js-lp-pagination-all",
                                             "data-tstid": "paginationTotal"}).string)
        for i in range(1, total_page+1):
            to_crawl_suburl = to_crawl_url + "&page={0}".format(i)
            req = urllib2.Request(to_crawl_suburl, headers=header)
            if check_crawl(to_crawl_suburl, "crawled_url.txt"):
                print "This page has been crawled!! {}".format(to_crawl_suburl)
                continue
            try:
                _content = urllib2.urlopen(req, timeout=30)
                _soup = BeautifulSoup(_content, "lxml")
                page_list = _soup.findAll("a", {"target": "_self"})
                if not os.path.exists("product_page_{}.txt".format(cate_list[category])):
                    f = open("product_page_{}.txt".format(cate_list[category]), "w")
                    f.close()
                with open("product_page_{}.txt".format(cate_list[category]), "a") as f:
                    for j in range(len(page_list)):
                        f.write(page_list[j].get('href')+'\n')
                print "Crawling category {0} page {1} complete!".format(cate_list[category], i)

                with open("crawled_url.txt", "a") as f:
                    f.write(to_crawl_suburl+"\n")
            except Exception as e:
                print e

def crawl_product_page():
    """ Crawl the concrete product information. """
    to_crawl_cate = [c for c in os.listdir(os.getcwd()) if re.compile(r"product_page_(\w+).txt").match(c)]
    for cate in to_crawl_cate:
        with open(cate, "r") as f:
            to_crawl_product_list = f.readlines()

        pool_size = mp.cpu_count() * 2
        pool = mp.Pool(processes=pool_size)
        pool.map(crawler, to_crawl_product_list)

        pool.close()
        pool.join()


def crawler(product):
    global lock
    product_full_page = urlparse.urljoin(main_page, product.strip('\n'))
    req = urllib2.Request(product_full_page, headers=header)
    if check_crawl(product_full_page, "crawled_product.txt"):
        print "This page has been crawled!! {}".format(product_full_page)
        return
    try:
        content = urllib2.urlopen(req, timeout=30)
        soup = BeautifulSoup(content, "lxml")
        imgs = soup.findAll("img", {"itemprop": "image",
                                    "class": "responsive js-blurload ff-blurload"})
        brand = soup.find("a", {"itemprop": "brand"}).string
        name = soup.find("span", {"itemprop": "name"}).string.strip()
        price = soup.find("span", {"class": "listing-price js-price"}).string
        info_list = [brand, name, price]
        info_list += [i.get("data-large") for i in imgs]
        info = "\t".join(info_list).encode('utf-8') + '\n'

        with lock:
            with open("product.txt", "a") as f:
                f.write(info)
            print "Crawl product {} successfully!".format(name)

            with open("crawled_product.txt", "a") as f:
                f.write(product_full_page + '\n')
    except Exception as e:
        print e

def crawler_start(a_b):
    """ A strange way to deal with multiprocessing. """
    return crawler(*a_b)

def update():
    id = 1000000
    pic = []
    with open("product_final.txt", "a") as f:
        with open("product.txt", "r") as pf:
            l = pf.readlines()
            for i in range(id, id+len(l)):
                pic += l[i-id].split('\t')[3:]
                info = l[i-id].split('\t')[:3]
                info = [str(i)] + info

                product_info = '\t'.join(info)+'\n'
                f.write(product_info)
                print "write info: {}".format(product_info)
    print len(pic)

if __name__ == '__main__':
    update()
