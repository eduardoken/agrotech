# Agrotech: Gestão e Monitoramento de Perdas na Colheita da Cana-de-Açúcar

## Contexto e Problema do Agronegócio
A colheita mecanizada de cana-de-açúcar no Brasil apresenta perdas estimadas em até 15% da produção total. Essa ineficiência gera prejuízos financeiros significativos aos produtores e impacta a produtividade da agroindústria.

## Solução Proposta
Desenvolvimento de uma ferramenta em Python para monitoramento e controle das perdas agrícolas por talhão. A solução registra a porcentagem de perdas, calcula o volume em toneladas perdidas e o impacto financeiro em reais, permitindo a exportação dos dados e integração com banco de dados.

## Requisitos Técnicos Implementados (Capítulos 3 a 6)

- **Subalgoritmos:** Funções e procedimentos organizados com passagem de parâmetros e validação de entradas do usuário.
- **Estruturas de Dados:** Utilização de listas, dicionários e tuplas para o armazenamento dinâmico das informações dos talhões.
- **Validação e Consistência:** Tratamento de exceções (`try-except`) para evitar entradas inválidas (textos em campos numéricos ou valores negativos).
- **Manipulação de Arquivos:**
  - Exportação de relatórios em formato Texto (`relatorio_perdas.txt`).
  - Persistência estruturada em formato JSON (`dados_perdas.json`).
- **Conexão com Banco de Dados:** Módulo de integração preparado para gravação no banco Oracle (`oracledb` / `cx_Oracle`).