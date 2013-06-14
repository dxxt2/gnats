# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from datetime import datetime

from spiders.mongodb import issues


class MongoPipeline(object):
    def add_to_collection(self, col, item):
        number = item['number']
        issue = col.find_one({'number': number})
        if not issue:
            if item['reported_in'].find('0z0') < 0 or item['state'] != 'closed':
                # ignore screenos issues or closed issues
                col.insert(item)
        elif issue['modified_at'] != item['modified_at']:
            history_item = {
                'responsible': issue['responsible'],
                'state': issue['state'],
                'dev_owner': issue['dev_owner'],
                'modified_at': issue['modified_at']
            }
            history = issue.get('history', [])
            history.append(history_item)
            item['history'] = history
            item['crawled'] = True
            col.update({'number': number}, item)
        else:
            col.update({'number': number}, {'$set': {'crawled': True}})

    def process_item(self, item, spider):
        issue = dict(item)
        self.add_to_collection(issues, issue)
        return item
