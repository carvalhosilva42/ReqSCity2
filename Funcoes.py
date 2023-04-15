import classes as cl
import nltk
def tratar_requisitos(f):
    if f.filename.split('.')[1]=='txt':
        mensagem = ""
        for linha_arq in f:
            frase = ""
            for i in range(len(linha_arq)):
                frase += chr(linha_arq[i])
            mensagem += frase
        f.close()
        mensagem = mensagem.split('\n')
        return mensagem
    elif f.filename.split('.')[1]=='docx':
        import docx2txt as converte
        txt = converte.process(f)
        return txt.split('\n\n')

def checa(dados, indice):
    retorno=[]
    for i in range(len(dados)):
        if dados[i][1][indice]==True:
            retorno.append(dados[i][0])
    return retorno

def caminho(escolha, requisitos):
    from pickle import load
    entrada = open('trigram.pkl','rb')
    tagger = load(entrada)
    entrada.close()
    
    if escolha == 1:
        arquivo = open('passivevoice.txt','r')
        texto = ''
        for linhas in arquivo:
            texto+=linhas
        arquivo.close()
        passive_voice = texto.split('\n')
        analise_sintatica = cl.AnaliseSintatica(requisitos,tagger,passive_voice).analise()
        PV = analise_sintatica['PV']
        MS = analise_sintatica['MS']
        MVM = analise_sintatica['MVM']
        DS = analise_sintatica['DS']
        
        headings = ("Nº Requisito", "Ausência de Verbos", "Voz Passiva", "Falta de Sujeito", "Dummy Subject")
        Data = []
        for indice in range(len(requisitos)):
            aux = []
            aux.append(indice in MVM)
            aux.append(indice in PV)
            aux.append(indice in MS)
            aux.append(indice in DS)
            if True in aux:
                Data.append((indice + 1, aux))
            else:
                continue
    elif escolha ==2:
        arquivo = open('dicionario_base.txt','r')
        texto = ''
        for linhas in arquivo:
            texto+=linhas
        arquivo.close()
        palavra_amb = texto.split('\n')
        pos = cl.trigram_pos(cl.limpeza(requisitos)[1])
        amb_lexical = cl.ambiguidade_lexica(requisitos,palavra_amb,pos).requisitos_ambiguos()
        amb_sintatica = cl.ambiguidade_sintatica(requisitos,pos).retorna_ambiguidade()
        PA = amb_lexical['PA']
        AFL = amb_lexical['AFL']
        Analitical = list(amb_sintatica['Analitical'].keys())
        Coordination = list(amb_sintatica['Coordination'].keys())
        Attachment = list(amb_sintatica['Attachment'].keys())
        
        headings = ("Nº Requisito", "Palavra Ambigua", "Algoritmo Flexible Ambiguity", "Ambiguidade Analitica", "Ambiguidade por Coordenação", "Ambiguidade de ligação")
        Data = []
        for indice in range(len(requisitos)):
            aux = []
            aux.append(indice in PA)
            aux.append(indice in AFL)
            aux.append(indice in Analitical)
            aux.append(indice in Coordination)
            aux.append(indice in Attachment)
            if True in aux:
                Data.append((indice + 1, aux))
            else:
                continue
        
    elif escolha ==3:
        headings = ("Nº Requisito", "Contextualizados", "Completos")
        contextualizados = cl.Contextualizacao(requisitos,"m3-ontology.txt").analise_contextualizacao()
        Contex = contextualizados['Contextualizados']
        Sensores = contextualizados['SensoresIncompletos']
        Atuadores = contextualizados["AtuadoresIncompletos"]
        Data = []
        for i in range(len(requisitos)):
            aux = []
            aux.append(i in Contex)
            aux.append(i in Sensores)
            aux.append(i in Atuadores)
            if True in aux:
                Data.append((i + 1, aux))
            else:
                continue
    elif escolha ==4:
        import copy
        Data = {'Analise_Sintatica':[],'Ambiguidade':[],'Bons':[],'Contextualizados':[]}
        Bons = {'Analise_Sintatica':[],'Ambiguidade':[]}
        
        arquivo = open('passivevoice.txt','r')
        texto = ''
        for linhas in arquivo:
            texto+=linhas
        arquivo.close()
        passive_voice = texto.split('\n')
        analise_sintatica = cl.AnaliseSintatica(copy.deepcopy(requisitos),tagger,passive_voice).analise()
        PV = analise_sintatica['PV']
        MS = analise_sintatica['MS']
        MVM = analise_sintatica['MVM']
        DS = analise_sintatica['PV']

        for indice in range(len(requisitos)):
            aux = []
            aux.append(indice in MVM)
            aux.append(indice in PV)
            aux.append(indice in MS)
            aux.append(indice in DS)
            if True in aux:
                Data['Analise_Sintatica'].append((indice + 1, aux))
            else:
                Bons['Analise_Sintatica'].append(indice+1)
        
        arquivo = open('dicionario_base.txt','r')
        texto = ''
        for linhas in arquivo:
            texto+=linhas
        arquivo.close()
        palavra_amb = texto.split('\n')
        pos = cl.trigram_pos(cl.limpeza(requisitos)[1])
        amb_lexical = cl.ambiguidade_lexica(requisitos,palavra_amb,pos).requisitos_ambiguos()
        amb_sintatica = cl.ambiguidade_sintatica(requisitos,pos).retorna_ambiguidade()
        PA = amb_lexical['PA']
        AFL = amb_lexical['AFL']
        Analitical = list(amb_sintatica['Analitical'].keys())
        Coordination = list(amb_sintatica['Coordination'].keys())
        Attachment = list(amb_sintatica['Attachment'].keys())
        

        for indice in range(len(requisitos)):
            aux = []
            aux.append(indice in PA)
            aux.append(indice in AFL)
            aux.append(indice in Analitical)
            aux.append(indice in Coordination)
            aux.append(indice in Attachment)
            if True in aux:
                Data['Ambiguidade'].append((indice + 1, aux))
            else:
                Bons['Ambiguidade'].append(indice+1)
            
        Data['Bons'].append(list(set(Bons['Ambiguidade'])&set(Bons['Analise_Sintatica'])))
        
        contextualizados = cl.Contextualizacao(requisitos,"m3-ontology.txt").analise_contextualizacao()
        Contex = contextualizados['Contextualizados']
        Sensores = contextualizados['SensoresIncompletos']
        Atuadores = contextualizados["AtuadoresIncompletos"]

        for i in range(len(requisitos)):
            aux = []
            aux.append(i in Contex)
            aux.append(i in Sensores)
            aux.append(i in Atuadores)
            if True in aux:
                Data['Contextualizados'].append((i + 1, aux))
            else:
                continue
        headings=''
    return [Data, headings, requisitos]

