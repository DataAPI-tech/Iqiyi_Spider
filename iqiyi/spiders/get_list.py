# -*- coding: utf-8 -*-
import scrapy
import logging
import json
import pymongo


class GetListSpider(scrapy.Spider):
    name = 'get_list'
    allowed_domains = ['iqiyi.com']
    start_urls = ['http://iqiyi.com/']
    myclient = pymongo.MongoClient("mongodb://106.14.104.171:27017/")
    mydb = myclient["spider_iqiyi"]

    def start_requests(self):
        for year in range(2019, 2020):
            url = 'http://search.video.iqiyi.com/o?&mode=11&ctgName=' + '电视剧' + \
                '&pageSize=2000&type=list&if=html5&pos=1&site=iqiyi&market_release_date_level=' + \
                str(year) + '&callback=json'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """获取列表"""
        logging.info('pageURL: ' + response.url)
        content = response.body.decode('utf8').replace(
            r'try{json(', '').replace(r')}catch(e){}', '')
        data_list = json.loads(content)['docinfos']
        mycol = self.mydb["index"]
        for data in data_list:
            data = data['albumDocInfo']
            data['_id'] = data['qipu_id']
            mycol.update_one({"_id": data['qipu_id']}, {"$set": data}, upsert=True)

            tvId = data.get('qipu_id')
            ftvid = data.get('videoinfos')[0].get('tvId')
            hot_data_url = 'https://pub.m.iqiyi.com/jp/h5/count/hotTrend/?videoId=' + \
                str(ftvid)+'&albumId='+str(tvId)
            yield scrapy.Request(hot_data_url, callback=self.get_hot_data, meta={'剧集ID': tvId})

    def get_hot_data(self, response):
        logging.info('hotURL: ' + response.url)
        content = response.body.decode('utf8').replace(r'var tvInfoJs=', '')
        data = json.loads(content)['data']
        data['_id'] = data['qipuId']
        mycol = self.mydb["data"]
        # mycol.insert_one(data)
        mycol.update_one({"_id": data['qipuId']}, {"$set": data}, upsert=True)
