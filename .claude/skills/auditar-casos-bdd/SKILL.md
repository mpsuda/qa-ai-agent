---
name: auditar-casos-bdd
description: Audita casos de teste em relação aos requisitos liberados e cenários BDD em relação aos casos aprovados, verificando cobertura, rastreabilidade, duplicidade, coerência, dados incorretos, informações inventadas e semântica BDD. Use para revisar artefatos gerados antes da aprovação humana ou do próximo gate. Não use para gerar, corrigir ou aprovar casos de teste ou BDD.
---

# Auditar casos e BDD

## Objetivo

Auditar semanticamente artefatos de QA antes da decisão do QA humano.

Executar somente um tipo de auditoria por solicitação:

- `CASOS_DE_TESTE`: comparar requisitos liberados com casos gerados;
- `BDD`: comparar casos aprovados com cenários BDD gerados.

A auditoria identifica problemas, mas não aprova, rejeita, corrige ou regenera artefatos.

## Responsabilidades

A Skill deve:

1. verificar a cobertura dos itens de origem;
2. verificar a rastreabilidade entre origem e artefato;
3. identificar duplicidades;
4. identificar contradições internas;
5. identificar valores ou contagens objetivamente incorretos;
6. identificar informações não fornecidas pela origem;
7. verificar a separação semântica entre `dado`, `quando` e `entao`;
8. retornar um diagnóstico estruturado.

A validação de tipos, campos obrigatórios e estrutura do modelo pertence ao Python e ao Pydantic.

## Entrada para auditoria de casos de teste

Para `CASOS_DE_TESTE`, a solicitação deve conter:

- indicação explícita do tipo de auditoria;
- lista dos requisitos liberados pelo gate;
- lista dos casos de teste gerados.

Considerar os requisitos liberados como única fonte autorizada.

Não reavaliar a testabilidade dos requisitos.

Não incluir requisitos bloqueados, sugestões ou lacunas como fonte para geração de testes.

## Entrada para auditoria de BDD

Para `BDD`, a solicitação deve conter:

- indicação explícita do tipo de auditoria;
- lista dos casos de teste aprovados pelo QA;
- lista dos cenários BDD gerados.

Considerar os casos aprovados como única fonte autorizada.

Não reavaliar os requisitos nem os casos aprovados.

## Auditoria de casos de teste

Verificar:

- se cada requisito liberado possui pelo menos um caso relacionado;
- se cada caso aponta para exatamente um requisito liberado;
- se `requisito_relacionado` corresponde ao texto do requisito de origem;
- se existem IDs ausentes, repetidos ou referências inválidas;
- se existem casos semanticamente duplicados;
- se valores e quantidades informados estão corretos;
- se título, tipo, técnica, entrada e resultado esperado são coerentes;
- se o resultado esperado pode ser derivado do requisito;
- se foram inventadas mensagens, limites, regras ou pré-condições;
- se casos negativos possuem uma regra explícita que determine rejeição;
- se Análise de Valor de Fronteira foi aplicada somente a limites numéricos explícitos;
- se os valores de fronteira correspondem, quando aplicável, a `N - 1`, `N` e `N + 1`.

As técnicas permitidas são:

- `Análise de Valor de Fronteira`;
- `Particionamento de Equivalência`;
- `Teste Baseado em Requisitos`.

Não exigir todas as técnicas. Verificar somente se a técnica escolhida é aplicável ao caso.

## Auditoria de BDD

Verificar:

- se existe exatamente um cenário para cada caso aprovado;
- se nenhum caso aprovado foi omitido;
- se nenhum caso foi convertido mais de uma vez;
- se `caso_teste_id` corresponde a um caso aprovado existente;
- se os IDs BDD são únicos e sequenciais;
- se valores, quantidades e mensagens foram preservados;
- se o resultado esperado do caso foi preservado em `entao`;
- se `dado` contém somente contexto, condição ou estado inicial;
- se `quando` contém a ação ou o evento executado;
- se os valores concretos utilizados na execução aparecem em `quando`;
- se `entao` contém somente o resultado observável;
- se não foram inventadas autenticação, tela, perfil, permissão, integração ou outras informações;
- se as palavras `Dado`, `Quando`, `Então` e `E` não foram inseridas dentro das strings dos passos.

Não considerar uma reformulação textual como erro quando ela preservar integralmente o significado do caso aprovado.

## Categorias

Utilizar somente estas categorias:

- `COBERTURA`
- `RASTREABILIDADE`
- `DUPLICIDADE`
- `COERENCIA_INTERNA`
- `DADO_INCORRETO`
- `INFORMACAO_INVENTADA`
- `SEMANTICA_BDD`

