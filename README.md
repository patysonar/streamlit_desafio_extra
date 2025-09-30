# streamlit_desafio_extra

# 🤖 Agente Autônomo de EDA - Análise Exploratória de Dados

## 📋 Descrição

Agente inteligente capaz de realizar análise exploratória de dados (EDA) em qualquer arquivo CSV, respondendo perguntas em linguagem natural e gerando visualizações automáticas.

Desenvolvido para a disciplina **Agentes Autônomos - Atividade Extra**.

## ✨ Funcionalidades

- ✅ Upload de qualquer arquivo CSV
- ✅ Detecção automática de tipos de dados
- ✅ Estatísticas descritivas completas
- ✅ Geração automática de gráficos (histogramas, boxplots, heatmaps)
- ✅ Detecção de outliers (IQR e Isolation Forest)
- ✅ Análise de correlação
- ✅ Clustering (KMeans)
- ✅ Processamento de perguntas em linguagem natural
- ✅ Sistema de memória (histórico de análises)
- ✅ Geração automática de relatório PDF

## 🚀 Instalação e Execução

### Requisitos
- Python 3.10+
- pip

### Passo a Passo

1. **Clone ou baixe os arquivos do projeto**

2. **Crie um ambiente virtual (opcional, mas recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute o aplicativo**
```bash
streamlit run app_streamlit.py
```

5. **Acesse no navegador**
- Automaticamente abrirá em: http://localhost:8501

## 📁 Estrutura do Projeto

```
agent_project/
├── app_streamlit.py          # Interface web (Streamlit)
├── agent_core.py             # Lógica do agente (EDA, plots, memória)
├── generate_report.py        # Gerador de relatório PDF
├── requirements.txt          # Dependências Python
├── memory.json               # Histórico de análises (gerado automaticamente)
├── outputs/                  # Gráficos e PDFs gerados
│   ├── hist_*.png
│   ├── correlation_heatmap.png
│   └── *.pdf
└── README.md                 # Este arquivo
```

## 💬 Exemplos de Perguntas

O agente responde perguntas como:

- "Quais são os tipos de dados?"
- "Mostre a distribuição de Amount"
- "Qual o intervalo das variáveis numéricas?"
- "Quais são as medidas de tendência central?"
- "Existe correlação entre as variáveis?"
- "Detecte outliers nos dados"
- "Qual a taxa de fraude?"
- "Quais são as conclusões do agente?"

## 📊 Exemplo de Uso (Dataset Credit Card Fraud)

1. Faça upload do arquivo `creditcard.csv`
2. Pergunte: "Qual a taxa de fraude?"
   - Resposta: 0.1727% (492 fraudes em 284,807 transações)
3. Pergunte: "Mostre correlação com Class"
   - Gera heatmap automático
   - Identifica top 10 variáveis correlacionadas

## 🔧 Gerar Relatório PDF

Para gerar o relatório final:

```bash
python generate_report.py
```

Isso criará o arquivo:
```
Agentes Autônomos – Relatório da Atividade Extra.pdf
```

**Importante**: Execute primeiro o app Streamlit e faça algumas análises para que os gráficos sejam incluídos no PDF.

## 🌐 Deploy (Streamlit Cloud)

### Opção 1: Streamlit Cloud (Recomendado)

1. Crie um repositório no GitHub com todos os arquivos
2. Acesse https://share.streamlit.io
3. Clique em "New app"
4. Conecte seu repositório GitHub
5. Selecione `app_streamlit.py` como main file
6. Clique em "Deploy"
7. Aguarde ~2 minutos
8. URL gerada: `https://appdesafioextragit-crsb6wy8rt4nkp9znqtubg.streamlit.app/`

## 🧠 Sistema de Memória

O agente mantém histórico de todas as análises em `memory.json`:

- Pergunta realizada
- Resumo da resposta
- Timestamp
- Artefatos gerados (gráficos)

Isso permite que o agente:
- Fundamente conclusões baseadas em análises anteriores
- Responda "Quais conclusões você tirou?"
- Mantenha contexto entre sessões

## 🔒 Segurança

- Nenhuma chave API incluída
- Processamento local
- Dados não são enviados para serviços externos
- Caso use APIs futuras: armazenar chaves em variáveis de ambiente

## 📦 Dependências Principais

- `streamlit`: Interface web
- `pandas`: Manipulação de dados
- `numpy`: Computação numérica
- `matplotlib`: Visualização
- `seaborn`: Gráficos estatísticos
- `scikit-learn`: Machine learning (clustering, outliers)
- `fpdf`: Geração de PDF

## 🎯 Características Técnicas

### Detecção Automática de Tipos
- Numérico
- Categórico
- Temporal
- Texto

### Estatísticas Calculadas
- Média, mediana, moda
- Desvio padrão, variância
- Mínimo, máximo, quartis
- Contagem de valores únicos
- Valores faltantes

### Detecção de Outliers
- **IQR (Interquartile Range)**: método estatístico clássico
- **Isolation Forest**: detecção multivariada

### Visualizações
- Histogramas
- Boxplots
- Scatter matrix
- Heatmap de correlação

## 🐛 Solução de Problemas

### Erro: "streamlit command not found"
```bash
pip install streamlit
# ou
python -m pip install streamlit
```

### Erro ao gerar PDF
```bash
pip install fpdf
```

### Gráficos não aparecem no PDF
1. Execute o app Streamlit
2. Faça upload do CSV
3. Gere os gráficos usando as ferramentas
4. Execute novamente `python generate_report.py`

## 📧 Contato e Entrega

**E-mail de entrega**: challenges@i2a2.academy

**Assunto**: Agentes Autônomos – Atividade Extra

**Anexar**:
- PDF do relatório
- Códigos-fonte (.py)
- Link para teste online

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais.

## 🙏 Agradecimentos

---

**Desenvolvido com ❤️ para o curso de Agentes Autônomos**
