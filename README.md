# Instruções de Uso

Este repositório contém scripts para manipulação e execução de mapas, utilizando os arquivos `map.py` (principal) e `main.py` (executor).

## Estrutura do Repositório

```
├── data/        # Dados de entrada
├── maps/        # Dados finais de mapas gerados
├── map.py       # Código principal de manipulação de mapas
├── main.py      # Script executor
└── README.md
```

## Pré-requisitos

- Python 3.x instalado
- Instale as dependências necessárias (se houver) com:
    ```bash
    pip install -r requirements.txt
    ```

## Como Executar

1. Coloque seus dados de entrada na pasta `data/`.
2. Execute o script principal:
     ```bash
     python main.py
     ```
3. Os mapas gerados estarão disponíveis na pasta `maps/`.

## Observações

- Modifique `map.py` para alterar a lógica de manipulação dos mapas.
- Consulte os comentários nos scripts para mais detalhes de uso.
