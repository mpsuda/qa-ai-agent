import os
import json
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv
from anthropic import Anthropic

class Requisito(BaseModel):
    requisito: str
    testavel: bool
    motivo: str
    depende_de: list[str] = Field(default_factory=list)

class DadoTeste(BaseModel):
    campo: str
    valor: str
    quantidade_caracteres: int | None = None

    @model_validator(mode="after")
    def validar_quantidade_caracteres(self):
        if self.quantidade_caracteres is None:
            return self

        quantidade_real = len(self.valor)

        if quantidade_real != self.quantidade_caracteres:
            raise ValueError(
                f"O valor '{self.valor}' possui "
                f"{quantidade_real} caracteres, mas a IA informou "
                f"{self.quantidade_caracteres}."
            )

        return self

class CasoDeTeste(BaseModel):
    id: str
    titulo: str
    tipo: Literal["POSITIVO", "NEGATIVO", "FRONTEIRA"]
    requisito_relacionado: str
    tecnica: str
    entrada: list[DadoTeste] = Field(min_length=1)
    resultado_esperado: str

class PlanoDeTestes(BaseModel):
    casos_de_teste: list[CasoDeTeste]

class CenarioBDD(BaseModel):
    id: str
    caso_teste_id: str
    titulo: str
    dado: list[str] = Field(min_length=1)
    quando: list[str] = Field(min_length=1)
    entao: list[str] = Field(min_length=1)

class PlanoBDD(BaseModel):
    cenarios_bdd: list[CenarioBDD] = Field(
        min_length=1
    )

class RevisaoBDD(BaseModel):
    bdd_aprovado: bool
    observacoes: str = ""

class AnaliseQA(BaseModel):
    requisitos_confirmados: list[Requisito]
    lacunas_perguntas: list[str]
    sugestoes_ia: list[str]

def carregar_json_da_ia(texto: str) -> dict:
    texto_limpo = texto.strip()

    if not texto_limpo:
        raise ValueError("A IA retornou uma resposta vazia.")

    linhas = texto_limpo.splitlines()

    if linhas and linhas[0].strip().startswith("```"):
        linhas = linhas[1:]

    if linhas and linhas[-1].strip() == "```":
        linhas = linhas[:-1]

    texto_limpo = "\n".join(linhas).strip()

    try:
        return json.loads(texto_limpo)

    except json.JSONDecodeError as erro:
        print("\nRESPOSTA INVÁLIDA RECEBIDA DA IA:")
        print(texto_limpo[:1000])

        raise ValueError(
            "A resposta da IA não contém um JSON válido."
        ) from erro

class RevisaoPlanoTestes(BaseModel):
    casos_aprovados: bool
    observacoes: str = ""

# Carrega as variáveis do arquivo .env
load_dotenv()

# Conecta com a API do Claude
api_key = os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    raise RuntimeError(
        "ANTHROPIC_API_KEY não encontrada. "
        "Verifique o arquivo .env."
    )

client = Anthropic(api_key=api_key)

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
      "motivo": "",
      "depende_de": []
    }
  ],
"lacunas_perguntas" deve ser uma lista de strings.
"sugestoes_ia" deve ser uma lista de strings.
Não utilize objetos dentro dessas listas.
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

FASE ATUAL: ANÁLISE DE TESTABILIDADE

Nesta etapa, NÃO gere:
- cenários de teste;
- técnicas de teste;
- casos de teste;
- BDD.

A finalidade desta etapa é somente:
1. identificar requisitos explicitamente definidos;
2. avaliar testabilidade de cada requisito;
3. identificar dependências;
4. identificar lacunas;
5. registrar sugestões separadamente.

Casos de teste e BDD serão gerados somente em etapas posteriores,
após revisão do QA.

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

