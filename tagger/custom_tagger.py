class CustomTagger:
    def __init__(self, tokens, stanford_ner, spacy_ner, unlemmatized_tokens):
        self.tokens = tokens
        self.stanford_ner = stanford_ner
        self.spacy_ner = spacy_ner
        self.unlemmatized_tokens = unlemmatized_tokens

    def tag_person(self, tokens = None):
        # fix to have persons at different locations
        ner_tagged_tokens = self.stanford_ner.tag(tokens if tokens else self.tokens)
        persons = list()
        start = False
        for token in ner_tagged_tokens:
            if (token[1] == 'PERSON'):
                if persons:
                    if start:
                        persons[len(persons) - 1] = persons[len(persons) - 1] + ' ' + token[0]
                    else:
                        start = True
                        persons.append(token[0])
                else:
                    start = True
                    persons.append(token[0])
            else:
                start = False
        self.persons = persons # for it to be used in other places
        return persons

    def tag_subject(self, tokens = None):
        # fix to have persons at different locations
        #ner_tagged_tokens = self.stanford_ner.tag(tokens if tokens else self.tokens)
        import nltk
        pos_lemmatized_tagged_tokens = nltk.pos_tag(tokens if tokens else self.tokens, tagset='universal')
        nouns = list()
        start = False
        for token in pos_lemmatized_tagged_tokens:
            if (token[1] == 'NOUN' or token[1] == 'ADJ' or token[1] == 'NUM'):
                if nouns:
                    if start:
                        nouns[len(nouns) - 1] = nouns[len(nouns) - 1] + ' ' + token[0]
                        if self.is_in_dates(nouns[len(nouns) - 1]):
                            nouns.pop()
                    else:
                        start = True
                        nouns.append(token[0])
                else:
                    start = True
                    nouns.append(token[0])
            else:
                start = False
        self.nouns = nouns # for it to be used in other places
        return nouns

    def tag_date(self, tokens = None):
        doc = self.spacy_ner(' '.join(tokens if tokens else self.tokens))
        dates = []
        for ent in doc.ents:
            # print(ent.label_, ent.text)
            if (ent.label_ == 'DATE'):
                dates.append(ent.text)
        self.dates = dates
        return dates

    def tag_action(self, tokens = None):
        import nltk
        pos_lemmatized_tagged_tokens = nltk.pos_tag(tokens if tokens else self.tokens, tagset='universal')
        #print(pos_lemmatized_tagged_tokens)
        #pos_lemmatized_tagged_tokens = tokens if tokens else self.tokens
        #print(pos_lemmatized_tagged_tokens)
        verbs = list()
        start = False
        verb_tags = ['VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VB']
        for token in pos_lemmatized_tagged_tokens:
            if (token[1] == 'VERB' and token[0] != 'be' and
                    not self.is_in_names(token[0])):
                if verbs:
                    if start:
                        verbs[len(verbs) - 1] = verbs[len(verbs) - 1] + ' ' + token[0]
                    else:
                        start = True
                        verbs.append(token[0])
                else:
                    start = True
                    verbs.append(token[0])

            else:
                start = False
        return verbs

    def is_in_names(self, segment):
        # used because some names were misunderstood as verbs like sylvester in douglas sylvester(not sure why)
        for person in self.persons:
            if segment in person.split(' '):
                return True

    def is_in_dates(self, segment):
        # used because some names were misunderstood as verbs like sylvester in douglas sylvester(not sure why)
        return segment in self.dates

    def tag_type(self, tokens = None):
        supported_question_types = ['what', 'who', 'when', 'how many', 'how much']
        tokens = tokens if tokens else self.tokens
        if tokens[0] in supported_question_types:
            return [tokens[0]]
        elif tokens[0] + ' ' + tokens[1] in supported_question_types:
            return [tokens[0] + ' ' + tokens[1]]
        else:
            return ['other']



