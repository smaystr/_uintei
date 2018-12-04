# -*- coding: utf-8 -*-
import scrapy
# import collections
from scrapy.utils.markup import remove_tags


class UinteiparsSpider(scrapy.Spider):
    name = 'uinteipars'
    # allowed_domains = ['/home/smaystr/Documents/UINTEI/pdf_examples_split']
    start_urls = [
        'file:///home/smaystr/jupyter-projects/ml/_uintei/data/pdf_examples_split/KPI/30300/30300.html',
    ]

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ROBOTSTXT_OBEY': False,
    }


    @staticmethod
    def get_clss(clss):
        try:
            clss.pop(0)
            clss.pop(1)
            clss.pop(2)
            clss.pop(2)
            # line.sort(reverse=True)
        except IndexError:
            print("Index Out of Range")

        return clss

    def parse(self, response):
        selector = "//div[@id='page-container']//div[contains(@class, 't')]"

        review_cls = response.xpath(selector + "/@class").extract()
        review_cls = set([tuple(self.get_clss(cls.split())) for cls in review_cls])

        data_set = dict()

        for cls in review_cls:
            tag_filter = len(cls)

            mask = ["contains(@class, '{}') {} ".format(cls, 'and' if (tag_filter > 1) and (
            counter + 1 < tag_filter) else '') for counter, cls in enumerate(cls)]

            if not mask or tag_filter < 7:
                continue

            mask = "//div[ {}]".format("".join(map(str, mask)))

            review_content = response.xpath(mask).extract()

            review_content = [remove_tags(content) for content in review_content]
            review_content = "".join(map(str, review_content)).strip().replace("\r\n", "").replace("\t", "")

            key = " ".join(map(str, cls)).strip()
            data_set[key] = review_content

        print(data_set)

        # paragraph = collections.OrderedDict(sorted(paragraph.items(), key=len))
        # paragraph = sorted(paragraph.keys())
        # review_content = "//div[ contains(@class, 'm1') and contains(@class, 'h4')
        # and contains(@class, 'ff1') and contains(@class, 'fs1') and contains(@class, 'fc0')
        # and contains(@class, 'sc0') and contains(@class, 'ls0')  and contains(@class, 'ws0') ]"

        # yield {
            # **data_set
            # 'UDK': page.xpath('//*[@id="pf1"]/div[1]/div[4]/text()').extract(),
            # 'name': page.xpath('//*[@id="pf1"]/div[1]/div[6]/text()').extract(),
            # 'author': page.xpath('//*[@id="pf1"]/div[1]/div[8]/text()').extract(),
            # 'LINE': 'review_content',
            # 'LINE': (counter, page),
            # 'text': page.css('span.text::text').extract_first(),
            # 'author': page.css('small.author::text').extract_first(),
            # 'tags': page.css('div.text::text').extract(),
        # }
