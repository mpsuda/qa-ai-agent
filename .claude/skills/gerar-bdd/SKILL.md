---
name: gerar-bdd
description: Converte casos de teste aprovados pelo QA em cenários BDD estruturados e rastreáveis. Use quando houver solicitação para gerar ou converter casos de teste em BDD, inclusive para verificar se o gate dos casos autoriza a geração. Não use para analisar requisitos, decidir testabilidade, gerar casos de teste ou aprovar o BDD.
---

# Gerar BDD

## Objetivo

Converter exclusivamente casos de teste aprovados pelo QA em cenários BDD rastreáveis, sem adicionar requisitos, regras, mensagens ou comportamentos.

## Autorização obrigatória

Gerar BDD somente quando a entrada:

- contiver `CASOS_APROVADOS_PELO_QA` e `LIBERADOS_PARA_GERACAO_DE_BDD`; ou
- declarar explicitamente que os casos fornecidos foram aprovados e liberados pelo QA para geração de BDD.

A lista dos casos aprovados deve estar presente na mesma solicitação.

Uma indicação de rejeição ou bloqueio prevalece sobre qualquer indicação de aprovação.

Não gerar BDD quando:

- não houver aprovação explícita do QA;
- houver `CASOS_REJEITADOS_PELO_QA`;
- houver `GERAÇÃO_DE_BDD_BLOQUEADA`;
- não houver casos de teste;
- os casos fornecidos não permitirem identificar seus IDs, entradas ou resultados esperados.

Nessas situações, retornar somente:

```text
GERAÇÃO_DE_BDD_BLOQUEADA
```

Não aprovar casos de teste por conta própria.

## Processo

1. Verificar a autorização explícita do gate.
2. Considerar somente os casos de teste aprovados fornecidos.
3. Preservar a ordem dos casos recebidos.
4. Gerar exatamente um cenário BDD para cada caso aprovado.
5. Relacionar cada cenário ao ID exato do caso correspondente.
6. Converter contexto, ação e resultado em `dado`, `quando` e `entao`.
7. Validar a cobertura, a rastreabilidade e a estrutura.
8. Quando autorizado, retornar somente o JSON; quando bloqueado, retornar somente `GERAÇÃO_DE_BDD_BLOQUEADA`.

## Conversão para BDD

Utilizar somente as informações existentes no caso de teste aprovado:

- título;
- requisito relacionado;
- entrada;
- resultado esperado.

Usar `dado` somente para representar contexto, condição ou estado inicial derivado do título, do requisito relacionado ou do caso aprovado.

Não colocar em `dado` ações como informar, enviar, clicar, salvar, concluir, solicitar ou alterar.

Usar `quando` para representar a ação ou evento executado, incluindo os valores concretos da entrada e suas quantidades quando forem relevantes.

Não deslocar uma entrada para `dado` apenas para preencher esse campo. A entrada utilizada na execução deve aparecer em `quando`.

Usar `entao` somente para representar o resultado observável definido em `resultado_esperado`.

Não colocar ações de execução em `entao` nem antecipar resultados em `dado` ou `quando`.

Quando não houver uma pré-condição detalhada, utilizar somente um contexto neutro derivado da capacidade descrita no próprio caso, sem inventar autenticação, tela, permissão ou estado externo.

Não adicionar contexto, pré-condição, ação ou resultado que não possa ser derivado diretamente do caso aprovado.

Preservar valores, quantidades, limites e mensagens exatamente como aparecem nos casos aprovados.

Permitir somente adaptações gramaticais mínimas necessárias para converter o conteúdo em passos BDD, sem alterar o significado, os valores ou o comportamento esperado.

Não corrigir, ampliar ou reinterpretar silenciosamente os casos aprovados.

Se um caso aprovado não puder ser convertido sem inventar informações, retornar somente:

```text
GERAÇÃO_DE_BDD_BLOQUEADA
```

## Estrutura dos passos

Os campos `dado`, `quando` e `entao` devem ser listas com pelo menos uma string não vazia.

Não iniciar as strings com as palavras-chave `Dado`, `Quando`, `Então` ou `E`. O código Python adicionará essas palavras ao exibir os cenários.

Exemplo:

```json
"dado": [
  "que o cliente possui uma senha cadastrada"
],
"quando": [
  "o cliente informa a nova senha \u0022Abc12345\u0022 com 8 caracteres"
],
"entao": [
  "o sistema aceita a nova senha"
]
```

Quando houver mais de uma condição, ação ou resultado explicitamente disponível, utilizar itens adicionais na lista correspondente.

## Rastreabilidade

Gerar exatamente um cenário para cada caso de teste aprovado.

Não gerar cenários adicionais.

Não omitir casos aprovados.

Não converter o mesmo caso mais de uma vez.

Copiar em `caso_teste_id` o ID exato do caso aprovado.

Criar um título não vazio, derivado do título do caso aprovado e sem ampliar seu comportamento.

Se os casos aprovados possuírem IDs ausentes ou duplicados, retornar somente `GERAÇÃO_DE_BDD_BLOQUEADA`.

Usar IDs BDD sequenciais e únicos, seguindo a ordem dos casos:

- `BDD-001`;
- `BDD-002`;
- `BDD-003`.

A quantidade de cenários deve ser igual à quantidade de casos aprovados.

O conjunto de valores de `caso_teste_id` deve ser exatamente igual ao conjunto de IDs dos casos aprovados.

## Restrições

Não:

- gerar BDD sem aprovação do QA;
- criar requisitos ou regras;
- inventar mensagens;
- inventar autenticação, perfis, permissões, telas ou integrações;
- alterar valores de entrada;
- alterar quantidades de caracteres;
- alterar o significado ou o conteúdo verificável dos resultados esperados;
- criar casos de teste adicionais;
- omitir casos aprovados;
- duplicar a conversão de um caso;
- realizar nova análise de testabilidade;
- calcular status geral;
- aprovar ou rejeitar o BDD;
- incluir explicações junto ao JSON.

## Formato de saída autorizado

Quando a geração estiver autorizada, retornar somente um JSON válido:

```json
{
  "cenarios_bdd": [
    {
      "id": "BDD-001",
      "caso_teste_id": "CT-001",
      "titulo": "",
      "dado": [
        ""
      ],
      "quando": [
        ""
      ],
      "entao": [
        ""
      ]
    }
  ]
}
```

Não retornar `cenarios_bdd` vazio, pois `PlanoBDD` exige pelo menos um cenário.

## Integridade do JSON

A resposta autorizada deve ser processável diretamente por `json.loads()` e validável por `PlanoBDD.model_validate()`.

Preservar a acentuação da língua portuguesa.

Quando houver aspas duplas dentro dos valores textuais, representá-las com `\u0022`.

Não utilizar Markdown, crases ou explicações na resposta autorizada.

Antes de responder, conferir:

- sintaxe JSON;
- IDs BDD sequenciais e únicos;
- `caso_teste_id` existente e não duplicado;
- um cenário para cada caso aprovado;
- listas `dado`, `quando` e `entao` não vazias;
- ausência das palavras-chave BDD no início das strings;
- valores de entrada preservados;
- resultados esperados preservados;
- ausência de informações inventadas;
- `dado` contém apenas contexto ou estado inicial;
- `quando` contém a ação e os valores concretos da entrada;
- `entao` contém somente o resultado esperado.