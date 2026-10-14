---
name: gerar-casos-de-teste
description: Gera casos de teste estruturados exclusivamente a partir de requisitos previamente analisados, aprovados e liberados pelo QA. Use quando houver solicitação de geração de testes para requisitos explicitamente liberados, após o gate de qualidade. Não use para analisar requisitos, decidir testabilidade ou gerar BDD.
---

# Gerar casos de teste

## Objetivo

Gerar casos de teste rastreáveis, concretos e executáveis somente para requisitos já liberados pelo gate de qualidade.

## Entrada obrigatória

Gerar testes somente quando a entrada:

- declarar que os requisitos foram aprovados ou liberados pelo QA; ou
- utilizar `GERAÇÃO_COMPLETA_AUTORIZADA`; ou
- utilizar `GERAÇÃO_PARCIAL_AUTORIZADA`; ou
- identificar explicitamente uma lista como `requisitos liberados`.

Considerar a expressão `requisitos liberados`, utilizada pelo código Python após o gate, como autorização suficiente.

Se não houver autorização explícita, se a análise estiver rejeitada, se a geração estiver bloqueada ou se não houver requisitos liberados, retornar somente:

```json
{
  "casos_de_teste": []
}
```

Não reavaliar a testabilidade e não liberar requisitos por conta própria.

## Processo

1. Verificar se houve liberação explícita pelo QA.
2. Considerar exclusivamente os requisitos liberados.
3. Preservar exatamente o texto de cada requisito.
4. Definir a cobertura aplicável sem criar regras adicionais.
5. Selecionar uma técnica coerente com a regra explícita.
6. Criar entradas concretas e resultados esperados verificáveis.
7. Eliminar casos duplicados.
8. Validar a estrutura e retornar somente o JSON.

## Cobertura

Criar pelo menos um caso para cada requisito liberado.

Não omitir silenciosamente um requisito liberado. Se algum requisito liberado não permitir a criação de um caso executável sem inventar informações, considerar a entrada inconsistente com o gate e retornar:

```json
{
  "casos_de_teste": []
}

Criar casos positivos somente a partir de comportamentos ou resultados explicitamente definidos.

Criar casos negativos somente quando uma regra explícita permitir determinar que uma entrada viola o requisito.

Aplicar Análise de Valor de Fronteira somente quando existir limite numérico explícito.

Para um limite mínimo `N`, considerar, quando aplicável:

- `N - 1`;
- `N`;
- `N + 1`.

Classificar como `FRONTEIRA` os casos criados especificamente para esses valores, mesmo quando `N - 1` resultar em rejeição.

Não criar outro caso negativo equivalente quando o caso `N - 1` já fornecer a mesma cobertura.

Usar `Particionamento de Equivalência` quando existirem classes objetivas de entradas aceitas ou rejeitadas.

Usar `Teste Baseado em Requisitos` para verificar comportamentos, mudanças de estado ou mensagens explicitamente declaradas.

Utilizar no campo `tecnica` somente um destes valores:

- `Particionamento de Equivalência`;
- `Análise de Valor de Fronteira`;
- `Teste Baseado em Requisitos`.

Evitar casos duplicados. Manter casos semelhantes somente quando acrescentarem cobertura relevante.

O resultado esperado deve descrever somente o comportamento diretamente determinado pelos requisitos liberados.

Quando uma entrada violar uma regra mínima explícita, é permitido afirmar que ela não deve ser aceita. Não acrescentar mensagens, efeitos colaterais, persistência do valor anterior ou outros comportamentos que não tenham sido declarados.

Casos que utilizam a mesma entrada não são duplicados quando verificam requisitos principais diferentes, como mudança de estado, regra de fronteira e mensagem de conclusão.

## Rastreabilidade

Relacionar cada caso a exatamente um requisito liberado.

Copiar em `requisito_relacionado` o texto exato do requisito correspondente, considerando o valor após o processamento do JSON.

Um caso pode utilizar regras de outros requisitos liberados para construir uma entrada executável, mas deve manter um único requisito principal em `requisito_relacionado`.

Usar IDs sequenciais:
- `CT-001`;
- `CT-002`;
- `CT-003`.

## Entradas

O campo `entrada` deve ser uma lista com pelo menos um objeto.

Cada objeto deve possuir:

- `campo`;
- `valor`;
- `quantidade_caracteres`.

Usar valores concretos derivados dos requisitos. Não usar expressões vagas como “dados válidos”, “senha válida” ou “preenchimento correto”.

Quando a quantidade de caracteres for relevante, informar sua contagem exata.

O tamanho informado deve ser igual a `len(valor)`. Aspas da representação JSON não fazem parte do valor.

Quando a quantidade não for relevante, usar:

```json
"quantidade_caracteres": null
```

Não retornar `entrada: []` para um caso executável.

## Restrições

Não:

- presumir ou inventar requisitos;
- criar autenticação, perfis, permissões, telas ou etapas não informadas;
- inventar limites, formatos, mensagens ou pré-condições;
- gerar casos para requisitos não liberados;
- gerar análise de testabilidade;
- gerar lacunas ou sugestões;
- calcular status geral;
- gerar BDD;
- utilizar Dado, Quando e Então;
- incluir explicações fora do JSON.

## Formato de saída

Retornar somente um JSON válido com esta estrutura:

```json
{
  "casos_de_teste": [
    {
      "id": "CT-001",
      "titulo": "",
      "tipo": "POSITIVO",
      "requisito_relacionado": "",
      "tecnica": "",
      "entrada": [
        {
          "campo": "",
          "valor": "",
          "quantidade_caracteres": null
        }
      ],
      "resultado_esperado": ""
    }
  ]
}
```

O campo `tipo` deve possuir somente um destes valores:

- `POSITIVO`;
- `NEGATIVO`;
- `FRONTEIRA`.

## Integridade do JSON

A resposta deve ser processável diretamente por `json.loads()` e validável por `PlanoDeTestes.model_validate()`.

Retornar valores numéricos como números, booleanos como booleanos e ausência de quantidade como `null`.

Preservar a acentuação da língua portuguesa.

Quando houver aspas duplas dentro de valores textuais, representá-las com `\u0022`.

Não utilizar Markdown, crases ou explicações na resposta final.

Antes de responder, conferir:

- sintaxe JSON;
- IDs sequenciais e únicos;
- tipos permitidos;
- requisito relacionado;
- entrada não vazia;
- contagem exata de caracteres;
- resultado esperado derivado do requisito.