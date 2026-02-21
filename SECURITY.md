# Validações de Segurança - Ecommerce LIFE

## ✅ Implementações de Segurança

### 1. Rate Limiting
- **Geral**: 180 requisições/minuto por IP
- **Sensível** (/admin, /checkout): 60 requisições/minuto por IP
- Proteção contra DDoS e brute force

### 2. Headers de Segurança
- `X-Content-Type-Options: nosniff` - Previne MIME sniffing
- `X-Frame-Options: DENY` - Previne clickjacking
- `X-XSS-Protection: 1; mode=block` - Proteção XSS
- `Strict-Transport-Security` - Force HTTPS
- `Content-Security-Policy` - Restringe recursos
- `Referrer-Policy` - Controla referrer
- `Permissions-Policy` - Desabilita APIs sensíveis

### 3. CORS Configurado
- Origins permitidas via variável de ambiente
- Credentials habilitado apenas para origins confiáveis
- Max age de 3600s para preflight cache

### 4. Validações de Entrada
- **Produtos**: Validação de slug (max 100 chars)
- **Frete**: Validação de CEP (8 dígitos), peso (0-100kg), subtotal positivo
- **Checkout**: Validação de email, valor (0-50000), parcelas (1-12)
- **Admin**: Validação de token não-nulo

### 5. Proteção de Dados Sensíveis
- Docs desabilitados em produção (`/docs`, `/redoc`)
- Detalhes de erro ocultos em produção
- Token admin via header customizado

### 6. Códigos HTTP Corretos
- `400 BAD_REQUEST` - Validação falhou
- `401 UNAUTHORIZED` - Token inválido
- `404 NOT_FOUND` - Recurso não encontrado
- `429 TOO_MANY_REQUESTS` - Rate limit excedido
- `500 INTERNAL_SERVER_ERROR` - Erro interno

## 🔐 Configuração Obrigatória

### Gerar Token Seguro
```bash
cd backend
python generate_token.py
```

### Atualizar .env
```env
AUTH_TOKEN=<token_gerado>
ENVIRONMENT=production
ALLOWED_ORIGINS=https://seudominio.com
```

## ⚠️ Próximas Etapas Críticas

1. **HTTPS Obrigatório** - Configure certificado SSL/TLS
2. **WAF** - Web Application Firewall (Cloudflare, AWS WAF)
3. **Autenticação JWT** - Substituir token simples por JWT com refresh
4. **Banco de Dados** - PostgreSQL com prepared statements
5. **Logs Estruturados** - Sentry, CloudWatch, ELK
6. **Backup Automático** - Dados e configurações
7. **Testes de Penetração** - OWASP ZAP, Burp Suite
8. **Secrets Manager** - AWS Secrets Manager, HashiCorp Vault
9. **2FA Admin** - Autenticação de dois fatores
10. **Auditoria** - Log de todas ações administrativas

## 🛡️ Checklist OWASP Top 10 (2021)

- [x] A01:2021 – Broken Access Control (rate limit, validação token)
- [x] A02:2021 – Cryptographic Failures (HSTS, headers seguros)
- [x] A03:2021 – Injection (validação de entrada, Pydantic)
- [x] A04:2021 – Insecure Design (rate limit por rota)
- [x] A05:2021 – Security Misconfiguration (docs desabilitados em prod)
- [ ] A06:2021 – Vulnerable Components (manter deps atualizadas)
- [x] A07:2021 – Identification/Authentication (token admin)
- [ ] A08:2021 – Software/Data Integrity (implementar assinatura)
- [x] A09:2021 – Security Logging (request ID, response time)
- [x] A10:2021 – SSRF (validação de entrada)

## 📊 Monitoramento

### Métricas Críticas
- Taxa de requisições por endpoint
- Latência (X-Response-Time-Ms)
- Taxa de erro 4xx/5xx
- Tentativas de acesso admin falhadas
- Rate limit triggers

### Alertas Recomendados
- > 100 requisições/min de um IP
- > 10 tentativas admin falhadas/hora
- Latência > 2000ms
- Taxa de erro > 5%
