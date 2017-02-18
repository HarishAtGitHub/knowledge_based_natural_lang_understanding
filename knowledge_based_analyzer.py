class KnowledgeBasedAnalyzer:
    def __init__(self):

        # stanford ner tagger
        from nltk.tag.stanford import StanfordNERTagger
        self.ner_stanford = StanfordNERTagger(
            '/home/harish/Documents/softwares/running/corenlp/stanford-corenlp-caseless-2015-04-20-models/edu/stanford/nlp/models/ner/english.all.3class.caseless.distsim.crf.ser.gz',
            '/home/harish/Documents/softwares/running/corenlp/stanford-corenlp-full-2015-04-20/stanford-corenlp-3.5.2.jar')

        # stanford pos tagger
        from nltk.tag.stanford import StanfordPOSTagger
        self.pos_stanford = StanfordPOSTagger(
            '/home/harish/Documents/softwares/running/corenlp/stanford-corenlp-caseless-2015-04-20-models/edu/stanford/nlp/models/pos-tagger/english-caseless-left3words-distsim.tagger',
            '/home/harish/Documents/softwares/running/corenlp/stanford-postagger-full-2015-04-20/stanford-postagger.jar')

        # spacy ner tagger
        import spacy
        self.ner_spacy = spacy.load('en')

        # wordnet lemmatizer
        from nltk.stem.wordnet import WordNetLemmatizer
        self.lemmatizer = WordNetLemmatizer()

        self.tagged_output = {}

    def analyze(self, text):
        self.lowercase(text)\
            .tokenize()\
            .tag_pos()\
            .lemmatize()\
            .tag_universal()
        self.tagged_output['INPUT_TEXT'] = self.text
        return self.tagged_output

    def lowercase(self, text):
        # to mimic text that comes out of voice to text conversion
        self.text = text.lower()
        return self

    def tokenize(self):
        from nltk import word_tokenize
        self.tokens = word_tokenize(self.text)
        return self

    def tag_pos(self):
        import nltk
        from nltk import word_tokenize

        #self.pos_tagged_tokens = nltk.pos_tag(word_tokenize(self.text), tagset='universal')
        self.pos_tagged_tokens = self.pos_stanford.tag(word_tokenize(self.text))
        return self
        #print(pos_tagged_tokens)


    def lemmatize(self):
        self.lemmatized_tokens = [self.lemmatizer.lemmatize(token[0], pos=self.__find_tag_letter(token[1])) for token in
                             self.pos_tagged_tokens]
        return self

    def __find_tag_letter(self, token):
        #ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v'
        JJ, RB, NN, VB = 'a', 'r', 'n', 'v' # did not find a match for ADJ_SAT
        # REFER: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        VBD = VBG = VBN = VBP = VBZ  = VB
        try:
            letter = eval(token)
        except NameError as ne:
            letter = 'n'  # default as per wordnet lemmatize function TODO: find some other way
        return letter

    def tag_universal(self):
        from tagger.custom_tagger import CustomTagger
        tagger = CustomTagger(tokens=self.lemmatized_tokens, stanford_ner=self.ner_stanford,
                              spacy_ner=self.ner_spacy,
                              unlemmatized_tokens=self.tokens)
        # TODO: FIXME as the verb and person names got mixed up
        # we need to check if verb is part of names so i need to do names first
        # Fix it later properly
        self.tagged_output['PERSON'] = tagger.tag_person(tokens=self.tokens)
        self.tagged_output['ACTION'] = tagger.tag_action()
        self.tagged_output['TYPE'] = tagger.tag_type()
        self.tagged_output['DATE'] = tagger.tag_date()
        self.tagged_output['SUBJECT'] = tagger.tag_subject()
        return self