# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from selenium import webdriver
import urlparse

from flipkart import settings
from flipkart.items import FlipkartItem

class FkartSpider(scrapy.Spider):
	handle_httpstatus_list = [403]
	name = "fkart"
	allowed_domains = 'https://www.flipkart.com/'
	start_urls = [
				"https://www.flipkart.com/mens-footwear/sports-shoes/pr?facets.availability[]=Exclude+Out+of+Stock&p%5B%5D=facets.filter_standard%255B%255D%3D1&p%5B%5D=facets.type%255B%255D%3DRunning%2BShoes&sid=osp%2Fcil%2F1cu&otracker=clp_metro_expandable_1_sport-categ-6a62b_Running_sports-shoes-store_0d1e241f-23e2-4cc9-aa0d-4b82db66e460_wp4",
				# "https://www.flipkart.com/womens-clothing/pr?sid=2oq,c1r"
		]
		
	download_delay = 1.0

	def __init__(self, *args, **kwargs):
		self.driver = webdriver.PhantomJS()
		# self.driver.set_window_size(1124, 850) # set browser size.
		super(FkartSpider, self).__init__(*args, **kwargs)

	def parse(self, response):
		self.driver.get(response.url)
		items = FlipkartItem()
		category = self.driver.find_element_by_xpath('//*[@id="container"]/div/div[2]/div[2]/div/div[2]/div/div[1]/div/div[2]/h1').text
		if category is not None:
			items['category'] = category
		else:
			items['category'] = ""
		for sel in self.driver.find_elements_by_xpath('//*[@id="container"]/div/div[2]/div[2]/div/div[2]/div/div[3]/div/div/div'):
			item_name = sel.find_element_by_css_selector('div > a._2cLu-l').text
			if item_name is not None:
				items['item_name'] = item_name
			else:
				items['item_name'] = ""
			URL = sel.find_element_by_css_selector('div > a._2cLu-l').get_attribute('href')
			items['URL'] = URL
			Price = sel.find_element_by_css_selector('div > div._1vC4OE').text
			if Price is not None:
				items['Price'] = Price
			else:
				items['Price'] = ""
			image_urls = sel.find_element_by_css_selector('div > a.Zhf2z- > div:nth-child(1) > div > div > img').get_attribute('src')
			items['image_urls'] = [urlparse.urljoin(response.url, image_urls)]
			yield items
		link_next = self.driver.find_element_by_css_selector('#container > div > div._3Q31_D > div._1XdvSH._17zsTh > div > div._2xw3j- > div > div:nth-child(3) > div._1JKxvj._31rYcN > ul + div > a').get_attribute('href')
		print "LINK_NEXT", link_next
		if link_next:
			yield scrapy.Request(response.urljoin(link_next), dont_filter=True)