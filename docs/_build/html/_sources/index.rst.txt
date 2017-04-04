.. Request Validator documentation master file, created by
   sphinx-quickstart on Tue Apr  4 15:20:38 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Request Validator's documentation!
=============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Github
======

https://github.com/amirasaran/request_validator

request\_validator
==================

Python Request(json) Validator

how to install
==============

::

    pip install request_validator

How to use
==========

| Imaging you have a json response that get from rest api server and you
| must validate response.

**sample:**

::

    from request_validator.serializers import *
    from request_validator.fields import *


    class GlossDefSerializer(BaseSerializer):
        para = CharField()
        gloss_see_also = CharField(many=True, source="GlossSeeAlso")


    class GlossEntrySerializer(BaseSerializer):
        id = IntField(source="ID")
        sort_as = CharField(source="SortAs")
        gloss_term = CharField(source="GlossTerm")
        acronym = CharField(source="Acronym")
        abbrev = CharField(source="Abbrev", required=True, allow_blank=False)
        gloss_def = GlossDefSerializer(source="GlossDef")
        gloss_see = CharField(source="GlossSee")


    class GlossListSerializer(BaseSerializer):
        gloss_entry = GlossEntrySerializer(source="GlossEntry")


    class GlossDivSerializer(BaseSerializer):
        title = CharField()
        gloss_list = GlossListSerializer(source="GlossList")


    class GlossarySerializer(BaseSerializer):
        title = CharField()
        gloss_div = GlossDivSerializer(source="GlossDiv")


    class SampleSerializer(BaseSerializer):
        glossary = GlossarySerializer()


    sample_data = {
        "glossary": {
            "title": "example glossary",
            "GlossDiv": {
                "title": "S",
                "GlossList": {
                    "GlossEntry": {
                        "ID": 12,
                        "SortAs": "SGML",
                        "GlossTerm": "Standard Generalized Markup Language",
                        "Acronym": "SGML",
                        "Abbrev": "",
                        "GlossDef": {
                            "para": "A meta-markup language, used to create markup languages such as DocBook.",
                            "GlossSeeAlso": ["GML", "XML"]
                        },
                        "GlossSee": "markup"
                    }
                }
            }
        }
    }


    validator = SampleSerializer(data=sample_data)
    print('validation status:')
    print(validator.is_valid())
    print("\nvalidation errors:")
    print(validator.get_errors())
    print("\nvalidated data:")
    print(validator.validate_data())

**The above sample output:**

::

    validation status:
    False

    validation errors:
    {'glossary': {'gloss_div': {'gloss_list': {'gloss_entry': {'abbrev': ['This field cannot be blank']}}}}}

    validated data:
    {'glossary': {'title': 'example glossary', 'gloss_div': {'title': 'S', 'gloss_list': {'gloss_entry': {'acronym': 'SGML', 'gloss_term': 'Standard Generalized Markup Language', 'gloss_def': {'gloss_see_also': ['GML', 'XML'], 'para': 'A meta-markup language, used to create markup languages such as DocBook.'}, 'gloss_see': 'markup', 'sort_as': 'SGML', 'id': 12}}}}}