import json

from django.conf import settings
from django.core.urlresolvers import reverse

from haystack import indexes

from geonode.groups.models import Group

class GroupIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField()

    type = indexes.CharField(faceted=True)
    json = indexes.CharField(indexed=False)

    def get_model(self):
        return Group 

    def prepare_title(self, obj):
        return str(obj)

    def prepare_type(self, obj):
        return "group"

    def prepare_json(self, obj):
        data = {
            "_type": self.prepare_type(obj),

            "title": obj.title,
            "description": obj.description,
	    "keywords": [keyword.name for keyword in obj.keywords.all()] if obj.keywords else [],
            "thumb": obj.logo.url, 
            "detail": obj.get_absolute_url(),
        }

        return json.dumps(data)
                                         
