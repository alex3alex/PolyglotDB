
import os

from .base import BaseParser,  DiscourseData

from ..helper import text_to_lines

class OrthographyTextParser(BaseParser):
    def __init__(self, annotation_types,
                    stop_check = None, call_back = None):
        self.annotation_types = annotation_types
        self.hierarchy = {'word': None}
        self.make_transcription = False
        self.make_label = False
        self.stop_check = stop_check
        self.call_back = call_back

    def parse_discourse(self, path):

        name = os.path.splitext(os.path.split(path)[1])[0]

        for a in self.annotation_types:
            a.reset()


        lines = text_to_lines(path)
        if self.call_back is not None:
            self.call_back('Processing file...')
            self.call_back(0, len(lines))
            cur = 0
        num_annotations = 0
        for line in lines:
            if self.stop_check is not None and self.stop_check():
                return
            if self.call_back is not None:
                self.call_back(num_annotations)
            if not line or line == '\n':
                continue

            to_add = []
            for word in line:
                spell = word.strip()
                spell = ''.join(x for x in spell if not x in self.annotation_types[0].ignored_characters)
                if spell == '':
                    continue
                to_add.append(spell)
            self.annotation_types[0].add((x, num_annotations + i) for i, x in enumerate(to_add))
            num_annotations += len(to_add)

        pg_annotations = self._parse_annotations()

        data = DiscourseData(name, pg_annotations, self.hierarchy)
        for a in self.annotation_types:
            a.reset()
        return data
