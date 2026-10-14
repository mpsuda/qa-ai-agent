---
name: analisar-requisitos
description: Analisa, refina ou revisa User Stories e requisitos funcionais para identificar requisitos explicitamente confirmados, testabilidade, dependências, lacunas bloqueantes e sugestões separadas. Use antes da geração de cenários, casos de teste ou BDD, quando for necessário verificar se os requisitos possuem informações suficientes para serem testados.
---

# Analisar requisitos

## Objetivo

Analisar somente as informações explicitamente fornecidas e produzir um diagnóstico estruturado de testabilidade, sem presumir regras de negócio.

## Processo

1. Identificar somente os requisitos explicitamente declarados.
2. Avaliar cada requisito considerando também os demais requisitos da mesma User Story.
3. Classificar sua testabilidade e explicar objetivamente o motivo.
4. Registrar somente dependências diretas entre requisitos.
5. Identificar apenas lacunas que bloqueiem a verificação.
6. Manter sugestões da IA separadas dos requisitos.
7. Retornar exclusivamente o JSON definido nesta Skill.

## Testabilidade

Marcar `testavel: true` quando houver informações suficientes para executar uma verificação e determinar objetivamente o resultado esperado.

Um requisito geral de capacidade pode ser testável quando outros requisitos da mesma User Story fornecem a regra de entrada ou o resultado observável necessário.

Considerar a própria mudança de estado explicitamente declarada como resultado observável, mesmo sem mensagem, redirecionamento ou confirmação visual.

Não exigir especificação exaustiva do produto. A ausência de regras adicionais, limite máximo, política de caracteres, autenticação ou outros campos não torna um comportamento já verificável em não testável.

Uma regra como “8 ou mais caracteres” permite verificar valores abaixo, no limite e acima do limite. Valores abaixo do mínimo violam a regra, mesmo que nenhuma mensagem de erro específica tenha sido definida.

Marcar `testavel: false` quando uma informação ausente impedir determinar uma entrada necessária ou um resultado esperado.

Termos vagos como “válido”, “adequado”, “rápido” ou “seguro” exigem critérios objetivos para serem testáveis.

Quando campo ausente, string vazia (`""`) e valor nulo (`null`) forem relevantes ao requisito analisado, não presumir que possuem o mesmo comportamento.

## Dependências

O campo `depende_de` deve conter somente requisitos diretamente necessários para determinar a entrada, a condição ou o resultado esperado do requisito atual.

Se o requisito A utiliza uma regra fornecida pelo requisito B, registrar B em `depende_de` de A.

Cada dependência deve corresponder exatamente ao texto de outro requisito presente em `requisitos_confirmados`, considerando o valor após a leitura do JSON.

Se o campo `motivo` afirmar que outro requisito fornece uma informação necessária, registrar esse requisito em `depende_de`.

Não inverter dependências, não criar ciclos e não confundir sequência com dependência.

Não repetir dependências transitivas. Se A depende de B e B depende de C, registrar C em A somente quando A também depender diretamente de C.

## Lacunas e sugestões

Registrar em `lacunas_perguntas` somente ausências que bloqueiem efetivamente a verificação de um requisito explícito.

Não transformar possibilidades adicionais, aumento de cobertura ou detalhamento opcional em lacunas bloqueantes.

Não ampliar o escopo com autenticação, histórico, múltiplos cadastros, internacionalização, integrações externas ou funcionalidades não mencionadas, salvo quando forem indispensáveis para verificar o requisito.

Evitar perguntas redundantes ou variações da mesma lacuna.

Registrar em `sugestoes_ia` somente sugestões diretamente relacionadas às lacunas identificadas.

Sugestões não são requisitos confirmados e não devem introduzir novas funcionalidades desnecessárias.

Quando não houver lacunas ou sugestões relevantes, retornar listas vazias.

Quando um comportamento esperado estiver indefinido e for necessário para verificar o requisito, registrá-lo como pergunta em `lacunas_perguntas`; não preencher essa ausência apenas com uma sugestão.

As sugestões podem indicar qual decisão precisa ser tomada, mas não devem escolher valores, máscaras, formatos, mensagens ou regras concretas que não tenham sido fornecidas, salvo quando o usuário pedir explicitamente recomendações de negócio.

Toda ausência mencionada no campo `motivo` como impedimento à testabilidade deve possuir uma pergunta correspondente em `lacunas_perguntas`. Não mencionar um bloqueio somente no motivo.

## Restrições de escopo

Não gerar:

- status geral de testabilidade;
- cenários de teste;
- técnicas de teste;
- casos de teste;
- BDD.

O status geral será calculado posteriormente pelo código Python.

## Formato de saída

Retornar somente um objeto JSON válido, sem Markdown, crases ou explicações antes ou depois:

```json
{
  "requisitos_confirmados": [
    {
      "requisito": "",
      "testavel": true,
      "motivo": "",
      "depende_de": []
    }
  ],
  "lacunas_perguntas": [],
  "sugestoes_ia": []
}
```

Usar valores booleanos JSON `true` ou `false`, nunca strings.

`lacunas_perguntas`, `sugestoes_ia` e `depende_de` devem ser listas de strings.

## Integridade do JSON

A resposta deve ser processável diretamente por `json.loads()` sem correções.

Preservar no campo `requisito` o texto original. Após o processamento por `json.loads()`, seu valor deve ser idêntico ao requisito recebido, incluindo acentuação e pontuação.

Quando houver aspas duplas dentro de um valor textual, representá-las com o escape Unicode `\u0022`.

Exemplo:

```json
{
  "requisito": "O sistema deve exibir a mensagem: \u0022Senha alterada com sucesso.\u0022"
}
```

Não converter textos para ASCII.

Antes de responder, conferir internamente aspas, vírgulas, chaves, colchetes, tipos dos campos e correspondência das dependências.