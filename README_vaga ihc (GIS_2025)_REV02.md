
# 🧭 Desafio Técnico IHC – Especialista em Python e Geoprocessamento (GIS)

Este repositório contém os arquivos de apoio para o desafio técnico.  

O objetivo é gerar um **mapa interativo em HTML (offline)** a partir de um conjunto de dados ambientais fornecido em formato CSV.

---

## 📂 Estrutura de arquivos

```
.
├── data/
│   └── dados_exemplo_poluentes_no_acentos.csv   # Arquivo de entrada
├── maps/
│   └── mapa.html                                # Saída esperada (gerada pelo candidato)
├── src/
│   └── map.py                                   # Script principal a ser desenvolvido
├── requirements.txt                             # Dependências para instalação via pip
├── pyproject.toml                               # Dependências para instalação via Poetry
└── README.md
```

---

## 📑 Dados de entrada

O arquivo `dados_exemplo_poluentes_no_acentos.csv` contém:

- **station_id** → Identificador da estação  
- **station_name** → Nome da estação (sem acentuação)  
- **lat, lon** → Coordenadas em WGS84 (EPSG:4326)  
- **sample_dt** → Data da coleta (YYYY-MM-DD)  
- **pol_a, pol_b** → Concentrações de dois poluentes (mg/L)  
- **unit** → Unidade das concentrações (mg/L)  

Exemplo:

```csv
station_id,station_name,lat,lon,sample_dt,pol_a,pol_b,unit
101,Estacao A1,-22.901,-43.172,2025-08-01,4.0,0.9,mg/L
205,Estacao B1,-22.512,-43.737,2025-07-15,0.7,2.6,mg/L
...
```

---

## 🎯 Objetivo

Gerar `maps/mapa.html` com:

1. **Camada de concentração (mini-barras)**  
   - Cada estação representada por um ícone customizado (SVG/DivIcon) com duas barras coloridas (pol_a e pol_b).  
   - Tooltip no hover exibindo informações da estação e valores.  

2. **Camada de heatmap**  
   - Heatmap de pol_a (ou pol_b se preferir, mas justifique).  

3. **Controle de camadas**  
   - Permitir ligar/desligar a camada de concentração e a camada de heatmap.  

### Parte 2 – Bônus (opcional)

- Clusterização com ícone de mini-barras mostrando as **medianas** de pol_a e pol_b.  
- Tooltip do cluster com número de pontos, medianas e intervalo de datas.  
- Outros extras úteis (responsividade, exportação em GeoJSON, destaques visuais).

   ```

## 📦 Dependências sugeridas

### requirements.txt
```txt
folium==0.16.0
pandas==2.2.2
numpy==1.26.4
branca==0.7.2
geopandas==1.0.1
```

### pyproject.toml (Poetry)
```toml
[tool.poetry]
name = "desafio-mapas"
version = "0.1.0"
description = "Desafio técnico: Especialista em Python e Geoprocessamento (GIS)"
authors = ["Seu nome e email"]
readme = "README.md"
packages = [{ include = "src" }]

[tool.poetry.dependencies]
python = ">=3.8,<3.12"
folium = "0.16.0"
pandas = "2.2.2"
numpy = "1.26.4"
branca = "0.7.2"
geopandas = "1.0.1"

---

## 📦 Entrega esperada

O(a) candidato(a) deve entregar:

- `src/map.py` → Script principal  
- `maps/mapa.html` → Arquivo HTML obrigatório para validação rápida do resultado 
- `README.md` → Instruções de uso  
- Dependências em `pyproject.toml` (Poetry) ou `requirements.txt`

## 📦 Forma de entrega

- Preferencial: repositório GitHub contendo todos os arquivos.
- Alternativa: arquivo ZIP com a mesma estrutura de pastas.
- ENVIAR resultados para o e-mail vagas@ihc.com.br
- PRAZO: 29/09/2025 as 12:00 (meio-dia)

---

## 🔎 Avaliação

- Funcionalidade essencial: mapa offline, barras embutidas, tooltips, heatmap  
- Qualidade visual e UX: clareza, legenda, organização, criatividade  
- Código e reprodutibilidade: clareza, README, dependências  
- Bônus: clusterização com medianas, extras úteis  


---
