# 📦 Sistema de Gerenciamento de Estoque

Estudo de Caso - UNIFECAF

## Descrição

O **Controle de Estoque** é uma aplicação desenvolvida em Python que permite gerenciar de forma eficiente o estoque de produtos em uma empresa. Com uma interface gráfica intuitiva construída com Tkinter, a aplicação possibilita o cadastro, edição e movimentação de produtos, além de gerenciar usuários com diferentes níveis de acesso.

## 📌 Visão Geral

Aplicação desktop para controle completo de estoque com:

- ✅ Autenticação segura de usuários  
- ✅ Cadastro e gestão de produtos  
- ✅ Controle de movimentações (entradas/saídas)  
- ✅ Alertas de estoque baixo  
- ✅ Histórico detalhado de transações  

---

## 🛠️ Tecnologias Utilizadas

**Backend:**

- tkinter – Interface gráfica  
- sqlite3 – Banco de dados  
- bcrypt – Criptografia de senhas  

---

## 🎯 Funcionalidades

### 👨‍💻 Controle de Acesso

- Perfis:  
  - Administrador (acesso completo)  
  - Usuário comum (operações básicas)  
- Autenticação com senhas criptografadas

### 🗃️ Gerenciamento de Produtos

| Operação | Descrição                             |
|----------|----------------------------------------|
| Cadastro | Nome, quantidade atual e mínima        |
| Edição   | Atualização de todos os campos         |
| Exclusão | Remoção com confirmação                |

### 🔄 Movimentações

- Tipos de movimentação:  
  - **Entrada**: Adição ao estoque  
  - **Saída**: Remoção do estoque  
- Atualização automática dos níveis de estoque  

---

## ⚡ Como Executar

1. Clone o repositório:

   `git clone https://github.com/O-Alexsandro/unifecaf-controle-de-estoque.git`

   `cd controle-estoque`

2. Execute a aplicação:

   `python estoque.py`

3. Credenciais padrão:

   - Usuário: `admin`  
   - Senha: `admin123`  

---

## 🗂️ Estrutura do Banco de Dados

```
estoque.db
├── usuarios (id, username, password, perfil)
├── produtos (id, nome, quantidade, quantidade_minima)
└── movimentacoes (id, produto_id, tipo, quantidade, data, usuario)
```

## 👨‍💻 Autor

**Alexsandro Ribas**  

--- 
























