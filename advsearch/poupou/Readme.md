# Trabalho 2 - Busca com Adversário

## Integrantes

- Vinícius Bergonzi Lazzari (334056)
- Turma: B

## Bibliotecas necessárias

Nenhuma. A implementação usa apenas bibliotecas padrão do Python 3 (`time`, `typing`...).

## 1. Minimax com poda alfa-beta (`minimax.py`)

A implementação do Minimax com poda alfa-beta usa a função recursiva `value`, que percorre a árvore de jogadas
em profundidade (DFS). Ela retorna a avaliação do estado, calculada por `eval_func(s, me)` sempre do ponto de vista
do jogador da raiz (`me`), assim que encontra um nó terminal ou quando `depth == max_depth`, o que limita a
profundidade da busca. Com `max_depth = -1` essa condição nunca é satisfeita, e a busca vai até os estados terminais.

A função também funciona em árvores em que os jogadores não se alternam em toda jogada, como no Othello, em que um
jogador sem jogadas legais passa a vez. Em cada nó, a condição `s.player == me` define a variável booleana
`maximizing`: o nó é de maximização quando quem joga é o jogador da raiz, e de minimização caso contrário.
Assim, quando o oponente passa a vez, o nó seguinte continua sendo de maximização.

Em cada nó, o algoritmo itera sobre as jogadas legais, calcula recursivamente o valor de cada estado sucessor e
atualiza `best`, além de `alpha` (nos nós de maximização) ou `beta` (nos de minimização). Sempre que `alpha >= beta`,
os demais sucessores são podados, pois não podem alterar a decisão.

Na raiz, `value` é chamada uma vez para cada jogada possível, e o valor de `alpha` é mantido entre essas chamadas,
o que permite podar também os ramos das jogadas seguintes. A função retorna em `best_move` a jogada de maior valor,
que é a mesma que o minimax sem poda escolheria, ou seja, a jogada ótima segundo a função de avaliação até a
profundidade pesquisada.

## 2. Tic-Tac-Toe Misere — avaliação (item 2.2 a)

**Função `utility`:** avalia estados terminais do ponto de vista do jogador da raiz. Usa `state.winner()`, que já
aplica a regra invertida (perde quem alinha 3 peças), e retorna +1 se o jogador venceu, −1 se perdeu e 0 em caso
de empate. Como o jogo é pequeno, o minimax roda sem limite de profundidade (`max_depth = -1`), então só estados
terminais são avaliados.

### (i) O minimax sempre ganha ou empata contra o randomplayer?

40 partidas via `server.py` (20 com cada cor):

| Minimax joga com | Vitórias | Empates | Derrotas |
|---|---|---|---|
| Pretas (começa) | 13 | 7 | 0 |
| Brancas | 20 | 0 | 0 |
| **Total** | **33** | **7** | **0** |

Por esses resultados podemos garantir que a avaliação funciona, visto que o agente não perdeu nenhuma partida e
empatou apenas 7, começando como Pretas, o que é uma desvantagem nesse jogo. 

### (ii) O minimax sempre empata consigo mesmo?

Partidas minimax × minimax via `server.py`: **empate (0 × 0)** em todas. Como o algoritmo é determinístico, todas as partidas são idênticas.

### (iii) O minimax não perde para vocês jogando com a melhor estratégia?

| Partida | Humano joga com | Resultado |
|---|---|---|
| 1 | Pretas | Agente ganhou |
| 2 | Pretas | Empate |
| 3 | Brancas | Empate |
| 4 | Brancas | Empate |

Por essa avaliação, é impossível ganhar um jogo contra o agente, visto que o espaço de busca é pequeno, o agente
consegue avaliar todas as combinações possíveis e garantir que toda jogada é ótima. O melhor resultado possível contra
o agente é o empate, caso ambos os jogadores joguem de maneira perfeita.

## 3. Othello

### 3.1 Heurísticas de contagem e de valor posicional

- **Contagem (`evaluate_count`)**: retorna a diferença entre o número de peças do jogador e o do oponente, usando
  `num_pieces` do tabuleiro. É a heurística mais simples e só retorna um valor para o estado atual: durante o jogo as peças mudam de cor frequentemente, então ter mais peças agora não necessariamente significa uma vantagem.
- **Valor posicional (`evaluate_mask`)**: itera o tabuleiro somando o valor da máscara `EVAL_TEMPLATE` (fornecida
  pelo kit e mantida sem alterações) em cada casa ocupada pelo jogador e subtraindo o valor das casas ocupadas pelo
  oponente. A máscara valoriza as quinas (100) e penaliza as casas vizinhas a elas (−30 e −50), que costumam
  entregar a quina ao adversário (uma estratégia utilizada também na heurística customizada).

### 3.2 Heurística customizada (`evaluate_custom`)

