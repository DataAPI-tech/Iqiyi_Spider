# -*- coding: utf-8 -*-
import scrapy
import logging
import json


class GetListSpider(scrapy.Spider):
    name = 'get_list'
    allowed_domains = ['iqiyi.com']
    start_urls = ['http://iqiyi.com/']

    def start_requests(self):
        for year in range(2010, 2025):
            url = 'http://search.video.iqiyi.com/o?&mode=11&ctgName=' + '电视剧' + \
                '&pageSize=2000&type=list&if=html5&pos=1&site=iqiyi&market_release_date_level=' + \
                str(year) + '&callback=json'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """获取列表"""
        logging.info('pageURL: ' + response.url)
        item = {}
        content = response.body.decode('utf8').replace(
            r'try{json(', '').replace(r')}catch(e){}', '')
        data_list = json.loads(content)['docinfos']
        for data in data_list:
            item['剧集ID'] = data.get('albumDocInfo').get('qipu_id')
            item['剧集名称'] = data.get('albumDocInfo').get('albumTitle')
            item['导演'] = data.get('albumDocInfo').get('director')
            item['主演'] = data.get('albumDocInfo').get('star')
            item['地域'] = data.get('albumDocInfo').get('region')
            item['开播时间'] = data.get('albumDocInfo').get('releaseDate')
            item['总集数'] = data.get('albumDocInfo').get('itemTotalNumber')
            item['平台'] = data.get('albumDocInfo').get('siteName')
            item['是否付费'] = data.get('albumDocInfo').get('isPurchase')
            item['评分'] = data.get('albumDocInfo').get('score')
            item['播出方式'] = data.get('albumDocInfo').get('stragyTime')
            item['是否独家'] = data.get('albumDocInfo').get('is_exclusive')
            if data.get('albumDocInfo').get('video_lib_meta').get('category') is not None:
                item['主题'] = '/'.join(data.get('albumDocInfo').get('video_lib_meta').get('category'))
            item['豆瓣ID'] = data.get('albumDocInfo').get('video_lib_meta').get('douban_id')
            item['是否爱奇艺出品'] = data.get('albumDocInfo').get('video_lib_meta').get('is_qiyi_produced')
            item['首集ID'] = data.get('albumDocInfo').get('videoinfos')[0].get('tvId')
            logging.info(item)
            # yield item
            hot_data_url = 'https://pub.m.iqiyi.com/jp/h5/count/hotTrend/?videoId='+str(item['首集ID'])+'&albumId='+str(item['剧集ID'])
            yield scrapy.Request(hot_data_url, callback=self.get_hot_data, meta={'剧集ID':item['剧集ID']})
            
    def get_hot_data(self, response):
        item = {}
        item['剧集ID'] = response.meta['剧集ID']
        logging.info('hotURL: ' + response.url)
        content = response.body.decode('utf8').replace(r'var tvInfoJs=', '')
        data_list = json.loads(content)['data'].get('allHotIndex')
        for i in data_list:
            item['日期'] = i.get('date').replace('.','')
            item['热度'] = i.get('count')
            print('jjej')
            yield item
