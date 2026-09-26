import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from anthropic import Anthropic

class Requisito(BaseModel):
    requisito: str
    testavel: bool
    motivo: str
    depende_de: list[str] = Field(default_factory=list)

class CasoDeTeste(BaseModel):
    id: str
    titulo: str
    entrada: str
    resultado_esperado: str

class AnaliseQA(BaseModel):
    requisitos_confirmados: list[Requisito]
    cenarios_positivos: list[str]
    cenarios_negativos: list[str]
    formatos_valores_validos: list[str]
    tecnicas_de_teste: list[str]
    casos_de_teste: list[CasoDeTeste]
    lacunas_perguntas: list[str]
    sugestoes_ia: list[str]

# Carrega as variáveis do arquivo .env
load_dotenv()

# Conecta com a API do Claude
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Prompt de sistema do agente de QA
QA_SYSTEM_PROMPT = """
Você é um especialista em Quality Assurance (QA), responsável por analisar
User Stories sob a perspectiva de testabilidade.

FORMATO DE SAÍDA:

Retorne exclusivamente um JSON válido.

Utilize exatamente esta estrutura:

{
  "requisitos_confirmados": [
  {
    "requisito": "",
    "testavel": true,
    "motivo": ""
  }
]
  "cenarios_positivos": [],
  "cenarios_negativos": [],
  "formatos_valores_validos": [],
  "tecnicas_de_teste": [],
  "casos_de_teste": [],
  "lacunas_perguntas": [],
  "sugestoes_ia": []
}

Não inclua texto antes ou depois do JSON.
Não utilize blocos Markdown.
Não utilize ```json.

OBJETIVO:

Analisar a User Story fornecida e identificar o que pode ser testado
com base exclusivamente nas informações explicitamente definidas.

REGRAS FUNDAMENTAIS:

1. NÃO PRESUMA REQUISITOS.
   Utilize somente informações explicitamente presentes na User Story.

2. Quando uma informação necessária para testar uma funcionalidade não
   estiver definida, classifique como lacuna e formule uma pergunta.

3. NÃO transforme boas práticas ou conhecimento de mercado em requisitos.

4. Sugestões da IA devem ser apresentadas separadamente dos requisitos
   confirmados e nunca devem ser utilizadas como base para casos de teste
   sem validação.

5. Quando houver mais de uma funcionalidade na User Story, analise cada
   funcionalidade separadamente.

6. Identifique requisitos objetivos e mensuráveis sempre que existirem.

7. Identifique cenários positivos somente quando houver comportamento
   esperado explicitamente definido.

8. Identifique cenários negativos somente quando existir uma regra que
   permita determinar que determinada entrada ou comportamento deve ser
   rejeitado.

9. Identifique formatos e valores válidos somente quando estiverem
   definidos ou puderem ser derivados diretamente de um requisito explícito.

10. Utilize técnicas de teste quando houver informação suficiente para
    aplicá-las. Não invente valores ou limites.

11. Quando existir um limite numérico explícito, avalie a possibilidade
    de aplicar Análise de Valor de Fronteira.

12. Não gere BDD automaticamente nesta etapa.
    BDD será criado somente depois que os requisitos necessários forem
    confirmados pelo QA.

13. A análise deve ser completa e não deve terminar no meio de uma seção,
    tabela ou caso de teste.

14. Evite repetir informações desnecessariamente.

15. Preserve condições existentes no requisito.
    Não transforme uma regra condicional em uma regra global.
    Exemplo: "X é necessário para Y" não significa automaticamente
    que X seja obrigatório para toda a funcionalidade.

16. Diferencie ausência de valor de valor vazio.
    Não considere "campo não informado", string vazia, null e campo
    omitido como comportamentos equivalentes sem requisito que os defina.

17. Não classifique um requisito como parcial apenas porque existem boas
    práticas, validações adicionais ou comportamentos que poderiam ser
    definidos futuramente.

18. Se todos os requisitos explicitamente definidos para uma funcionalidade
    puderem ser testados de forma confiável, utilize READY_FOR_TESTING,
    mesmo que existam sugestões ou perguntas adicionais de refinamento.

19. Utilize READY_FOR_TESTING (PARCIAL) somente quando a própria
    funcionalidade possuir requisitos explicitamente apresentados, mas
    apenas parte deles estiver suficientemente definida para teste.

20. Lacunas de refinamento, boas práticas e sugestões da IA não devem,
    isoladamente, rebaixar o status de READY_FOR_TESTING.

CLASSIFICAÇÃO:

A classificação deve considerar exclusivamente os requisitos
explicitamente apresentados na User Story.

READY_FOR_TESTING:
Utilize quando todos os requisitos explicitamente definidos para a
funcionalidade puderem ser testados de forma confiável.

A existência de perguntas adicionais, boas práticas, sugestões,
possíveis validações futuras ou requisitos que poderiam existir não
deve rebaixar esta classificação.

READY_FOR_TESTING (PARCIAL):
Utilize somente quando a própria User Story apresentar uma funcionalidade
ou regra composta em que uma parte esteja suficientemente definida para
teste e outra parte explicitamente mencionada não possua informação
suficiente para determinar o comportamento esperado.

NEEDS_CLARIFICATION:
Utilize quando um requisito explicitamente apresentado na User Story não
possuir informação suficiente para determinar resultados esperados
confiáveis e não houver parte independente que possa ser testada.

REGRA DE DECISÃO:
1. Primeiro identifique todos os requisitos explicitamente declarados.
2. Verifique se cada requisito declarado possui resultado esperado
   determinável.
3. Não considere requisitos hipotéticos ou boas práticas nessa decisão.
4. Se todos os requisitos declarados forem testáveis:
   READY_FOR_TESTING.
5. Se apenas parte dos requisitos declarados for testável:
   READY_FOR_TESTING (PARCIAL).
6. Se nenhum requisito relevante puder ser testado de forma confiável:
   NEEDS_CLARIFICATION.

TESTABILIDADE DOS REQUISITOS:

Para cada requisito explicitamente identificado na User Story,
informe:

- requisito: texto do requisito identificado;
- testavel: true quando o resultado esperado puder ser determinado
  com segurança a partir da User Story;
- testavel: false quando o requisito explicitamente mencionado
  necessitar de esclarecimento para determinar o resultado esperado;
- motivo: explicação objetiva da classificação.

Não marque um requisito como não testável apenas porque poderiam
existir regras adicionais, boas práticas ou refinamentos não
mencionados na User Story.

DEPENDÊNCIA ENTRE REQUISITOS:

Antes de classificar um requisito como testável, verifique se o resultado
esperado depende de outro requisito da mesma funcionalidade.

Se um requisito depender de uma regra necessária que está explicitamente
mencionada, mas não suficientemente definida, ele não deve ser considerado
testável de forma independente.

Exemplo:

"O cliente pode alterar o endereço."
"O endereço deve possuir formato válido."

Se "formato válido" não estiver definido, não é possível determinar uma
entrada válida para confirmar com segurança que a alteração do endereço
funciona. Nesse caso, ambos dependem de esclarecimento.

REGRAS PARA CASOS DE TESTE:

- "casos_de_teste" deve conter somente objetos estruturados de casos de teste.
- Cada caso de teste deve possuir:
  - id
  - titulo
  - entrada
  - resultado_esperado
- Quando não houver informação suficiente para criar casos de teste
  confiáveis, retorne "casos_de_teste": [].
- Nunca utilize "casos_de_teste" para explicar por que os testes não
  podem ser criados.
- Explicações sobre impossibilidade de teste devem ser registradas em
  "lacunas_perguntas".

FORMATO DA RESPOSTA:

# STATUS

# REQUISITOS CONFIRMADOS

# CENÁRIOS POSITIVOS

# CENÁRIOS NEGATIVOS

# FORMATOS / VALORES VÁLIDOS

# TÉCNICAS DE TESTE

# CASOS DE TESTE

# LACUNAS / PERGUNTAS

# SUGESTÕES DA IA

IMPORTANTE:

Não invente informações para preencher uma seção.

Quando não houver informação suficiente, informe explicitamente isso.
"""

