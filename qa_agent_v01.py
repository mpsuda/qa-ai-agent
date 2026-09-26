import os

from dotenv import load_dotenv
from anthropic import Anthropic


load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


user_story = """
O cliente pode alterar a senha cadastrada.
A senha deve possuir 8 ou mais caracteres.

O cliente pode alterar o endereço cadastrado.
"""


prompt = f"""
Você é um QA Analyst.

Analise a User Story abaixo.

USER STORY:
{user_story}

Siga obrigatoriamente estas etapas:

1. Identifique os requisitos confirmados explicitamente na User Story.
2. Identifique cenários positivos sustentados pelos requisitos.
3. Identifique cenários negativos que devem ser barrados pelos requisitos.
4. Identifique formatos ou valores válidos quando houver informação suficiente.
5. Identifique o que precisa ser confirmado porque não está definido.
6. Apresente sugestões da IA separadamente dos requisitos confirmados.

REGRAS IMPORTANTES:

- Não presuma requisitos que não estejam definidos.
- Não transforme sugestões em requisitos.
- Quando uma informação não estiver definida, informe que precisa ser esclarecida.
- Não gere cenários BDD nesta etapa.
- Não invente regras de negócio.

TÉCNICAS DE TESTE:

Quando existir uma regra de limite mínimo ou máximo:

- Identifique o limite explicitamente definido.
- Considere o valor imediatamente abaixo do limite.
- Considere o próprio limite.
- Considere o valor imediatamente acima do limite.
- Não invente limites que não estejam definidos.
- Explique quando um valor não puder ser considerado sem uma regra adicional.

Quando apresentar sugestões:
- não transformar sugestões em requisitos;
- não definir valores, limites ou parâmetros de negócio que não estejam especificados;
- se mencionar exemplos hipotéticos, identificá-los explicitamente como exemplos;
- preferir recomendações qualitativas quando o valor exato depende do negócio.

GERAÇÃO DE CASOS DE TESTE:

Após identificar os requisitos confirmados, crie casos de teste somente para
comportamentos que estejam sustentados pelos requisitos.

Para cada caso de teste informe:

- ID
- Tipo: Positivo ou Negativo
- Cenário
- Dados de entrada
- Resultado esperado

Regras:

- Não criar casos para requisitos que não estejam confirmados.
- Não utilizar sugestões da IA como base para casos de teste.
- Não utilizar lacunas como base para casos de teste.
- Aplicar análise de valor de fronteira quando houver limites definidos.
- Para um limite mínimo, considerar pelo menos:
  - valor imediatamente abaixo;
  - valor limite;
  - valor imediatamente acima.
- Não gerar BDD nesta etapa.

GATE DE TESTABILIDADE:

Antes de gerar casos de teste detalhados, avalie cada User Story
individualmente.

Classifique cada User Story como:

READY_FOR_TESTING
ou
NEEDS_CLARIFICATION

Use READY_FOR_TESTING somente quando existirem informações suficientes
para determinar comportamentos esperados de teste.

Use NEEDS_CLARIFICATION quando houver lacunas que impeçam determinar
com segurança os comportamentos esperados.

Quando uma User Story estiver como NEEDS_CLARIFICATION:

- não criar casos de teste detalhados para as regras que dependem das
  informações ausentes;
- não inventar regras;
- não inventar formatos;
- não inventar valores;
- apresentar as perguntas que precisam ser respondidas;
- separar claramente os requisitos que já estão confirmados das
  informações que ainda precisam ser definidas.

Uma User Story com NEEDS_CLARIFICATION não deve bloquear a análise de
outras User Stories que estejam READY_FOR_TESTING.

Regra de completude: a análise deve concluir todas as seções obrigatórias para todas as funcionalidades identificadas na User Story. 
Nunca interromper uma seção no meio. Caso o limite de saída seja insuficiente, priorizar a conclusão estruturada da análise antes de adicionar explicações adicionais.

Organize a resposta exatamente nestas seções:

STATUS

REQUISITOS CONFIRMADOS

CENÁRIOS POSITIVOS

CENÁRIOS NEGATIVOS

FORMATOS / VALORES VÁLIDOS

TÉCNICAS DE TESTE

CASOS DE TESTE

STATUS POR USER STORY

Para cada User Story analisada, informe:

- Identificador da User Story
- STATUS
- Justificativa resumida

LACUNAS / PERGUNTAS

SUGESTÕES DA IA

BDD
"""


message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=3000,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)


for block in message.content:
    if block.type == "text":
        print(block.text)