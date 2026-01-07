# 🚚 Sistema de Delivery

<div align="center">

<p align="center">
  <img src="https://raw.githubusercontent.com/Kauanrodrigues01/Kauanrodrigues01/refs/heads/main/images/projetos/sistema-delivery/dashboard.png" alt="Sistema Delivery" width="800">
</p>

**Sistema de Delivery completo e moderno** desenvolvido com **Django 5.1**, projetado para automatizar todo o processo de vendas e entregas. Integra **pagamentos Mercado Pago**, **notificações WhatsApp automatizadas**, **WebSockets em tempo real**, **geração de relatórios em PDF** e um **painel administrativo avançado** com regras de negócio complexas.

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Django Channels](https://img.shields.io/badge/Django_Channels-092E20?style=for-the-badge&logo=django&logoColor=white)](https://channels.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 📋 Sobre o Projeto

Sistema completo de delivery desenvolvido para otimizar operações de vendas e entregas, com foco em automação, escalabilidade e experiência do usuário. Implementa arquitetura moderna com comunicação assíncrona, cache distribuído e processamento em background.

### 🎯 Principais Diferenciais

- 🔄 **Comunicação em Tempo Real** - WebSockets via Django Channels para atualizações instantâneas
- 🤖 **Automação Completa** - Notificações WhatsApp e emails automáticos baseados em eventos
- 📊 **Relatórios Inteligentes** - Geração automática de PDFs com WeasyPrint e agendamento via APScheduler
- 💳 **Múltiplos Métodos de Pagamento** - PIX, Cartão (Mercado Pago) e Dinheiro com troco
- 🚀 **Alta Performance** - Cache Redis, otimização de queries e compressão de assets
- 🐳 **Deploy Simplificado** - Containerização completa com Docker Compose

---

## ✨ Funcionalidades

### 🛍️ **E-commerce**
- Catálogo de produtos com categorias e imagens otimizadas (Cloudinary)
- Carrinho de compras persistente com sessões
- Sistema de busca e filtros avançados
- Checkout inteligente com validação de endereço e cálculo de frete

### 💰 **Pagamentos**
- Integração completa com Mercado Pago (PIX e Cartão)
- Webhook para confirmação automática de pagamentos
- Sistema de pagamento em dinheiro com cálculo de troco
- Controle de status de pagamento em tempo real

### 📱 **Notificações**
- WhatsApp via Evolution API para confirmações e atualizações
- Sistema de backup com CallMeBot
- Notificações em tempo real via WebSocket
- Templates personalizáveis de mensagens

### 🎛️ **Painel Administrativo**
- Dashboard com métricas e gráficos em tempo real
- CRUD completo para produtos, categorias e pedidos
- Gestão de clientes e histórico de pedidos
- Sistema de filtros avançados e exportação de dados
- Relatórios diários em PDF gerados automaticamente

### 📊 **Relatórios e Analytics**
- Geração automática de relatórios diários (PDF)
- Métricas de vendas, produtos mais vendidos e receita
- Exportação de dados em múltiplos formatos
- Agendamento de relatórios via APScheduler

### 🔐 **Segurança**
- Autenticação de usuários com permissões granulares
- Proteção CSRF e XSS
- Validação de webhooks com assinatura
- Logs estruturados e auditoria de ações

---

## 🛠️ Tecnologias

### **Backend**
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django Channels](https://img.shields.io/badge/Django_Channels-092E20?style=for-the-badge&logo=django&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)

### **Banco de Dados & Cache**
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

### **Frontend**
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Lucide Icons](https://img.shields.io/badge/Lucide_Icons-F56565?style=for-the-badge&logo=feather&logoColor=white)

### **Infraestrutura & DevOps**
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)
![WhiteNoise](https://img.shields.io/badge/WhiteNoise-499848?style=for-the-badge)

### **Integrações & APIs**
![Mercado Pago](https://img.shields.io/badge/Mercado_Pago-00B1EA?style=for-the-badge&logo=mercadopago&logoColor=white)
![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![WeasyPrint](https://img.shields.io/badge/WeasyPrint-FF6B6B?style=for-the-badge&logo=adobe-acrobat-reader&logoColor=white)

### **Ferramentas & Bibliotecas**
- **django-compressor** - Compressão de CSS/JS
- **django-redis** - Cache distribuído
- **django-apscheduler** - Agendamento de tarefas
- **WeasyPrint** - Geração de PDFs
- **Pillow** - Processamento de imagens
- **colorlog** - Logs coloridos e estruturados

### Frontend
* **HTML5/CSS3/JavaScript**: Interface responsiva nativa
* **Modal System**: Interfaces dinâmicas sem recarregar página
* **AJAX**: Verificação de status de pagamento em tempo real

---

## 🚀 Executando Localmente

### 🔧 Pré-requisitos

* Python 3.10+
* Poetry (gerenciador de dependências)
* PostgreSQL (opcional, usa SQLite por padrão)
* Evolution API configurada (para WhatsApp)
* Conta Mercado Pago (para pagamentos)

### 1. Clone o repositório

```bash
git clone https://github.com/Kauanrodrigues01/delivery-agua.git
cd delivery-agua
```

### 2. Instale as dependências

```bash
poetry install
```

### 3. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# Configurações Básicas
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui

# Banco de Dados
DATABASE_URL=sqlite:///db.sqlite3
# Para PostgreSQL: DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# WhatsApp Evolution API
EVOLUTION_API_BASE_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua-chave-da-evolution
INSTANCE_NAME=sua-instancia
WHATSAPP_ADMIN_NUMBER=5511999999999

# Mercado Pago
MP_ACCESS_TOKEN=seu-access-token-mp
NOTIFICATION_URL=https://seu-dominio.com/services/webhook/mercadopago/
BASE_APPLICATION_URL=https://seu-dominio.com

# Cloudinary (Opcional)
CLOUDINARY_CLOUD_NAME=seu-cloud-name
CLOUDINARY_API_KEY=sua-api-key
CLOUDINARY_API_SECRET=seu-api-secret

# CallMeBot (Backup WhatsApp)
CALLMEBOT_API_URL=https://api.callmebot.com/whatsapp.php
CALLMEBOT_API_KEY=sua-chave-callmebot
CALLMEBOT_PHONE_NUMBER=5511999999999
```

### 4. Execute as migrações e configure o banco

```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### 5. (Opcional) Carregue dados de exemplo

```bash
poetry run python manage.py mock_products
poetry run python manage.py mock_orders
```

### 6. Inicie o servidor

```bash
poetry run python manage.py runserver
```

### 🌐 Acesse:

* **Loja**: [http://localhost:8000](http://localhost:8000)
* **Admin Django**: [http://localhost:8000/admin](http://localhost:8000/admin)
* **Dashboard**: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)

---

## 🐳 Executando com Docker

### 📦 Produção (com Redis incluído)

O `docker-compose.yml` já inclui o Redis configurado automaticamente:

```bash
# Subir todos os containers (web + redis)
docker-compose up -d --build

# Executar migrações
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down
```

**Serviços incluídos:**
- 🌐 **web**: Aplicação Django (porta 8000)
- 🔴 **redis**: Cache e WebSockets (porta 6379)

### 🛠️ Desenvolvimento (com PostgreSQL + Redis)

Para ambiente de desenvolvimento completo:

```bash
# Subir PostgreSQL e Redis
docker-compose -f docker-compose-dev.yml up -d

# Configurar o .env para usar o PostgreSQL
DATABASE_URL=postgres://delivery_user:delivery_pass123@localhost:5432/delivery_agua_dev
REDIS_URL=redis://localhost:6379/1

# Executar aplicação localmente
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### ⚙️ Configuração do Redis

O Redis é usado para:
- ✅ **Cache**: Melhora performance de queries
- ✅ **WebSockets**: Dashboard em tempo real
- ✅ **Health Check**: Monitoramento da aplicação

**Variáveis de ambiente (opcional):**
```env
REDIS_PASSWORD=redis123           # Senha do Redis
REDIS_CONTAINER_NAME=delivery-redis
REDIS_HOST_PORT=6379              # Porta exposta no host
```

> **Nota**: Em desenvolvimento (DEBUG=True), o sistema usa cache em memória se o Redis não estiver disponível.

---

## 📊 Arquitetura do Sistema

### 🏗️ Estrutura de Apps Django

```
delivery-agua/
├── app/                    # Configurações principais do Django
├── cart/                   # Lógica do carrinho de compras
├── checkout/               # Processo de checkout e pedidos
├── core/                   # Funcionalidades centrais e comandos
├── dashboard/              # Painel administrativo avançado
├── products/               # Gestão de produtos e categorias
└── services/               # Integrações externas (WhatsApp, Mercado Pago)
```

### 🔄 Fluxo do Sistema

1. **Cliente navega** pelos produtos organizados por categorias
2. **Adiciona ao carrinho** com quantidades desejadas
3. **Checkout** com múltiplas opções de pagamento
4. **Processamento** automático via Mercado Pago (PIX/Cartão)
5. **Notificações** automáticas via WhatsApp para admin e cliente
6. **Gestão** completa no painel administrativo

### 💳 Sistema de Pagamentos

| Método | Processamento | Confirmação | Troco |
|--------|---------------|-------------|-------|
| **PIX** | Mercado Pago | Webhook automático | ❌ |
| **Cartão** | Mercado Pago | Webhook automático | ❌ |
| **Dinheiro** | Manual | Admin confirma | ✅ Calculado |

---

## 📱 Funcionalidades Principais

### 🛍️ E-commerce Frontend
- **Catálogo de produtos** com categorias e filtros
- **Carrinho persistente** com controle de quantidades
- **Checkout intuitivo** com validações em tempo real
- **Cálculo automático** de frete e troco
- **Interface responsiva** para todos os dispositivos

### 🎛️ Painel Administrativo
- **Dashboard** com métricas de vendas e pedidos
- **CRUD completo** para produtos e categorias
- **Gestão avançada de pedidos** com sistema de status duplo
- **Filtros e relatórios** personalizáveis
- **Interface modal** para ações rápidas

### 📊 Sistema de Status Inteligente

O sistema possui **duplo controle de status**:

#### Status Operacional
- 🟡 **Pending**: Pedido aguardando processamento
- 🟢 **Completed**: Pedido entregue
- 🔴 **Cancelled**: Pedido cancelado

#### Status de Pagamento
- 🟡 **Pending**: Pagamento pendente
- 🟢 **Paid**: Pagamento confirmado
- 🔴 **Cancelled**: Pagamento cancelado/devolvido

### 🔒 Regras de Negócio

- **Pedidos Finalizados** (`completed + paid`): Imutáveis para auditoria
- **Edição Limitada**: Pedidos pagos só permitem alterar dados básicos
- **Proteções Automáticas**: Validações que impedem operações inválidas
- **Estados Especiais**: Tratamento para devoluções e cancelamentos

---

## 📱 Integração WhatsApp

### 📤 Notificações Automáticas

#### Para o Admin (Novo Pedido)
```
🚨 NOVO PEDIDO RECEBIDO!

Cliente: João Silva
Telefone: (11) 99999-9999
Endereço: Rua das Flores, 123

Itens do pedido:
• Água Mineral 20L (x2)
• Água Mineral 5L (x1)

Total: R$ 45,00

Pagamento: PIX
Status: Pendente
```

#### Para o Cliente (Confirmação)
```
✅ Pedido Confirmado!

Olá João Silva, seu pedido foi confirmado com sucesso!

Resumo do pedido:
Total: R$ 45,00
Pagamento: PIX

Em breve entraremos em contato para combinar a entrega.

Obrigado pela preferência!
```

### 🔄 Updates de Status
- **Pagamento confirmado**: Notificação automática via webhook
- **Entrega realizada**: Notificação manual pelo admin
- **Problemas**: Notificações contextuais baseadas no status

---

## 🔗 API Endpoints

### 🔒 Endpoints Protegidos (Admin)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/dashboard/` | Painel principal com métricas |
| `GET/POST` | `/dashboard/produtos/` | CRUD de produtos |
| `GET/POST` | `/dashboard/categorias/` | CRUD de categorias |
| `GET/POST` | `/dashboard/pedidos/` | Gestão de pedidos |

### 🌐 Endpoints Públicos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Catálogo de produtos |
| `GET` | `/carrinho/` | Visualizar carrinho |
| `POST` | `/carrinho/adicionar/` | Adicionar ao carrinho |
| `GET/POST` | `/checkout/` | Processo de checkout |
| `GET` | `/checkout/aguardando-pagamento/` | Status do pagamento |

### 🔗 Webhooks

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/services/webhook/mercadopago/` | Atualizações de pagamento |
| `GET` | `/checkout/api/check-payment/` | Verificar status PIX |

---

## 🎯 Scripts Úteis

### 📋 Comandos de Desenvolvimento

```bash
# Servidor de desenvolvimento
poetry run python manage.py runserver

# Migrações
poetry run python manage.py makemigrations
poetry run python manage.py migrate

# Admin
poetry run python manage.py createsuperuser

# Dados de exemplo
poetry run python manage.py mock_products
poetry run python manage.py mock_orders

# Testes
poetry run python manage.py test

# Linting
poetry run ruff check .
poetry run ruff format .
```

### 🚀 Comandos de Produção

```bash
# Coletar arquivos estáticos
poetry run python manage.py collectstatic --noinput

# Verificar configurações
poetry run python manage.py check --deploy

# Shell Django
poetry run python manage.py shell
```

---

## 🔒 Segurança

### 🛡️ Proteções Implementadas
- **CSRF Protection**: Todos os formulários protegidos
- **SQL Injection**: Uso exclusivo do Django ORM
- **XSS Protection**: Templates com escape automático
- **Validações Server-Side**: Todas as entradas validadas
- **Webhook Security**: Verificação de assinatura Mercado Pago

### 🔐 Configurações de Produção
- **HTTPS Obrigatório**: `SECURE_SSL_REDIRECT = True`
- **Cookies Seguros**: `SESSION_COOKIE_SECURE = True`
- **Headers de Segurança**: Via WhiteNoise e Django
- **Debug Desabilitado**: `DEBUG = False` em produção

---

## 📈 Métricas e Performance

### ⚡ Otimizações Implementadas
- **Select Related**: Redução de queries N+1
- **Prefetch Related**: Carregamento eficiente de relacionamentos
- **Índices de Banco**: Campos de filtro otimizados
- **Cache de Templates**: Reutilização de componentes
- **Compressão de Assets**: Via WhiteNoise

### 📊 Métricas Disponíveis
- **Total de pedidos** por período
- **Receita** por método de pagamento
- **Status de entrega** em tempo real
- **Produtos mais vendidos**
- **Taxa de conversão** do carrinho

---

## 🧪 Testes

### 🔬 Coverage Atual
```bash
# Executar todos os testes
poetry run python manage.py test

# Com coverage
poetry run coverage run --source='.' manage.py test
poetry run coverage report
```

### 📋 Áreas Testadas
- ✅ Modelos de dados e validações
- ✅ Views e lógica de negócio
- ✅ Integração com APIs externas
- ✅ Sistema de pagamentos
- ✅ Notificações WhatsApp

---

## 🌍 Deploy em Produção

### 🚀 Variáveis de Ambiente (Produção)

```env
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
SECRET_KEY=sua-chave-super-secreta-e-longa

# URLs completas para webhooks
NOTIFICATION_URL=https://seu-dominio.com/services/webhook/mercadopago/
BASE_APPLICATION_URL=https://seu-dominio.com

# Cloudinary obrigatório em produção
CLOUDINARY_CLOUD_NAME=seu-cloud-name
CLOUDINARY_API_KEY=sua-api-key
CLOUDINARY_API_SECRET=seu-api-secret
```

### 📦 Deploy Sugerido
- **Heroku**: Procfile e configurações incluídas
- **DigitalOcean**: Docker Compose pronto
- **AWS**: EC2 + RDS + S3 via Cloudinary
- **VPS**: Nginx + uWSGI + PostgreSQL

---

## 💡 Futuras Melhorias

### 🔮 Roadmap Técnico
- 🔐 **Autenticação de clientes** com login/registro
- 📊 **Analytics avançado** com gráficos interativos
- 📱 **App móvel** React Native ou Flutter
- 🔔 **Push notifications** via Firebase
- 🌍 **Multi-tenant** para múltiplas empresas

### 🚀 Funcionalidades Planejadas
- 🗓️ **Agendamento de entregas** com calendário
- 📍 **Tracking GPS** em tempo real
- 💰 **Programa de fidelidade** com pontos
- 📧 **Email marketing** integrado
- 📋 **Relatórios PDF** automatizados

---

## 📝 Documentação Adicional

### 📚 Recursos Extras
- [📋 Regras de Negócio Detalhadas](./REGRAS_DE_NEGOCIO_PEDIDOS.md)
- [🐳 Docker Compose](./docker-compose.yml)
- [⚙️ Configurações](./pyproject.toml)

### 🔗 Links Úteis
- [Django Documentation](https://docs.djangoproject.com/)
- [Mercado Pago API](https://www.mercadopago.com.br/developers)
- [Evolution API](https://doc.evolution-api.com/)

---

## 🤝 Contribuindo

### 🐛 Reportar Bugs
1. Abra uma [issue](https://github.com/Kauanrodrigues01/delivery-agua/issues)
2. Descreva o problema detalhadamente
3. Inclua steps para reproduzir
4. Adicione screenshots se aplicável

### 💻 Contribuições de Código
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

<div align="center">

**Desenvolvido com ❤️ por [Kauan Rodrigues](https://github.com/Kauanrodrigues01)**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/kauanrodrigues01)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Kauanrodrigues01)
[![Portfolio](https://img.shields.io/badge/Portfolio-FF5722?style=for-the-badge&logo=google-chrome&logoColor=white)](https://portfolio-kauan-rodrigues.vercel.app)

</div>

---

<div align="center">

### ⭐ Se este projeto te ajudou, não esqueça de dar uma estrela!

![GitHub stars](https://img.shields.io/github/stars/Kauanrodrigues01/delivery-agua?style=social)
![GitHub forks](https://img.shields.io/github/forks/Kauanrodrigues01/delivery-agua?style=social)

</div>
