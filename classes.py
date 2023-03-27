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

def limpeza(requisitos):
    tokens = []
    for indice,req in enumerate(requisitos):
        req= re.sub("[!'@*>=+#%:&;™.,_\\/()?\"]+", ' ', req)
        req= re.sub('[0-9]+', ' ', req)
        req= re.sub('- | -|-+', ' ', req)
        req= re.sub(r'(?:^| \\ )\w(?:$| )', ' ', req).strip()
        words = nltk.word_tokenize(req.lower())
        words = words[1:]
        tokens.append(words)
        newwords = []
        for word in words:
            if word in nltk.corpus.stopwords.words('english'):
                continue
            try:
                newwords.append(word)
            except:
                continue
        requisitos[indice] = ' '.join(newwords)
    return tokens,requisitos


class ambiguidade_lexica:
    def __init__(self, requisitos, palavras_amb,POS):
        self.requisitos=requisitos
        self.ambiguos_lexicos = {"PA": [], "AFL": []}
        self.palavras_amb=palavras_amb
        self.POS=POS
        self.tokens=[]
    
    def palavras_ambiguas(self):
        for indice,req in enumerate(self.requisitos):
            self.tokens.append(nltk.word_tokenize(req))
            for ambigua in self.palavras_amb:
                if ambigua.lower() in tokens:
                    self.ambiguos_lexicos["PA"].append(indice)

    def objetoWN(self,pos):
        
        if pos == 'V':
            return nltk.corpus.wordnet.VERB
        elif pos == 'N':
            return nltk.corpus.wordnet.NOUN
        elif pos == 'R':
            return nltk.corpus.wordnet.ADV
        elif pos == 'J':
            return nltk.corpus.wordnet.ADJ
        else:
            return nltk.corpus.wordnet.NOUN
    
    def algoritmo_flex_amb(self):
        LIMIAR_MIN = 3 / 4
        QTDE_SIM = 3
        for indice,req in enumerate(self.POS):
            qtde = len(self.tokens[indice])
            possiveis = []
            for token in req:
                if len(nltk.corpus.wordnet.synsets(token[0], pos=self.objetoWN(token[1][0]))) > QTDE_SIM:
                    possiveis.append(req[0])
            if len(possiveis) >= (LIMIAR_MIN * qtde):
                self.ambiguos_lexicos["AFL"].append(indice)
    
    def requisitos_ambiguos(self):
        self.palavras_ambiguas()
        self.algoritmo_flex_amb()
        return self.ambiguos_lexicos

class Ambiguidade_sintatica
    


arquivo = open('requisitos.txt','r')
texto = ''
for linhas in arquivo:
    texto+=linhas
arquivo.close()
requisitos = texto.split('\n')

arquivo = open('dicionario_base.txt','r')
texto = ''
for linhas in arquivo:
    texto+=linhas
arquivo.close()
palavras_ambiguas = texto.split('\n')



def trigram_pos(requisitos):
    from pickle import load
    entrada = open('trigram.pkl','rb')
    tagger = load(entrada)
    entrada.close()
    
    saida=[tagger.tag(requisito) for requisito in requisitos]
    
    return saida


tokens,requisitos=limpeza(requisitos)
pos = trigram_pos(tokens)

ambiguidadelexica = ambiguidade_lexica(requisitos,palavras_ambiguas,pos).requisitos_ambiguos()
print(ambiguidadelexica)
            
        