TEST_GENERATION_PROMPT = """
Você é um especialista em Quality Assurance responsável por gerar
casos de teste a partir de requisitos previamente analisados,
revisados e liberados por um QA humano.

FASE ATUAL: GERAÇÃO DE CASOS DE TESTE

Retorne exclusivamente um JSON válido com esta estrutura:

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
    "campo": "nova_senha",
    "valor": "Abcd1234",
    "quantidade_caracteres": 8
  }
]
      "resultado_esperado": ""
    }
  ]
}

REGRAS:

1. Utilize exclusivamente os requisitos fornecidos.
2. Não presuma ou invente requisitos.
3. Cada caso deve estar relacionado a um requisito recebido.
4. Copie em "requisito_relacionado" o texto exato do requisito.
5. Utilize IDs sequenciais: CT-001, CT-002, CT-003.
6. O campo "tipo" deve possuir somente:
   - POSITIVO
   - NEGATIVO
   - FRONTEIRA
7. Casos negativos somente podem ser criados quando existir uma regra
   explícita que permita determinar que uma entrada deve ser rejeitada.
8. Análise de Valor de Fronteira somente pode ser utilizada quando
   existir um limite numérico explícito.
9. Não invente mensagens de erro.
10. Não gere BDD.
11. Não utilize Dado, Quando e Então.
12. Não inclua explicações antes ou depois do JSON.
13. Não utilize blocos Markdown.
14. Se não houver requisitos liberados, retorne:
    {"casos_de_teste": []}
15. Não invente pré-condições como autenticação, permissões, perfis,
    telas ou etapas que não estejam nos requisitos fornecidos.

16. Não utilize expressões vagas como "dados válidos", "senha válida"
    ou "preenchimento correto". Utilize valores concretos derivados
    dos requisitos explícitos.

17. Quando aplicar Análise de Valor de Fronteira a um limite mínimo N,
    considere, quando aplicável:
    - N - 1;
    - N;
    - N + 1.

18. Evite casos duplicados. Casos semelhantes só devem ser mantidos
    quando técnicas diferentes acrescentarem cobertura relevante.

19. Uma informação comum de mercado não deve ser tratada como requisito.
    Por exemplo, não presuma que o cliente esteja autenticado se isso
    não tiver sido informado.
20. O campo "entrada" deve ser uma lista de dados estruturados.

21. Quando um valor possuir quantidade de caracteres relevante para
    o teste, preencha "quantidade_caracteres" com a contagem exata.

22. O valor deve conter somente os caracteres efetivamente utilizados.
    Aspas usadas na representação do JSON não fazem parte do valor.

23. Quando a quantidade de caracteres não for relevante, utilize:
    "quantidade_caracteres": null
24. Todo caso de teste deve possuir pelo menos um item em "entrada".

25. Casos de fronteira devem informar o valor concreto utilizado e
    sua quantidade exata de caracteres.

26. Não retorne "entrada": [] para um caso de teste executável.
"""
BDD_GENERATION_PROMPT = """
FASE ATUAL: GERAÇÃO DE BDD

Transforme exclusivamente os casos de teste aprovados pelo QA em cenários BDD.

REGRAS:
- Gere um cenário BDD para cada caso de teste recebido.
- Preserve o ID do caso de teste em "caso_teste_id".
- Não crie novos requisitos, regras ou mensagens.
- Não presuma informações ausentes.
- Utilize somente os dados e resultados esperados dos casos aprovados.
- Os campos "dado", "quando" e "entao" devem ser listas de strings.
- Retorne somente JSON válido.
- Não utilize blocos Markdown.
- Não escreva explicações antes ou depois do JSON.

FORMATO OBRIGATÓRIO:

{
  "cenarios_bdd": [
    {
      "id": "BDD-001",
      "caso_teste_id": "CT-001",
      "titulo": "Título do cenário",
      "dado": [
        "contexto ou pré-condição disponível no caso de teste"
      ],
      "quando": [
        "ação executada"
      ],
      "entao": [
        "resultado esperado"
      ]
    }
  ]
}
"""

