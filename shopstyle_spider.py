# -*- coding: utf-8 -*-nam
import scrapy
import json
import logging
import datetime
from shopstyle.items import ShopstyleItem

class ShopstyleSpiderSpider(scrapy.Spider):
	name = "shopstyle_spider"
	allowed_domains = ["shopstyle.com"]
	start_urls = ['http://www.shopstyle.com/api/v2/products?cat=womens-accessories&locales=all&pid=shopstyle&limit=40&offset=0',
				]

	def parse(self, response):
		
		main_data = json.loads((response.body).decode("utf-8"))

		##metadata
		metadata = main_data['metadata']
		offset = metadata['offset']
		limit = metadata['limit']
		total = metadata['total']

		if (offset + limit > total):
			return
		else:
			offset = offset + limit
			base_url = response.url[:response.url.rfind("=")+1]
			new_url = base_url + str(offset)
			logging.info(offset)
			yield scrapy.Request(new_url, callback=self.parse) 


		product_data = main_data['products']


		for product in product_data:
			item = ShopstyleItem()

			item['itemNum'] = 'shopstyle_' + str(product['id'])

			##get url

			#vast majority of cases in this
			if ('directUrl' in product.keys()):
				item['url'] = product['directUrl']
			else:
				logging.warning("skipped one")

			item['itemName'] = product['name']
			
			#color
			color = product['colors']
			if (color):
				color = color[0]['canonicalColors']
				if (color):
					item['color'] = color[0]['name']

			##images
			images = [product['image']['sizes']['Best']['url']]


			for image in product['alternateImages']:
				images.append(image['sizes']['Best']['url'])

			item['images'] = images

			##priceData

			if ('salePriceLabel' in product.keys()):
				item['hasSale'] = True
				item['regular_price'] = product['priceLabel']
				item['price'] = product['salePriceLabel']
			else:
				item['hasSale'] = False
				item['price'] = product['priceLabel']

			##category

			item['category'] = product['categories'][0]['name']

			item['seller'] = 'Shopstyle_' + product['retailer']['name']

			item['desc'] = product['description']

			item['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

			yield item