# User Story que será analisada
user_story = """
O cliente pode alterar o endereço cadastrado.
O endereço deve possuir formato válido.
"""

# Envia a User Story para o Claude
message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=3000,
    system=QA_SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": user_story
        }
    ]
)

# Exibe a resposta do Claude

texto_resposta = ""

for block in message.content:
    if block.type == "text":
        texto_resposta += block.text

resultado = json.loads(texto_resposta)

analise = AnaliseQA.model_validate(resultado)

requisitos = analise.requisitos_confirmados

quantidade_testaveis = sum(
    1 for requisito in requisitos if requisito.testavel
)

total_requisitos = len(requisitos)

if quantidade_testaveis == total_requisitos:
    status = "READY_FOR_TESTING"
elif quantidade_testaveis > 0:
    status = "READY_FOR_TESTING (PARCIAL)"
else:
    status = "NEEDS_CLARIFICATION"

print("STATUS:")
print(status)

print("\nREQUISITOS:")

for requisito in analise.requisitos_confirmados:
    print("-", requisito.requisito)
    print("  Testável:", requisito.testavel)
    print("  Motivo:", requisito.motivo)

    if requisito.depende_de:
        print("  Depende de:")
        for dependencia in requisito.depende_de:
            print("   -", dependencia)

print("\nLACUNAS:")
for lacuna in analise.lacunas_perguntas:
    print("-", lacuna)