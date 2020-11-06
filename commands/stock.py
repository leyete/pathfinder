# Copyright (C) 2020 Lagg Squad Dev Team.
# This source code is released under a GPL-3.0 license.

"""
Stock command.
"""

import logging
import queue
import scrapy
import scrapy.crawler
import scrapy.http
import telegram
import telegram.ext

from .command import CommandHandler
from collections import namedtuple
from typing import Dict, List

from crochet import setup, wait_for
setup()

# Namedtuple to store the scraping results.
Result = namedtuple('Result', ['name', 'price', 'stock', 'href'])


class PccomponentesSpider(scrapy.Spider):
    """
    Spider class for the pccomponentes.com website.

    Parameters:
        product (:obj:`str`): Product-id string.
        result_queue (:obj:`queue.Queue`): Queue to place scraping results.
        Additional parameters will be forwarded to the Spider base class.

    Attributes:
        site_url (:obj:`str`): Base site URL.
        product (:obj:`str`): Product-id of the product to look for.
        product_parameters (:obj:`dict`): Dictionary that maps a product-id
            with the corresponding URL parameters.
        result_queue (:obj:`queue.Queue`): Queue to place scraping results.
    """
    name: str = 'pccomponentes'
    site_url: str = 'https://www.pccomponentes.com'

    # Product parameters. This dictionary maps a product-id with the corresponding
    # URL parameters to be included in the Ajax request.
    product_parameters: Dict[str, Dict[str, str]] = {
        'rtx-3080': {                 # Geforce RTX 3080 series
            'idFilters[]': '7498',
            'idFamilies[]': '6',
        },
        'ryzen9': {
            'idFilters[]': '7678',
            'idFamilies[]': '4',
        },
    }

    def __init__(self, product: str, result_queue: queue.Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product  # TODO: make sure the product_id is available.
        self.result_queue = result_queue

    def generate_url(self, extra: Dict[str, str] = {}) -> str:
        """
        Generates a URL with the product parameters.

        Parameters:
            extra (:obj:`dict`): Extra parameters that will be used to update the `product_parameters`
            dictionary before building the URL.

        Returns:
            The generated URL.
        """
        parameters = self.product_parameters[self.product]
        parameters.update(extra)
        return f'{self.site_url}/listado/ajax?{"&".join([f"{k}={v}" for k, v in parameters.items()])}'

    def start_requests(self) -> List[scrapy.Request]:
        """
        Generate the starting requests for this Spider.

        Returns:
            A list with the starting Request.
        """
        return [scrapy.Request(url=self.generate_url({'page': '0'}), callback=self.parse)]

    def parse(self, response: scrapy.http.Response) -> List[scrapy.Request]:
        """
        Process the downloaded data and adds the scraped data to the result queue.

        Parameters:
            response (:obj:`scrapy.http.Response`): The response to parse.

        Returns:
            A list with the Requests to follow. These will include the required
            requests to parse all available product pages.
        """
        items = response.xpath('//article[@class="c-product-card"]')
        for item in items:
            data_id = item.xpath("@data-id").get()  # used to get the href tag.
            data_name = item.xpath("@data-name").get()
            data_price = item.xpath("@data-price").get()
            data_stock_web = item.xpath("@data-stock-web").get()
            href = f'{self.site_url}%s' % item.xpath(f'//a[@data-id="{data_id}"]/@href').get()
            # add the scraped data to the result queue.
            self.result_queue.put(Result(data_name, data_price, data_stock_web, href))

        # if there are more pages to check, return the list of appropriate Responses.
        if response.headers.get('currentpage') == b'0' and (totalpages := int(response.headers.get('totalpages'))) > 1:
            return [
                scrapy.Request(url=self.generate_url({'page': str(i)}), callback=self.parse) for i in range(1, totalpages)
            ]


class StockCommand(CommandHandler):
    """
    Look for stock of various PC components (currently only RTX 3080).
    """
    command: str = 'stock'

    @wait_for(10)
    def run_spider(self, spider, *args, **kwargs):
        """
        Run the Spider from Crochet, this will solve the problem of twister's
        reactor complaining about restarting issues when the Lambda environment
        is preserved between consecutive calls.
        """
        crawler = scrapy.crawler.CrawlerRunner({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        })
        d = crawler.crawl(spider, *args, **kwargs)
        return d

    def callback(self, update: telegram.Update, context: telegram.ext.CallbackContext) -> None:
        """Look for stock and show results."""
        # get the product_id from the command arguments.
        if len(context.args) == 0:
            update.message.reply_text('You need to specify me a product_id!')
            return

        product_id = context.args[0]
        update.message.reply_text(f'Hold on. Let me scout the web for "{product_id}" :)')

        # instantiate and run the crawlers.
        for spider in [PccomponentesSpider]:
            results = queue.Queue()
            self.run_spider(spider, product_id, results)
            # filter non-available items.
            stock = []
            try:
                for product in iter(lambda: results.get(block=False), None):
                    if product.stock in ['1', '2', '3']:  # not so sure about the value '3'.
                        stock.append(product)
            except queue.Empty:
                pass

            if stock:
                message = 'Here is the stock that I\'ve found!\n'
                for product in stock:
                    message += f'\nProduct: {product.name}\nPrice: {product.price}\nLink: {product.href}\n'

            else:
                message = 'No stock available right now :('

            context.dispatcher.bot.send_message(update.message.chat_id, message)