A heurística implementada combina 4 estratégias diferentes para avaliar o estado do jogo:

- **Quinas** (±10 por quina): assim como na máscara de `evaluate_mask`, as quinas são valorizadas porque uma peça em
  uma quina nunca pode ser virada pelo adversário, o que as torna muito valiosas para quem as obtém. Cada quina do
  jogador soma 10 pontos, e cada quina do oponente subtrai 10.
- **X-squares** (∓5 por casa): também penalizados em `evaluate_mask`, os X-squares são as casas na diagonal de uma
  quina. Um jogador que ocupa um X-square enquanto a quina ainda está vazia costuma entregar essa quina ao oponente.
  Por isso, cada X-square do jogador subtrai 5 pontos e cada X-square do oponente soma 5. Diferente da máscara, que
  usa valores fixos, esse termo só conta enquanto a quina correspondente está vazia: depois que ela é ocupada, o
  perigo deixa de existir.
- **Mobilidade** (±1 por jogada): uma ideia nova em relação às heurísticas anteriores. Ela calcula quantas jogadas
  legais o estado garante ao jogador e quantas garante ao oponente, e subtrai uma da outra. Um estado em que o jogador
  tem muito mais opções que o adversário é melhor, pois permite esperar por boas jogadas, enquanto o oponente com
  poucas opções acaba forçado a fazer jogadas ruins.
- **Fronteira** (∓1 por peça): conta as peças que estão encostadas em pelo menos uma casa vazia (nas 8 direções).
  Essas peças de fronteira dão ao oponente lugares onde jogar e podem ser viradas com facilidade. Por isso, cada peça
  de fronteira do jogador subtrai 1 ponto, e cada peça de fronteira do oponente soma 1. Esse termo complementa a
  mobilidade: ela mede as jogadas disponíveis agora, enquanto a fronteira estima as jogadas que o oponente terá
  depois.

Por fim, quando o estado é terminal (nenhum dos jogadores tem jogadas), a heurística ignora esses termos e retorna
apenas o resultado da partida: +1000 em caso de vitória, −1000 em caso de derrota e 0 em caso de empate. O valor
1000 é maior do que qualquer pontuação que um estado não terminal pode alcançar, então uma vitória garantida sempre
é preferida a qualquer outra estimativa.

| Termo | Peça/casa do jogador | Peça/casa do oponente | O que mede |
|---|---|---|---|
| Quinas | +10 por quina | −10 por quina | Quinas nunca podem ser viradas |
| X-squares (só com a quina vazia) | −5 por casa | +5 por casa | Casa diagonal a uma quina vazia: costuma entregar a quina ao oponente |
| Mobilidade | +1 por jogada legal | −1 por jogada legal | Quem tem mais opções de jogada |
| Fronteira | −1 por peça | +1 por peça | Peças encostadas em casa vazia dão jogadas futuras ao oponente |
| Fim de jogo | +1000 se vence | −1000 se perde | Em estado terminal, só o resultado importa (0 no empate) |

A pontuação final é `10 × quinas + 5 × x_squares + mobilidade + fronteira`, em que cada termo já é a diferença entre
o jogador e o oponente (com o sinal da tabela).

**Fontes consultadas**