# User Story que será analisada
user_story = """
O cliente pode alterar a senha cadastrada.
A nova senha deve possuir 8 ou mais caracteres.
Ao concluir a alteração, o sistema deve exibir a mensagem:
"Senha alterada com sucesso."
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

resultado = carregar_json_da_ia(texto_resposta)

analise = AnaliseQA.model_validate(resultado)

requisitos = analise.requisitos_confirmados

quantidade_testaveis = sum(
    1 for requisito in requisitos if requisito.testavel
)

total_requisitos = len(requisitos)

if total_requisitos == 0:
    status = "NEEDS_CLARIFICATION"
elif quantidade_testaveis == total_requisitos:
    status = "READY_FOR_TESTING"
elif quantidade_testaveis > 0:
    status = "READY_FOR_TESTING (PARCIAL)"
else:
    status = "NEEDS_CLARIFICATION"

print("STATUS:")
print(status)

print("\nREQUISITOS:")

for requisito in analise.requisitos_confirmados:
    print(f"- {requisito.requisito}")
    print(f"  Testável: {requisito.testavel}")
    print(f"  Motivo: {requisito.motivo}")

    dependencias = (
        ", ".join(requisito.depende_de)
        if requisito.depende_de
        else "Nenhuma dependência registrada"
    )

    print(f"  Depende de: {dependencias}")

print("\nLACUNAS:")
for lacuna in analise.lacunas_perguntas:
    print("-", lacuna)

print("\nSUGESTÕES:")

if analise.sugestoes_ia:
    for sugestao in analise.sugestoes_ia:
        print(f"- {sugestao}")
else:
    print("- Nenhuma sugestão registrada.")

class RevisaoQA(BaseModel):
    diagnostico_aprovado: bool
    observacoes: str = ""


def solicitar_revisao_qa() -> RevisaoQA:
    print("\nREVISÃO DO QA")

    while True:
        resposta = input(
            "O diagnóstico da IA está correto? [S/N]: "
        ).strip().upper()

        if resposta in {"S", "N"}:
            break

        print("Resposta inválida. Digite S ou N.")

    observacoes = input(
        "Observações do QA, se houver: "
    ).strip()

    return RevisaoQA(
        diagnostico_aprovado=resposta == "S",
        observacoes=observacoes,
    )


def aplicar_gate_de_qualidade(
    status: str,
    analise: AnaliseQA,
    revisao: RevisaoQA,
) -> list[Requisito]:
    if not revisao.diagnostico_aprovado:
        print("\nGATE DE QUALIDADE:")
        print("ANÁLISE_REJEITADA_PELO_QA")
        print("A análise deverá ser revisada antes de continuar.")
        return []

    if status == "NEEDS_CLARIFICATION":
        print("\nGATE DE QUALIDADE:")
        print("DIAGNÓSTICO_APROVADO")
        print("GERAÇÃO_DE_TESTES_BLOQUEADA")
        print("Motivo: existem requisitos sem testabilidade suficiente.")
        return []

    if status == "READY_FOR_TESTING (PARCIAL)":
        requisitos_liberados = [
            requisito
            for requisito in analise.requisitos_confirmados
            if requisito.testavel
        ]

        print("\nGATE DE QUALIDADE:")
        print("GERAÇÃO_PARCIAL_AUTORIZADA")
        print(f"Requisitos liberados: {len(requisitos_liberados)}")

        for requisito in requisitos_liberados:
            print(f"- {requisito.requisito}")

        return requisitos_liberados

    print("\nGATE DE QUALIDADE:")
    print("GERAÇÃO_COMPLETA_AUTORIZADA")
    print(
        f"Requisitos liberados: "
        f"{len(analise.requisitos_confirmados)}"
    )

    for requisito in analise.requisitos_confirmados:
        print(f"- {requisito.requisito}")

    return analise.requisitos_confirmados

def gerar_plano_de_testes(
    requisitos_liberados: list[Requisito],
) -> PlanoDeTestes:
    if not requisitos_liberados:
        return PlanoDeTestes(casos_de_teste=[])

    requisitos_para_teste = [
        requisito.requisito
        for requisito in requisitos_liberados
    ]

    requisitos_json = json.dumps(
        requisitos_para_teste,
        ensure_ascii=False,
        indent=2,
    )

    message_testes = client.messages.create(
    model="claude-sonnet-5",
    thinking={"type": "disabled"},
    max_tokens=3000,
        system=TEST_GENERATION_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Gere casos de teste somente para os requisitos "
                    "liberados abaixo:\n\n"
                    f"{requisitos_json}"
                ),
            }
        ],
    )

    texto_testes = ""

    for block in message_testes.content:
        if block.type == "text":
            texto_testes += block.text

    if not texto_testes.strip():
        tipos_blocos = [
            block.type
            for block in message_testes.content
        ]

        raise ValueError(
            "A Fase 2 não retornou texto. "
            f"stop_reason={message_testes.stop_reason}; "
            f"blocos={tipos_blocos}"
        )

    resultado_testes = carregar_json_da_ia(texto_testes)

    return PlanoDeTestes.model_validate(resultado_testes)

def gerar_plano_bdd(plano_de_testes: PlanoDeTestes) -> PlanoBDD:
    casos_json = plano_de_testes.model_dump_json(indent=2)

    mensagem_bdd = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        thinking={"type": "disabled"},
        system=BDD_GENERATION_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Converta os casos de teste aprovados abaixo em BDD:\n\n"
                    + casos_json
                ),
            }
        ],
    )

    texto_bdd = ""

    for bloco in mensagem_bdd.content:
        if bloco.type == "text":
            texto_bdd += bloco.text

    resultado_bdd = carregar_json_da_ia(texto_bdd)
    plano_bdd = PlanoBDD.model_validate(resultado_bdd)

    ids_casos_aprovados = {
        caso.id for caso in plano_de_testes.casos_de_teste
    }

    ids_casos_convertidos = [
        cenario.caso_teste_id
        for cenario in plano_bdd.cenarios_bdd
    ]

    ids_desconhecidos = (
        set(ids_casos_convertidos) - ids_casos_aprovados
    )

    if ids_desconhecidos:
        raise ValueError(
            "O BDD referencia casos de teste não aprovados: "
            + ", ".join(sorted(ids_desconhecidos))
        )

    ids_duplicados = {
        caso_id
        for caso_id in ids_casos_convertidos
        if ids_casos_convertidos.count(caso_id) > 1
    }

    if ids_duplicados:
        raise ValueError(
            "Existem casos de teste convertidos mais de uma vez: "
            + ", ".join(sorted(ids_duplicados))
        )

    ids_nao_convertidos = (
        ids_casos_aprovados - set(ids_casos_convertidos)
    )

    if ids_nao_convertidos:
        raise ValueError(
            "Existem casos aprovados sem cenário BDD: "
            + ", ".join(sorted(ids_nao_convertidos))
        )

    return plano_bdd


def revisar_bdd() -> RevisaoBDD:
    print("\nREVISÃO DOS CENÁRIOS BDD")

    while True:
        resposta = input(
            "O QA aprova os cenários BDD? [S/N]: "
        ).strip().upper()

        if resposta in {"S", "N"}:
            break

        print("Resposta inválida. Digite S ou N.")

    observacoes = input(
        "Observações do QA, se houver: "
    ).strip()

    return RevisaoBDD(
        bdd_aprovado=resposta == "S",
        observacoes=observacoes,
    )


# A partir daqui começa o código principal

def solicitar_revisao_plano_testes() -> RevisaoPlanoTestes:
    print("\nREVISÃO DOS CASOS DE TESTE")

    while True:
        resposta = input(
            "O QA aprova os casos de teste? [S/N]: "
        ).strip().upper()

        if resposta in {"S", "N"}:
            break

        print("Resposta inválida. Digite S ou N.")

    observacoes = input(
        "Observações sobre os casos, se houver: "
    ).strip()

    return RevisaoPlanoTestes(
        casos_aprovados=resposta == "S",
        observacoes=observacoes,
    )

revisao_qa = solicitar_revisao_qa()

requisitos_liberados = aplicar_gate_de_qualidade(
    status=status,
    analise=analise,
    revisao=revisao_qa
)

if requisitos_liberados:
    plano_de_testes = gerar_plano_de_testes(
        requisitos_liberados
    )

    print("\nFASE 2 — CASOS DE TESTE:")

    for caso in plano_de_testes.casos_de_teste:
        print(f"\n{caso.id} — {caso.titulo}")
        print(f"  Tipo: {caso.tipo}")
        print(
            f"  Requisito relacionado: "
            f"{caso.requisito_relacionado}"
        )
        print(f"  Técnica: {caso.tecnica}")
        print("  Entrada:")

        for dado in caso.entrada:
            if dado.quantidade_caracteres is not None:
                print(
                    f"    - {dado.campo}: '{dado.valor}' "
                    f"({dado.quantidade_caracteres} caracteres)"
                )
            else:
                print(
                    f"    - {dado.campo}: '{dado.valor}'"
                )

        print(
            f"  Resultado esperado: "
            f"{caso.resultado_esperado}"
        )

    revisao_plano = solicitar_revisao_plano_testes()

    if revisao_plano.casos_aprovados:
        print("\nGATE DOS CASOS DE TESTE:")
        print("CASOS_APROVADOS_PELO_QA")
        print("LIBERADOS_PARA_GERACAO_DE_BDD")
    else:
        print("\nGATE DOS CASOS DE TESTE:")
        print("CASOS_REJEITADOS_PELO_QA")
        print("GERAÇÃO_DE_BDD_BLOQUEADA")

        if revisao_plano.observacoes:
            print(
                f"Observações: "
                f"{revisao_plano.observacoes}"
            )

else:
    print("\nFASE 2 NÃO EXECUTADA:")
    print("Nenhum requisito foi liberado pelo gate.")

if requisitos_liberados and revisao_plano.casos_aprovados:
    plano_bdd = gerar_plano_bdd(plano_de_testes)

    print("\nFASE 3 — CENÁRIOS BDD:")

    for cenario in plano_bdd.cenarios_bdd:
        print(f"\n{cenario.id} — {cenario.titulo}")
        print(f"  Caso de teste relacionado: {cenario.caso_teste_id}")

        for indice, passo in enumerate(cenario.dado):
            palavra_chave = "Dado" if indice == 0 else "E"
            print(f"  {palavra_chave} {passo}")

        for indice, passo in enumerate(cenario.quando):
            palavra_chave = "Quando" if indice == 0 else "E"
            print(f"  {palavra_chave} {passo}")

        for indice, passo in enumerate(cenario.entao):
            palavra_chave = "Então" if indice == 0 else "E"
            print(f"  {palavra_chave} {passo}")

    revisao_bdd = revisar_bdd()

    print("\nGATE FINAL DO BDD:")

    if revisao_bdd.bdd_aprovado:
        print("BDD_APROVADO_PELO_QA")
        print("WORKFLOW_QA_CONCLUIDO")
    else:
        print("BDD_REJEITADO_PELO_QA")
        print("WORKFLOW_QA_NAO_CONCLUIDO")

    if revisao_bdd.observacoes:
        print(f"Observações: {revisao_bdd.observacoes}")