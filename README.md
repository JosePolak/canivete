# 🛠️ Canivete Multiferramentas

Uma plataforma utilitária modular desenvolvida com **Python** e **Flask**, projetada para centralizar ferramentas do dia a dia. O projeto foca em uma interface limpa, responsiva e com processamento de dados em tempo real.

## 🚀 Módulo Atual: Cotador de Moedas
O primeiro módulo implementado é um conversor de moedas inteligente que consome dados da [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas).

### ✨ Principais Funcionalidades
* **Cotações em Tempo Real:** Monitoramento de USD, EUR e BTC diretamente no topo da página.
* **Conversor Dinâmico:** Suporte a múltiplas moedas com função de inversão rápida (Swap).
* **Localização PT-BR:** Tratamento completo de entradas e saídas com vírgula decimal e formatação brasileira via `locale`.
* **Persistência com SQLAlchemy:** Histórico das últimas 10 conversões armazenado em banco de dados SQLite.
* **Design Responsivo:** Interface adaptada para dispositivos móveis com menu hambúrguer e ocultação estratégica de elementos secundários em telas pequenas.

## 🛠️ Tecnologias Utilizadas
* **Backend:** Python 3.12 / Flask
* **Banco de Dados:** SQLAlchemy / SQLite
* **Frontend:** HTML5, CSS3 (Flexbox Moderno) e JavaScript Vanilla
* **Arquitetura:** Estrutura modular utilizando **Blueprints** para facilitar a escalabilidade.

## 📦 Como Executar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/JosePolak/canivete.git](https://github.com/JosePolak/canivete.git)
   cd canivete

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate

3. **Instale as dependências:**
   ```bash
   python app.py

4. **Acesse:**

   Clique em ctrl + http://127.0.0.1:5000

## 🗺️ Roadmap (próximos passos, não necessariamente na ordem apresentada)
O projeto "Canivete" será expandido com os seguintes módulos:
   [ ] Loterias: Consulta de resultados da Caixa e gerador de apostas.
   [ ] CEP: Busca de endereços via API.
   [ ] Medidas: Conversor de unidades (peso, comprimento, temperatura).
   [ ] IMC: Calculadora de Índice de Massa Corporal.

## 🎯 Objetivo do Projeto
Este projeto foi desenvolvido com foco estritamente didático e técnico. O objetivo central é a aplicação de boas práticas de desenvolvimento web, tais como:
* **Arquitetura Modular:** Organização de código escalável com Blueprints.
* **Consumo de APIs Externas:** Tratamento de requisições e dados dinâmicos.
* **UX/UI Reativa:** Criação de interfaces responsivas e intuitivas sem dependência de frameworks pesados de frontend.
* **Fullstack Development:** Integração completa entre lógica de servidor (Python) e persistência de dados (SQL).