### COBERTURA

Usar quando um item de origem não possuir o artefato correspondente.

Exemplos:

- requisito liberado sem caso de teste;
- caso aprovado sem cenário BDD;
- ausência da lista de origem ou da lista de artefatos necessária para executar a auditoria.

### RASTREABILIDADE

Usar quando o artefato não estiver corretamente relacionado à sua origem.

Exemplos:

- caso relacionado a requisito não liberado;
- texto de `requisito_relacionado` incompatível com a origem;
- cenário relacionado a `caso_teste_id` inexistente.

### DUPLICIDADE

Usar quando houver:

- IDs repetidos;
- casos semanticamente equivalentes sem cobertura adicional;
- mais de um cenário BDD para o mesmo caso aprovado.

### COERENCIA_INTERNA

Usar somente quando campos do próprio artefato se contradisserem.

Exemplos:

- título informa 8 caracteres, mas a entrada representa 7;
- tipo `NEGATIVO` com resultado esperado de aceitação;
- título, entrada e resultado esperado descrevem comportamentos diferentes.

### DADO_INCORRETO

Usar para erros objetivos em valores ou contagens.

Exemplos:

- `quantidade_caracteres` diferente de `len(valor)`;
- valor apresentado como `N - 1` sem corresponder a `N - 1`;
- mensagem ou valor alterado durante a conversão para BDD.

### INFORMACAO_INVENTADA

Usar quando o artefato acrescentar informação ausente da origem.

Exemplos:

- mensagem não declarada;
- limite não informado;
- autenticação, permissão ou tela não mencionada;
- política de senha não fornecida.

### SEMANTICA_BDD

Usar somente na auditoria de BDD quando houver uso incorreto dos passos.

Exemplos:

- ação colocada em `dado`;
- resultado antecipado em `quando`;
- ação de execução colocada em `entao`;
- entrada concreta deslocada para `dado` apenas para preencher o campo.

## Escolha da categoria

Registrar cada problema apenas uma vez.

Utilizar a categoria mais específica aplicável.

Aplicar estas prioridades:

1. `DADO_INCORRETO` para erro objetivo de valor ou contagem;
2. `INFORMACAO_INVENTADA` para conteúdo inexistente na origem;
3. `RASTREABILIDADE` para ligação inválida com a origem;
4. `COBERTURA` para item de origem não contemplado;
5. `DUPLICIDADE` para repetição;
6. `SEMANTICA_BDD` para posicionamento semântico incorreto;
7. `COERENCIA_INTERNA` para outras contradições entre campos.

Não registrar o mesmo problema em mais de uma categoria.

## Severidade

Utilizar somente:

- `BLOQUEANTE`
- `ALERTA`

Classificar como `BLOQUEANTE` quando o problema:

- impedir a rastreabilidade;
- deixar um item de origem sem cobertura;
- alterar uma regra, entrada ou resultado esperado;
- introduzir informação não autorizada;
- apresentar dado objetivo incorreto;
- causar perda ou alteração de significado no BDD;
- utilizar ID duplicado ou inexistente.

Classificar como `ALERTA` quando o artefato continuar executável e rastreável, mas apresentar:

- redação pouco clara;
- título que possa ser melhorado sem alterar o significado;
- redundância que não comprometa cobertura ou rastreabilidade;
- duplicidade sem impacto funcional, quando mantiver cobertura adicional justificável.

Alertas não bloqueiam o avanço para o próximo gate.

## Resultado da auditoria

Usar:

- `COM_BLOQUEIOS` quando existir pelo menos um problema `BLOQUEANTE`;
- `SEM_BLOQUEIOS` quando não existir problema bloqueante.

Uma auditoria com apenas alertas deve retornar `SEM_BLOQUEIOS`.

A Skill não deve retornar `APROVADO`, `REPROVADO`, `ACEITO` ou `REJEITADO`.

A decisão final pertence ao QA humano.

## Formato de saída

Retornar somente um JSON válido:

```json
{
  "tipo_auditoria": "CASOS_DE_TESTE",
  "resultado_auditoria": "SEM_BLOQUEIOS",
  "problemas": [
    {
      "severidade": "ALERTA",
      "categoria": "DUPLICIDADE",
      "artefato_id": "CT-004",
      "descricao": "O caso possui cobertura equivalente à do CT-002.",
      "referencia_origem": "A nova senha deve possuir 8 ou mais caracteres."
    }
  ],
  "resumo": {
    "itens_origem": 3,
    "itens_auditados": 5,
    "problemas_bloqueantes": 0,
    "alertas": 1
  }
}