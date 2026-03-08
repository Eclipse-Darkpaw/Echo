import spacy

class SemanticSimilarityChecker:
    def __init__(self, english_model='en_core_web_md', multi_model='xx_sent_ud_sm'):
        self.nlp_en = spacy.load(english_model)
        """Natural Language Processing English"""
        self.nlp_multi = spacy.load(multi_model)
        """Natural Language Processing Multi""" 

    def find_similar(self,
        input_str: str,
        compare_str_list: list[str],
        threshold_en=0.75,
        threshold_multi=0.7
    ) -> set[str]:
        """
        Returns a list of the found similar strings.
        A string is considered similar when either one of the
        nlps report higher than the set threshold.
        """
        doc_new_en = self.nlp_en(input_str)
        doc_new_multi = self.nlp_multi(input_str)

        similar = set()

        for compare_str in compare_str_list:
            score_en = doc_new_en.similarity(self.nlp_en(compare_str))
            if score_en > threshold_en:
                similar.add(compare_str)
            else: # Avoid running nlp_multi if already added to similar
                score_multi = doc_new_multi.similarity(self.nlp_multi(compare_str))
                if score_multi > threshold_multi:
                    similar.add(compare_str)
        
        return similar