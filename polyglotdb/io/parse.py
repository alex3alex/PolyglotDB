


from .types.standardized import PGAnnotation, PGAnnotationType

from .discoursedata import DiscourseData

def parse_annotations(discourse_name, levels, hierarchy, make_transcription = True):
    annotation_types = {}
    segment_type = None
    for k, v in hierarchy.items():
        annotation_types[k] = PGAnnotationType(k)
        annotation_types[k].supertype = v
        if k == 'word':
            annotation_types[k].is_word = True # FIXME?
        if k not in hierarchy.values() and not annotation_types[k].is_word:
            segment_type = k

    for k in annotation_types.keys():
        relevent_levels = {}
        lengths = {}
        for inputlevel in levels:
            if inputlevel.ignored:
                continue
            if inputlevel.linguistic_type != k:
                continue
            speaker = inputlevel.speaker
            if speaker not in relevent_levels:
                relevent_levels[speaker] = []
            if speaker not in lengths:
                lengths[speaker] = None
            relevent_levels[speaker].append(inputlevel)
            if lengths[speaker] is None:
                lengths[speaker] = len(inputlevel)
            elif lengths[speaker] != len(inputlevel):
                raise(Exception('Annotations sharing a linguistic type and a speaker don\'t have a consistent length.'))
        for speaker, speaker_levels in relevent_levels.items():
            if len(speaker_levels) == 0:
                continue

            for i in range(len(speaker_levels[0])):
                type_properties = {}
                token_properties = {}
                label = None
                begin = None
                end = None
                for rl in speaker_levels:
                    if begin is None:
                        try:
                            begin = rl[i].begin
                        except AttributeError:
                            begin = rl[i].time
                    if end is None:
                        try:
                            end = rl[i].end
                        except AttributeError:
                            end = rl[i].time
                    if rl.name == k or rl.name == 'label':
                        if rl[i].value:
                            label = rl[i].value
                    elif rl.type_property:
                        type_properties[rl.name] = rl[i].value
                    else:
                        token_properties[rl.name] = rl[i].value

                a = PGAnnotation(label, begin, end)
                a.type_properties.update(type_properties)
                a.token_properties.update(token_properties)
                a.speaker = speaker
                if i != 0:
                    a.previous_id = annotation_types[k][-1].id
                annotation_types[k].add(a)

    for k, v in annotation_types.items():
        st = v.supertype
        if st is not None:
            for a in annotation_types[k]:
                super_annotation = annotation_types[st].lookup(a.midpoint, speaker = a.speaker)
                a.super_id = super_annotation.id
        if make_transcription and segment_type is not None and v.is_word:
            v.type_property_keys.update(['transcription'])
            for a in annotation_types[k]:
                transcription = annotation_types[segment_type].lookup_range(a.begin, a.end, speaker = a.speaker)
                a.type_properties['transcription'] = [x.label for x in transcription]
    return DiscourseData(discourse_name, annotation_types, hierarchy)
