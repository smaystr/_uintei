# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.utils.markup import remove_tags
from scrapy.selector import Selector


class UinteiscrapSpider(scrapy.Spider):

    name = 'uinteiscrap'

    selector = "//div[@id='page-container']//div[contains(@class, 't')]"

    # allowed_domains = ['/home/smaystr/Documents/UINTEI/pdf_examples_split']
    start_urls = [
        # 'file:///media/smaystr/disk/jupyter-projects/ml/_uintei/data/pdf_examples_split/KPI/r_2_4/r_2_4.html',
        # 'file:///media/smaystr/disk/jupyter-projects/ml/_uintei/data/pdf_examples_split/KPI/703-1408-1-PB/703-1408-1-PB.html',
        'file:///media/smaystr/disk/jupyter-projects/ml/_uintei/data/pdf_examples_split/KPI/30300/30300.html',
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
            clss.pop(1)
            clss.pop(1)
            clss.pop(1)
            clss.pop(2)
            clss.pop(2)
            clss.pop(2)
            clss.pop(2)
        except IndexError:
            # print("Index Out of Range")
            pass

        return clss

    @staticmethod
    def get_re_cleaned(review_content):

        review_content = "".join(map(str, review_content))

        # review_content = re.sub(r'(\<(/?[^>]+)>)', '', review_content)
        # review_content = re.sub(r'\W', ' ', review_content)
        # review_content = re.sub(r'(?=[\W])[^\.\:\;\!\?\=\?\+\-]', ' ', review_content)
        # review_content = re.sub(r'(?=[\W])[^\.\,\:\-\!\?]', ' ', review_content)

        # review_content = re.sub(r'^[?-?A-Z]', ' ', review_content)

        review_content = re.sub(r'(?:&).[\w\-_]{1,9}?(?:;)', '', review_content)  # &..;
        review_content = re.sub(r'[\u0370-\u03FF]', ' ', review_content)  # GR
        review_content = re.sub(r'[\u0080-\u00FF]', ' ', review_content)  # Latin-1
        review_content = re.sub(r'(?=[\W])[^\.\,\:\-\!\?]', ' ', review_content)

        review_content = review_content.replace("\n", "").replace("\r\n", "").replace("\t", "")
        review_content = review_content.strip()

        review_content = re.sub(r'$', ' ', review_content)
        review_content = re.sub(r'(?:\- )$', '', review_content)

        review_content = re.sub(r' +\.', '.', review_content)
        review_content = re.sub(r' +\,', ',', review_content)
        review_content = re.sub(r'\,\,', '', review_content)
        review_content = re.sub(r' +\...', '...', review_content)
        review_content = re.sub(r' +\!', '!', review_content)
        review_content = re.sub(r' +\?', '?', review_content)

        review_content = re.sub(r' +', ' ', review_content)

        return review_content

    def get_data_sets_score(self, response):
        review_cls = response.xpath(self.selector + "/@class").extract()
        review_cls = set([tuple(self.get_clss(cls.split())) for cls in review_cls])

        data_sets_score = dict()

        for cls in review_cls:
            tag_filter = len(cls)

            mask = ["contains(@class, '{}') {} ".format(cls, 'and' if (tag_filter > 1) and (
                counter + 1 < tag_filter) else '') for counter, cls in enumerate(cls)]

            if not mask or tag_filter < 2:
                continue

            mask = "//div[ {}]".format("".join(map(str, mask)))
            review_content = response.xpath(mask).extract()

            review_content = [remove_tags(content) for content in review_content]
            review_content = self.get_re_cleaned(review_content)

            # key = " ".join(map(str, cls)).strip()
            key = cls
            data_sets_score[key] = len(review_content)

        data_sets_sum = sum(data_sets_score.values())
        data_sets_score = {key: (value/data_sets_sum)*100 for key, value in data_sets_score.items()}
        data_sets_score = dict(set_score for set_score in sorted(
            data_sets_score.items(), key=lambda x: x[1], reverse=True))

        return data_sets_score

    def parse(self, response):
        sets_score = self.get_data_sets_score(response)
        sets_score = {key: value for key, value in sets_score.items() if value >= 0.1}

        for key, value in sets_score.items():
            print(' -- score --', key, value)

        # print('------------sum - score --------------->', sum(sets_score.values()))

        lines = response.xpath(self.selector).extract()

        paragraph = dict()
        paragraphs = list()
        val = len(lines)-1

        for counter, line in enumerate(lines):
            # print("++++++++++++++++++++++++++++++++++++++++++++", counter, val)
            line = remove_tags(line, keep=('div',))
            line = Selector(text=line).xpath("//div[text()[re:match(., '\w')]]")
            if not line:
                if counter == val:
                    paragraphs.append(paragraph.copy())
                continue
            clss = tuple(self.get_clss(line.xpath("//div/@class").extract()[0].split()))

            # line = remove_tags(line)
            line = remove_tags(line.extract()[0])
            line = self.get_re_cleaned(line)
            if not line or len(line) < 5:
                if counter == val:
                    paragraphs.append(paragraph.copy())
                continue

            if paragraph and list(paragraph.keys())[0] == clss:
                paragraph[clss] += line
                # print("------------------------", clss, line, counter, val)
            else:
                # print("=====================", clss, line, counter, val)
                if clss in sets_score.keys():
                    if paragraph:
                        paragraphs.append(paragraph.copy())
                        paragraph.clear()
                    paragraph[clss] = line
            if counter == val:
                paragraphs.append(paragraph.copy())

            # print("........................", clss, line, counter, val)

        paragraphs_len = len(paragraphs)-1
        for counter, value in enumerate(paragraphs):
            print(paragraphs_len, counter, (counter/paragraphs_len)*100, value)


            # yield {

            # 'UDK': page.xpath('//*[@id="pf1"]/div[1]/div[4]/text()').extract(),
            # 'name': page.xpath('//*[@id="pf1"]/div[1]/div[6]/text()').extract(),
            # 'author': page.xpath('//*[@id="pf1"]/div[1]/div[8]/text()').extract(),
            # 'LINE': pages_selector,
            # 'LINE': (counter, page),
            # 'text': page.css('span.text::text').extract_first(),
            # 'author': page.css('small.author::text').extract_first(),
            # 'tags': page.css('div.text::text').extract(),
            # }