- [Computer Othello — Wikipedia](https://en.wikipedia.org/wiki/Computer_Othello)
- [otto-othello (pesos por fase do jogo)](https://github.com/eigenfoo/otto-othello)
- [An Analysis of Othello AI Strategies](https://barberalec.github.io/pdf/An_Analysis_of_Othello_AI_Strategies.pdf)
- [Reversi Strategy Guide](https://reversi-baj.pages.dev/articles/reversi-strategy-guide/)
- [Reversi Parity Guide](https://reversi-baj.pages.dev/articles/reversi-parity-guide/)

### 3.3 Critério de parada

| Agente | Critério | Jogada mais lenta medida |
|---|---|---|
| Contagem, posicional, customizada | Profundidade máxima fixa = 4 | 0,19 s / 0,30 s / 0,35 s |
| Agente do torneio | Aprofundamento iterativo, interrompido aos 4 s | ≈ 4,0 s (limite do servidor: 5 s) |

Para as heurísticas mais simples, uma profundidade máxima fixa de 4 níveis foi escolhida, pois permitia iterar
rapidamente sobre os resultados e testes. Para o agente do torneio, o limite de 5 segundos foi levado em consideração:
o agente busca iterativamente até atingir 4 segundos de tempo de uso, interrompendo a busca nesse momento, o que 
garante que o tempo de busca estará dentro do limite estabelecido com margem.

### 3.4 Mini-torneio (item 2.2 b)

Partidas via `server.py`, posição inicial padrão. O primeiro agente joga com as pretas e começa.

| Partida (pretas × brancas) | Peças finais | Vencedor |
|---|---|---|
| Contagem × Posicional | 28 × 36 | Posicional |
| Posicional × Contagem | 22 × 42 | Contagem |
| Contagem × Customizada | 15 × 49 | Customizada |
| Customizada × Contagem | 41 × 23 | Customizada |
| Posicional × Customizada | 18 × 46 | Customizada |
| Customizada × Posicional | 39 × 25 | Customizada |

| Agente | Vitórias | Peças capturadas (soma) |
|---|---|---|
| **Customizada** | **4** | **175** |
| Contagem | 1 | 108 |
| Posicional | 1 | 101 |

**Implementação mais bem-sucedida:** heurística customizada (4 vitórias em 4 partidas).

Como é possível observar, a heurística customizada ganha das estratégias de Contagem e Posicional em todas as
simulações jogadas, provando assim que a estratégia oferece melhores resultados do que as vistas anteriormente.

### 3.5 Agente do torneio (`tournament_agent.py`)

O agente do torneio usa o mesmo minimax com poda alfa-beta (`minimax.py`) e a heurística customizada da seção 3.2,
mas troca a profundidade fixa por uma busca limitada por tempo. Seus componentes são:

1. **Aprofundamento iterativo**: executa a poda alfa-beta com profundidade 1, 2, 3… até se passarem 4 segundos e
   joga o resultado da última profundidade finalizada (seção 4.1).
2. **Heurística customizada**: as folhas são avaliadas com `evaluate_custom` (quinas, X-squares, mobilidade e
   fronteira), a melhor das três heurísticas no mini-torneio.
3. **`FasterBoard`**: subclasse do `Board` do kit que deixa a busca cerca de 1,8× mais rápida sem mudar as regras do
   jogo (seção 4.2).
4. **Jogada única**: se existe só uma jogada legal, ela é feita imediatamente, sem busca.
5. **Regras do torneio**: o limite de 4 s deixa 1 s de folga em relação aos 5 s do servidor. Como o limite usa o
   relógio real, em uma máquina mais lenta o agente apenas busca menos, sem estourar o tempo. O agente não cria
   threads nem processos e não lê nem grava arquivos.

**Desempenho:** a versão do agente antes da fronteira, com `FasterBoard`, buscou em média 6,35 níveis de
profundidade, contra 4 dos agentes de profundidade fixa, e venceu as 6 partidas contra contagem, posicional e
customizada (posição inicial, cada um com as duas cores). A jogada mais lenta levou 4,03s, sem nenhum estouro de
tempo ou jogada ilegal no `server.py`. Com a fronteira, o agente venceu 13 de 16 partidas contra a versão sem
fronteira a partir da posição inicial (seção 5).

## 4. Extras

### 4.1 Aprofundamento iterativo com limite de tempo

Técnica não vista em aula. Com profundidade fixa, o tempo de cada jogada varia muito: com profundidade 4, a jogada
mais lenta da heurística customizada levou 0,35s, deixando sem uso quase todo o limite de 5s, mas aumentar a
profundidade fixa poderia estourar o tempo nas posições com muitas jogadas possíveis. O aprofundamento iterativo
resolve esse problema: o agente repete a busca com profundidades crescentes e sempre tem pronta a jogada da última busca
completa, buscando mais fundo quando há poucas jogadas (por exemplo, no fim do jogo) e menos quando há muitas.

Como a assinatura de `minimax_move` não pode mudar, a interrupção é feita pela função de avaliação: o agente passa ao
minimax uma versão de `evaluate_custom` que confere o relógio a cada chamada e lança uma exceção quando o prazo acaba.
Como a avaliação é chamada em toda folha da árvore, a busca para quase imediatamente, e a busca incompleta é
descartada. A busca também para quando a profundidade alcança o número de casas vazias, pois a partir daí ela já
cehgou ao fim do jogo.

Na primeira versão do agente do torneio (ainda sem `FasterBoard` e sem a fronteira), essa técnica alcançou em média
cerca de 6 níveis de profundidade, contra 4 dos agentes de profundidade fixa, e venceu as 6 partidas contra
contagem, posicional e customizada.

### 4.2 `FasterBoard`

Ao medir onde a busca gastava tempo (com `cProfile`), observamos que cerca de 77% ia para o cálculo de jogadas legais no
`Board` do kit, e que ele era feito cerca de 3 vezes por tabuleiro criado, quando 2 bastariam (uma por cor). O
motivo é o `copy` do kit: ele converte o tabuleiro em texto e o reconstrói, descartando as jogadas legais já
calculadas, que são recalculadas logo em seguida, quando `process_move` confere se a jogada é legal. Além disso,
`has_legal_move` calcula as jogadas do oponente sem guardá-las.

A `FasterBoard` é uma subclasse com apenas dois métodos reescritos: `copy`, que copia as linhas da matriz
diretamente e mantém as jogadas já calculadas (válidas, pois a cópia é idêntica ao original; quando uma peça é
colocada, o próprio kit as invalida), e `has_legal_move`, que reaproveita essas jogadas. As regras continuam sendo
as do kit: verificamos em 6.000 posições que as jogadas legais e os tabuleiros resultantes são idênticos aos do
`Board` original.

Numa busca de profundidade 6, a `FasterBoard` foi 1,8× mais rápida, o que elevou a profundidade média do agente do
torneio de 6,03 para 6,35. Com tempo real (4 s por jogada), a versão com `FasterBoard` venceu a versão anterior por
**12 vitórias, 5 derrotas e 1 empate**, sem estouros de tempo.

## 5. Experimentos

Cada ideia foi testada como uma versão candidata da heurística, diferente da versão atual em apenas um ponto, e
jogou contra a versão atual. Para que as partidas não se repetissem, cada uma começou a partir de uma abertura
aleatória (6 jogadas sorteadas), e cada abertura foi jogada duas vezes, uma com cada cor. Os resultados são a
porcentagem de partidas vencidas pela candidata (empate conta meia vitória).

O teste foi feito em três etapas, para separar melhora real de sorte:

1. **Triagem**: 128 partidas por ideia, com 0,1s por jogada para ser rápido. Uma candidata "controle", idêntica à
   versão atual, mediu o quanto um resultado pode variar só por sorte: 52,7%.
2. **Reverificação**: as 3 melhores jogaram 64 partidas novas, em outras aberturas, com 0,5s por jogada.
3. **Tempo real**: a melhor jogou 24 partidas com 4 s por jogada.

### Variações da heurística testadas

Triagem: 128 partidas por ideia, 0,1s por jogada, contra a versão então atual. Uma "controle" idêntica à versão atual mede o efeito da sorte (52,7%).

| Ideia | Resultado (vitórias) |
|---|---|
| Fronteira | 53,5% → 58,6% (64 partidas novas, 0,5s) → 56,2% (24 partidas, 4s) |
| Poucas peças no início | 59,4% → 46,9% na reverificação |
| Pegar quina imediatamente | 43,8% |
| Contagem de peças no fim | 43,0% |
| Mobilidade ×2 | 39,5% |
| Mobilidade por fase do jogo | 37,9% |

### Validação da fronteira

| Teste | Resultado |
|---|---|
| Customizada com fronteira × sem, profundidade 4, 200 partidas | 120 V, 75 D, 5 E |
| Agente do torneio com × sem fronteira, posição inicial, `server.py` (5 s) | 13 V, 3 D (cerca de 6 partidas distintas) |
| Customizada com fronteira × contagem e posicional, 24 aberturas aleatórias cada | 24–0 e 23–1 |

### Otimizações da busca testadas

| Ideia | Resultado |
|---|---|
| Memoização da avaliação | 0% mais rápido |
| Ordenação de jogadas | 5 V, 9 D com tempo real |
| Desligar o garbage collector | sem ganho (1,04× e 0,90×) |
| `FasterBoard` (adotada, seção 4.2) | 12 V, 5 D, 1 E com tempo real |

### Conclusões

- **Só a fronteira melhorou de forma consistente.** Ela ficou acima de 50% nas três etapas e venceu 120 de 200
  partidas contra a heurística anterior (chance de cerca de 0,1% de isso acontecer por sorte), por isso foi
  adotada. O ganho é moderado: a margem média de peças foi de apenas +1,9.
- **Um bom resultado isolado não basta.** "Poucas peças no início" foi a melhor ideia na triagem (59,4%), mas caiu
  para 46,9% em aberturas novas: o primeiro resultado foi sorte.
- **Os pesos atuais já estavam bem ajustados.** Mudar os pesos das quinas, dos X-squares ou da mobilidade não
  melhorou o resultado, e mudanças grandes (mobilidade ×2, por fase do jogo) pioraram claramente.
- **Velocidade nem sempre vira vitória.** A ordenação de jogadas deixaram a busca
  mais rápida, mas não venceram mais partidas. Testes rápidos (0,4s por jogada) também podem enganar: a ordenação
  venceu 15 de 24 partidas nesse teste e só 5 de 14 com tempo real. Por isso, as mudanças adotadas foram confirmadas
  com tempo real.

## 6. Uso de chatbots e agentes de IA

Para esse projeto, principalmente a ferramenta Claude foi utilizada para as seguintes tarefas:

- Guiar e dar ideias de implementação de código, especialmente em funções mais complicadas como o Timeout por 
tempo do aprofundamento iterativo.
- Dar ideias de possiveis estratégias de heurísticas a serem testadas e implementadas.
- Uma vez que o código foi implementado, verificar que o mesmo atendia aos critérios requisitados.
- Debugar a função de `Board` para achar bottlenecks e sugerir melhorias.
- Corrigir e formatar este relatório.
