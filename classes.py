import nltk
import re

class AnaliseSintatica:
    def __init__(self, requisitos, tagger,passive_voice):
        self.tagger=tagger
        self.chunker=nltk.RegexpParser("""
                      AdvP: {<QL>?<AB.*>?<RB.*>+}                         #Para extrair Adverbial Phrases
                      AP: {<AB.*>?<AdvP>?<QL>?<JJ.*>+}                    #Para extrair Adjective Phrases
                      NP: {<PP.*>?<CS>?<DT>?<AT>?<AP>?<NN.*>+|<PPS.*>}    #Para extrair Noun Phrases
                      P: {<IN.*>|<TO>}                                    #Para extrair preposições
                      PP: {<P>+<NP>?}                                     #Para extrair Preposition Phrases
                      MOD: {<MD>}                                         #Para extrair Modal Auxiliare
                      V: {<VB.*>|<BE.*>|<DO.*>|<HV.*>}                    #Para extrair os verbos
                      VP: {<MOD>?<V>+<NP>*<PP>*<AP>*<AdvP>*}              #Para extrair Verb Phrases
                      CCPP: {<P><CC><P>}                                  #Para extrair Coordination Preposition Phases
                      CCNP: {<NP><CC><NP>}                                #Para extrair Coordination Noun Phrases
                      CCAP: {<AP><CC><AP>}                                #Para extrair Coordination Adjective Phrases
                      """)
        self.passive_voice=passive_voice
        self.analise_sintatica={'PV': [],'MS':[],'MVM': [],'DS':[]}
        self.requisitos=requisitos
    
    def obter_nos(self,arvore):
        largura=len(arvore)
        nodes=[]
        for i in range(largura):
            if type(arvore[i]) is nltk.Tree:
                nodes.append(arvore[i].label())
            else:
                nodes.append(arvore[i][1])
        return nodes
    
    def sequencia_tags(self,tags):
        retorno = ""
        for tag in tags:
            retorno+=tag[1]
        return retorno
    
    def voz_passiva(self,tags,passivevoice):
        for padrao in passivevoice:
            if padrao in tags:
                return True
        return False
    def obter_sujeito(self,arvore):
        largura=len(arvore)
        for i in range(largura):
            if type(arvore[i]) is nltk.Tree:
                if(arvore[i].label()=='NP'):
                    retorno=[]
                    for word in arvore[i]:
                        retorno.append(word[0])
                    return ' '.join(retorno)
            else:
                if(arvore[i][1]=='NP'):
                    return(arvore[i][0])
    
    def arvore_sintatica(self,sentences,passivevoice):
        for sentence in sentences:
            if len(sentence)==0:
                return "OK"
            tagged_sentence = self.tagger.tag(nltk.word_tokenize(sentence))
            sintaxe_tree = self.chunker.parse(tagged_sentence)
            nodes = self.obter_nos(sintaxe_tree)
            if not ('VP' or 'V' or 'MOD') in nodes:
                return("MVM")
            sequencia = self.sequencia_tags(sintaxe_tree.leaves())
            if(self.voz_passiva(sequencia,passivevoice)):
                return("PV")
            if not ('NP' in nodes[0:nodes.index('VP')] or 'CCNP' in nodes[0:nodes.index('VP')]):
                return("MS")
            else:
                subject = self.obter_sujeito(sintaxe_tree).lower()
                if ('it' in subject or 'there' in subject):
                    return("DS")
            return "OK"
    def analise_completa(self):
        for indice,req in enumerate(self.requisitos):
            req = req.split(':')[1]
            req=re.sub("[! - &;™,]+",' ',req)
            sentences = req.split('.')
            erro = self.arvore_sintatica(sentences,self.passive_voice)
            if erro!="OK":
                self.analise_sintatica[erro].append(indice)

    def analise(self):
        print("Cheguei")
        self.analise_completa()
        return self.analise_sintatica