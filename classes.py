import nltk
import re

#Funções de uso geral
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

def trigram_pos(requisitos):
    from pickle import load
    entrada = open('trigram.pkl','rb')
    tagger = load(entrada)
    entrada.close()
    
    saida=[tagger.tag(requisito) for requisito in requisitos]
    
    return saida

###################################################################################


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


class Contextualizacao:
    def __init__(self, requisitos,nome_arquivo_ontologia):
        self.requisitos=requisitos
        self.arquivo=nome_arquivo_ontologia
        self.dicionario_palavras_smart={}
        self.contextualizados = {"Contextualizados":[], "SensoresIncompletos":[],"AtuadoresIncompletos":[]}
        self.sensores=[]
    def tratamento_ontologia(self):
        arquivo = open(self.arquivo,'r')
        arq = ''
        for i in arquivo:
            arq+=i
        arquivo.close()
        palavras_smart=arq.split('\n')

        for palavra in palavras_smart:
            chave,valor=palavra.split(',')
            self.dicionario_palavras_smart[chave]=int(valor)
    def sensores(self):
        arquivo = open("sensores.txt",'r')
        arq = ''
        for i in arquivo:
            arq+=i
        arquivo.close()
        self.sensores=arq.split('\n')
    def OR(self,array1,array2):
        aux=[]
        for i in range(len(array1)):
            aux.append(array1[i] or array2[i])
        return aux 

    def contextualizacao(self):
        from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
        import pandas as pd
        import numpy as np
        from sklearn.cluster import KMeans
        requisitos=limpeza(self.requisitos)[1]
        self.tratamento_ontologia()
        tfidfvectorizer = TfidfVectorizer(analyzer='word', stop_words='english')

        tfidf_wm = tfidfvectorizer.fit_transform(requisitos)
        tfidf_tokens = tfidfvectorizer.get_feature_names_out()
        palavras = list(tfidfvectorizer.get_feature_names_out())
        df_tfidfvect = pd.DataFrame(data=tfidf_wm.toarray(), columns=palavras)

        n = 2
        kmeans = KMeans(n_clusters=n, random_state=0,n_init=10)

        df = df_tfidfvect
        kmeans.fit(df)
        palavras_smart=list(self.dicionario_palavras_smart.keys())
        labels = kmeans.labels_

        classe_0 = [not bool(x) for x in labels]
        classe_1 = [bool(x) for x in labels]

        classe_0 = df[classe_0]
        classe_1 = df[classe_1]

        
        
        indices_0 = list(classe_0.mean() == 0)
        indices_0 = list(classe_0.mean()[indices_0].index)
        indices_1 = list(classe_1.mean() == 0)
        indices_1 = list(classe_1.mean()[indices_1].index)

        classe_1 = classe_1.drop(columns=indices_1)
        classe_0 = classe_0.drop(columns=indices_0)

        palavras_0 = list(classe_0.columns)
        palavras_1 = list(classe_1.columns)
        
        palavras_check_0 = []
        for i in range(len(palavras_0)):
            for palavra in palavras_smart:
                if palavras_0[i] in palavra:
                    if palavras_0[i] not in palavras_check_0:
                        palavras_check_0.append(palavras_0[i])
        palavras_check_1 = []
        for i in range(len(palavras_1)):
            for palavra in palavras_smart:
                if palavras_1[i] in palavra:
                    if palavras_1[i] not in palavras_check_1:
                        palavras_check_1.append(palavras_1[i])
        
        media_0 = classe_0.mean()[palavras_check_0]
        media_1 = classe_1.mean()[palavras_check_1]
        

        
        score_0 = media_0.sum()
        score_1 = media_1.sum()

        
        if score_0 > score_1:
            classe=0
            qtde_palavras=len(palavras_0)
        else:
            classe=1
            qtde_palavras = len(palavras_1)

        if classe==1:
            pass
        else:
            aux=[]
            '''print('labels sem mexer: ',list(labels))'''
            for i in list(labels):
                if i==0:
                    i=1
                elif i==1:
                    i=0
                aux.append(i)
            labels=aux
        
        vetor=[0 for i in range(len(palavras))]
        for chave,valor in self.dicionario_palavras_smart.items():
            if len(chave.split(' '))==1:
                if chave in palavras:
                    indice=palavras.index(chave)
                    vetor[indice]=valor
            else:
                aux=0
                for mini_chave in chave.split(' '):
                    if mini_chave in palavras:
                        aux+=1
                if aux==len(chave.split(' ')):
                    for mini_chave in chave.split(' '):
                        indice=palavras.index(mini_chave)
                        vetor[indice]=valor
        df_pesos=pd.DataFrame(vetor,index=palavras)
        vetor_pesos=np.array(vetor)

        array_score=[]
        for indice in range(len(self.requisitos)):
            linha=df_tfidfvect.iloc[indice]
            array_linha=np.array(linha)
            array_score.append(np.dot(vetor_pesos,array_linha))
        media_score=sum(array_score)/len(array_score)

        resultado=[]
        for i in array_score:
            if i>=media_score:
                resultado.append(1)
            else:
                resultado.append(0)
        

        array_or=self.OR(labels,resultado)
        self.contextualizados["Contextualizados"]=[indice for indice,valor in enumerate(array_or) if valor==1]
    
    def completude(self):
        tokens, requisitos=limpeza(self.requisitos)
        pos = trigram_pos(requisitos)
        
        
        for indice in self.contextualizados["Contextualizados"]:
            palavras=tokens[indice]
            
            for i,palavra in enumerate(palavras):
                # 1 - Sensor sem definição do sensor
                if(palavra=="sensor" or palavra=="sensors"):
                    if not ((palavras[i - 1] in self.sensores)):
                        if indice not in self.contextualizados["SensoresIncompletos"]:
                            self.contextualizados["SensoresIncompletos"].append(indice)

                        
                        
                # 2 - Atuadores sem definição
                if (palavra == "actuator" or palavra == "actuators"):
                    if not ((pos[indice][i+1][1]=='RB') or (pos[indice][i+1][1][0]=='V')):
                        if indice not in self.contextualizados["AtuadoresIncompletos"]:
                            self.contextualizados["AtuadoresIncompletos"].append(indice)
    
    def analise_contextualizacao(self):
        self.contextualizacao()
        self.completude()
        return self.contextualizados

arquivo = open('requisitos.txt','r')
texto = ''
for linhas in arquivo:
    texto+=linhas
arquivo.close()
requisitos = texto.split('\n')

analise = Contextualizacao(requisitos,"m3-ontology.txt").analise_contextualizacao()
print(analise)

                        