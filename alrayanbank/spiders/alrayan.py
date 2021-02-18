import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from alrayanbank.items import Article


class AlrayanSpider(scrapy.Spider):
    name = 'alrayan'
    start_urls = ['https://www.alrayanbank.co.uk/useful-info-tools/about-us/latest-news/']

    def parse(self, response):
        links = response.xpath('//ul[@class="event-ul-loop"]//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="page_next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()
        else:
            return
        date = response.xpath('//div[@class="event-date-timing"]//text()').get()

        if date and date.strip():
            date = datetime.strptime(date.strip(), '%d %B %Y')
            date = date.strftime('%Y/%m/%d')
        else:
            return

        content = response.xpath('//div[@class="column-1 contentP"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[4:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
