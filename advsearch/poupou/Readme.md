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

Por essa avalição, é impossível ganhar um jogo contra o agente, visto que o espaço de busca é pequeno, o agente
consegue avaliar todos possíveis combinações e garantir que toda jogada é ótima. O melhor resultado possível contra
o agente é o empate, caso ambos os jogadores joguem de maneira perfeita.

## 3. Othello

### 3.1 Heurísticas de contagem e de valor posicional

TODO: descrevam brevemente:

- **Contagem (`evaluate_count`)**: peças do jogador − peças do oponente;
- **Valor posicional (`evaluate_mask`)**: soma dos valores de `EVAL_TEMPLATE` nas casas do jogador − nas casas do oponente (máscara do kit, sem alteração).

### 3.2 Heurística customizada (`evaluate_custom`)

TODO: expliquem a heurística com suas palavras. Ela combina quatro termos:

| Termo | Peso | O que mede |
|---|---|---|
| Quinas | ±10 por quina | Quinas nunca podem ser viradas |
| X-squares | ∓5 por casa | Casa diagonal a uma quina **vazia**: costuma entregar a quina ao oponente |
| Mobilidade | ±1 por jogada | Jogadas legais do jogador − jogadas legais do oponente |
| Fronteira | ∓1 por peça | Peças encostadas em casa vazia dão jogadas ao oponente |
| Fim de jogo | ±1000 / 0 | Em estado terminal, só importa vitória, derrota ou empate |

TODO: escrevam como chegaram aos pesos (ver seção 5, experimentos).

**Fontes consultadas** — TODO: digam como foram usadas (ex.: conceitos tirados das fontes e combinados pelo grupo; pesos definidos por testes próprios):

- [Computer Othello — Wikipedia](https://en.wikipedia.org/wiki/Computer_Othello)
- [otto-othello (pesos por fase do jogo)](https://github.com/eigenfoo/otto-othello)
- [An Analysis of Othello AI Strategies](https://barberalec.github.io/pdf/An_Analysis_of_Othello_AI_Strategies.pdf)
- [Reversi Strategy Guide](https://reversi-baj.pages.dev/articles/reversi-strategy-guide/)
- [Reversi Parity Guide](https://reversi-baj.pages.dev/articles/reversi-parity-guide/)
- [Reversi & Othello Glossary](https://rarepike.com/reversi/glossary/)
- [Reversi AI and Computer Players](https://rarepike.com/reversi/computer-ai/)

### 3.3 Critério de parada

| Agente | Critério | Jogada mais lenta medida |
|---|---|---|
| Contagem, posicional, customizada | Profundidade máxima fixa = 4 | 0,19 s / 0,30 s / 0,35 s |
| Agente do torneio | Aprofundamento iterativo, interrompido aos 4 s | ≈ 4,0 s (limite do servidor: 5 s) |

TODO: justifiquem a escolha da profundidade 4 e da folga de 1 s.

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

TODO: comentário sobre os resultados.

### 3.5 Agente do torneio (`tournament_agent.py`)

TODO: expliquem a implementação escolhida. Componentes:

1. **Aprofundamento iterativo**: busca com profundidade 1, 2, 3… até 4 s; joga o resultado da última profundidade completa. A função de avaliação confere o relógio e interrompe a busca quando o tempo acaba.
2. **Heurística customizada** (seção 3.2).
3. **`FasterBoard`**: subclasse do `Board` do kit que copia o tabuleiro sem passar por texto e reaproveita as jogadas legais já calculadas.
4. Se só existe uma jogada legal, ela é feita imediatamente.
5. Não cria threads/processos nem usa arquivos.

TODO: comentem a profundidade alcançada e o desempenho em jogo.

---

## 4. Extras

TODO: escrevam um parágrafo por item.

- **Aprofundamento iterativo com limite de tempo** (técnica não vista em aula), com os mesmos componentes da seção 3.5.
- **`FasterBoard`**: medido 1,8× mais rápido que o `Board` do kit numa busca de profundidade 6; contra a versão anterior do agente do torneio, com tempo real (4 s): **12 vitórias, 5 derrotas, 1 empate**.
- **Experimentos de heurística** (seção 5).

---

## 5. Experimentos

TODO: descrevam a metodologia (partidas candidata × versão atual, aberturas aleatórias, as duas cores).

### Variações da heurística testadas

Triagem: 128 partidas por ideia, 0,1 s por jogada, contra a versão então atual. Uma "controle" idêntica à versão atual mede o efeito da sorte (52,7%).

| Ideia | Resultado (vitórias) |
|---|---|
| Fronteira | 53,5% → 58,6% (64 partidas novas, 0,5 s) → 56,2% (24 partidas, 4 s) |
| Poucas peças no início | 59,4% → 46,9% na reverificação |
| X-square 3, margem de vitória, quina 20, C-squares, paridade, bordas estáveis, mobilidade ×0,5, mobilidade potencial | 50–53% (igual à sorte) |
| X-square 8 | 47,7% |
| Pegar quina imediatamente | 43,8% |
| Contagem de peças no fim | 43,0% |
| Aceitar só profundidades ímpares | 39,8% |
| Mobilidade ×2 | 39,5% |
| Mobilidade por fase do jogo | 37,9% |
| Aceitar só profundidades pares | 36,3% |

### Validação da fronteira

| Teste | Resultado |
|---|---|
| Customizada com fronteira × sem, profundidade 4, 200 partidas | 120 V, 75 D, 5 E |
| Agente do torneio com × sem fronteira, posição inicial, `server.py` (5 s) | 13 V, 3 D (cerca de 6 partidas distintas) |
| Customizada com fronteira × contagem e posicional, 24 aberturas aleatórias cada | 24–0 e 23–1 |

### Otimizações testadas e descartadas

| Ideia | Resultado |
|---|---|
| Memoização da avaliação | 0% mais rápido |
| Ordenação de jogadas | 5 V, 9 D com tempo real |
| Jogadas legais com bitboard | 15 V, 15 D, 2 E (0,4 s por jogada) |
| Desligar o coletor de lixo | sem ganho (1,04× e 0,90×) |

TODO: conclusões.

---

## 6. Uso de chatbots e agentes de IA

TODO: declaração explícita e honesta. O enunciado pede que relatem:

- quais ferramentas usaram (ex.: Claude Code);
- como usaram (quais partes do código e dos testes vieram da IA, o que foi feito pelo grupo);
- uma avaliação da experiência.

Lembrem que o enunciado não permite usar IA para gerar códigos completos que resolvam o trabalho.
