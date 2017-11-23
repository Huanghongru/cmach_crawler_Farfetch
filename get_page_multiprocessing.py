import os
import urllib
import itertools
import multiprocessing as mp

id = 1000000
store_file = "fashion"

def crawl_product_image(url, name):
    if name in os.listdir(os.path.join(os.getcwd(), store_file)):
        print "image {} already exists!".format(name)
    else:
        try:
            urllib.urlretrieve(url, os.path.join(os.getcwd(), store_file)+'\\'+name)
            print "retrieve image {} successfuly".format(name)
        except Exception as e:
            print e

def crawl_product_image_start(a_b):
    """ A strange way for multiprocessing. """
    return crawl_product_image(*a_b)

def Get_images():
    to_crawl = []
    name = []
    with open("product.txt", "r") as f:
        l = f.readlines()
        for i in range(id, id+len(l)):
            subimgs = l[i-id].strip('\n').split('\t')[3:]
            to_crawl += l[i-id].strip('\n').split('\t')[3:]
            for j in range(len(subimgs)):
                name.append("{0}_{1}.jpg".format(i, j))
    pool_size = mp.cpu_count() * 2
    pool = mp.Pool(processes=pool_size)
    pool.map(crawl_product_image_start, itertools.izip(to_crawl, name))

if __name__ == '__main__':
    Get_images()