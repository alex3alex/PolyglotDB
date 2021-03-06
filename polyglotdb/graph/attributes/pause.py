
from polyglotdb.graph.attributes.base import AnnotationAttribute, Attribute, key_for_cypher

from polyglotdb.graph.attributes.path import PathAnnotation, PathAttribute

class PauseAnnotation(AnnotationAttribute):
    def __init__(self, pos = 0, corpus = None, hierarchy = None):
        self.type = 'pause'
        self.pos = pos
        self.corpus = corpus
        self.hierarchy = hierarchy
        self.subset_token_labels = []
        self.subset_type_labels = []

    @property
    def define_alias(self):
        """ concatenates type, corpus, and alias

        Returns
        -------
        str
            concatenated string"""
        label_string = ':{}'.format(self.type)
        if self.corpus is not None:
            label_string += ':{}'.format(key_for_cypher(self.corpus))
        return '{}{}'.format(self.alias, label_string)

    def __getattr__(self, key):
        if key in ['previous', 'following']:
            if key == 'previous':
                pos = self.pos - 1
            else:
                pos = self.pos + 1
            return PausePathAnnotation(self.type, pos, corpus = self.corpus, hierarchy = self.hierarchy)
        elif key == 'speaker':
            from .speaker import SpeakerAnnotation
            return SpeakerAnnotation(self, corpus = self.corpus)
        elif key == 'discourse':
            from .discourse import DiscourseAnnotation
            return DiscourseAnnotation(self, corpus = self.corpus)
        return PauseAttribute(self, key, False)

    @property
    def key(self):
        """Returns 'pause' """
        return 'pause'

class PauseAttribute(Attribute):
    pass

class PausePathAnnotation(PathAnnotation):
    def additional_where(self):
        """
        Returns
        -------
        str or None
            cypher string if key is 'pause', None otherwise"""
        if self.key == 'pause':
            return 'NONE (x in nodes({})[1..-1] where x:speech)'.format(self.path_alias)
        return None

    def __getattr__(self, key):
        if key == 'annotation':
            raise(AttributeError('Annotations cannot have annotations.'))
        return PausePathAttribute(self, key, False)

class PausePathAttribute(PathAttribute):
    duration_return_template = 'extract(n in {alias}[-1..]| n.end)[0] - extract(n in {alias}[0..1]| n.begin)[0]'

    @property
    def with_alias(self):
        """ Returns annotation's path_type_alias"""
        return self.annotation.path_type_alias
