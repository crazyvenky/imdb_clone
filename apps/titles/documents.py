from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from apps.titles.models import Title

@registry.register_document
class TitleDocument(Document):
    title = fields.TextField(attr='title')
    description = fields.TextField(attr='description')

    class Index:
        name = 'titles'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Title  
        fields = [
            'type',
            'release_date',
            'popularity',
            'poster_path',
            'backdrop_path',
        ]