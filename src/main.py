from collections import defaultdict, deque

def escrever_resultados(caminho_arquivo, palavras, resultados):
    with open(caminho_arquivo, 'w') as f:
        for palavra, resultado in zip(palavras, resultados):
            if resultado:
                f.write(f"aceito {''.join(palavra)}\n")
            else:
                f.write(f"nao aceito {''.join(palavra)}\n")

def validar_palavras(afd, palavras):
    resultados = []
    
    for palavra in palavras:
        estado_atual = afd['estado_inicial']
        
        for caractere in palavra:
            if caractere in afd['transicoes'][estado_atual]:
                estado_atual = afd['transicoes'][estado_atual][caractere]
            else:
                resultados.append(False)
                break
        
        if estado_atual in afd['estados_finais']:
            resultados.append(True)
        else:
            resultados.append(False)
    return resultados

def ler_palavras(caminho_arquivo): 
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    return [list(linha.strip()) for linha in linhas]

def obter_estados_alcancaveis(afnd, estados):
    estados_alcancaveis = set(estados)
    fila = deque(estados)
    
    while fila:
        estado_atual = fila.popleft()
        if estado_atual in afnd['transicoes'] and 'h' in afnd['transicoes'][estado_atual]:
            for estado in afnd['transicoes'][estado_atual]['h']:
                if estado not in estados_alcancaveis:
                    estados_alcancaveis.add(estado)
                fila.append(estado)
    return tuple(sorted(estados_alcancaveis))  # Dicionário aceita apenas tuplas como chaves ('A', 'B')

def calcular_transicoes_para_estado(afnd, estado_atual):
    transicoes_por_simbolo = defaultdict(set)
    
    for estado in estado_atual:
        if estado in afnd['estados']:
            for simbolo, proximos_estados in afnd['transicoes'][estado].items():
                if simbolo != 'h':
                    for proximo_estado in proximos_estados:
                        transicoes_por_simbolo[simbolo].update(obter_estados_alcancaveis(afnd, [proximo_estado]))    
    return transicoes_por_simbolo

def converter_afnd_para_afd(afnd):
    afd = {
        'estados': set(),
        'estado_inicial': None,
        'estados_finais': set(),
        'transicoes': defaultdict(dict)
    }

    afd['estado_inicial'] = obter_estados_alcancaveis(afnd, [afnd['estado_inicial']])
    afd['estados'].add(afd['estado_inicial'])
    
    processados = set()
    nao_processados = [afd['estado_inicial']]  # Array para armazenar os novos estados (tuplas) não processados [('A', 'B')]
    
    while nao_processados:
        estado_atual = nao_processados.pop(0)  # ('A', 'B')
        if estado_atual in processados:
            continue
        processados.add(estado_atual)
        
        afd['transicoes'][estado_atual] = {}  # {'A': {}}

        transicoes_por_simbolo = calcular_transicoes_para_estado(afnd, estado_atual)  # Cálculo do novo estado através das transições do símbolo {'0': {'A', 'B', 'C'}}
    
        for simbolo, novo_estado in transicoes_por_simbolo.items():
            novo_estado = tuple(sorted(novo_estado))  # Dicionário aceita apenas tuplas como chaves ('A', 'B')
            if novo_estado not in afd['estados']: 
                afd['estados'].add(novo_estado)  # Adiciona o novo estado descoberto aos estados do afd
                nao_processados.append(novo_estado)  # Adiciona o novo estado para ser processado
            afd['transicoes'][estado_atual][simbolo] = novo_estado  # Adiciona uma transição do estado atual para o novo estado

        # Verifica se algum estado dentro do estado atual é um estado final
        if any(estado in afnd['estados_finais'] for estado in estado_atual):
            afd['estados_finais'].add(estado_atual)
    
    return afd

def salvar_afd(caminho_arquivo, afd):
    with open(caminho_arquivo, 'w') as f:
        estados_str = [''.join(estado) for estado in afd['estados']]
        f.write(' '.join(estados_str) + '\n')

        estado_inicial_str = ''.join(afd['estado_inicial']) if isinstance(afd['estado_inicial'], tuple) else afd['estado_inicial']
        f.write(estado_inicial_str + '\n')

        estados_finais_str = [''.join(estado) for estado in afd['estados_finais']]
        f.write(' '.join(estados_finais_str) + '\n')
        
        for estado, transicoes in afd['transicoes'].items():
            estado_str = ''.join(estado)  # Concatenando os estados
            for simbolo, proximo_estado in transicoes.items():
                proximo_estado_str = ''.join(proximo_estado) if isinstance(proximo_estado, tuple) else proximo_estado
                f.write(f"{estado_str} {simbolo} {proximo_estado_str}\n")

def ler_afnd(caminho_arquivo):
    afnd = {
        'estados': set(),
        'estado_inicial': None,
        'estados_finais': set(),
        'transicoes': defaultdict(lambda: defaultdict(list))
    }
    
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
    
    afnd['estados'] = set(linhas[0].strip().split())
    afnd['estado_inicial'] = linhas[1].strip()
    afnd['estados_finais'] = set(linhas[2].strip().split())
    
    for linha in linhas[3:]:
        estado_atual, simbolo, proximo_estado = linha.strip().split()
        if estado_atual not in afnd['estados'] or proximo_estado not in afnd['estados']:
            raise ValueError(f"Estado inválido: {estado_atual} ou {proximo_estado} não está na lista de estados.")
        afnd['transicoes'][estado_atual][simbolo].append(proximo_estado)

    return afnd

caminho_arquivo_entrada = 'src/inputs/afnd.txt'
caminho_arquivo = 'src/outputs/afd.txt'
caminho_arquivo_palavras = 'src/inputs/palavras.txt'
caminho_arquivo_resultado = 'src/outputs/resultado.txt'

afnd = ler_afnd(caminho_arquivo_entrada)
afd = converter_afnd_para_afd(afnd)
salvar_afd(caminho_arquivo, afd)

palavras = ler_palavras(caminho_arquivo_palavras)
resultado = validar_palavras(afd, palavras)
escrever_resultados(caminho_arquivo_resultado, palavras, resultado)