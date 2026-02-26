Trigger de deploy vazio

Este arquivo foi criado para forçar um redeploy quando for feito commit/push.

O que este patch faz:
- adiciona configuração explícita em `frontend/vercel.json` para usar `@vercel/static-build` com `dist` como output
- adiciona `engines.node: 18.x` em `frontend/package.json` e o script `vercel-build`

Instruções:
1. Commit e push das alterações para o repositório remoto.
2. Na Vercel, no projeto, forçar um redeploy do último commit (ou aguardar o CI disparar).

Se preferir, você pode commitar apenas este arquivo para um "deploy vazio" se quiser apenas acionar um redeploy sem outras mudanças.

Timestamp: 2026-02-25
