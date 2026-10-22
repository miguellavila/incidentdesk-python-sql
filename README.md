# IncidentDesk — Registro de Incidentes de Segurança

Projeto educacional de **Python + SQLite + SQL + HTML/CSS** para registrar ocorrências, acompanhar o tratamento e exportar um relatório local visualmente organizado.

## Funcionalidades

- Cadastrar incidentes com título, severidade e notas.
- Alterar status: aberto, em investigação ou resolvido.
- Listar registros, com filtro por status.
- Armazenar dados em SQLite, com restrições de integridade.
- Exportar um relatório HTML com escapamento seguro de texto inserido pelo usuário.

## Executar

Python 3.10+; não requer bibliotecas externas.

    python incidentdesk.py add "Tentativas de login incomuns" --severity high --notes "Ambiente de laboratório"
    python incidentdesk.py list
    python incidentdesk.py status 1 investigating
    python incidentdesk.py export relatorio.html
    python -m unittest discover -s tests -v

O banco incidents.db é criado automaticamente na primeira execução. Para usar outro caminho, adicione --db caminho.db **antes** do subcomando.

## Tecnologias
Python, SQLite, SQL, HTML5, CSS3 e unittest.

**Privacidade:** use apenas informações de laboratório ou dados que você tenha permissão para armazenar. A ferramenta é local, não inclui autenticação nem pretende substituir uma plataforma de resposta a incidentes.
