import json


class FeedBack:
    def __init__(self, fb_json: str) -> None:
        self.relations = {}
        self.process_from_json(fb_json)

    def process_from_json(self, fb_json):
        rels = json.loads(fb_json)
        for fr, to, val in rels:
            self.relations[(fr, to)] = val
