# Calculadora de Horas Úteis

Este projeto oferece uma ferramenta para calcular o total de horas úteis desde o primeiro dia do mês atual até a data de hoje, considerando feriados nacionais e estaduais.

Ele está disponível em duas versões:
1.  **Aplicação Web:** Uma interface amigável que roda no navegador.
2.  **Script de Linha de Comando:** Para uso direto no terminal.

## Funcionalidades

- Calcula o total de horas úteis em um intervalo de datas.
- Desconsidera fins de semana (sábados e domingos).
- Utiliza a biblioteca `holidays` para identificar feriados automaticamente, incluindo feriados móveis.

---

## Pré-requisitos

- Python 3.6 ou superior.

---

## Instalação e Configuração

Siga os passos abaixo para configurar o ambiente e rodar o projeto.

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd calculadora-horas
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Criar o ambiente
    python3 -m venv .venv

    # Ativar (macOS/Linux)
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Como Usar (2 Opções)

### Opção 1: Executar a Aplicação Web (Recomendado)

Com o ambiente virtual ativado, você pode iniciar o servidor de duas maneiras:

**A. Usando o comando `flask` (padrão):**

```bash
flask run
```

Abra seu navegador e acesse http://127.0.0.1:5000 para usar a calculadora.

### Opção 2: Usar o Script de Linha de Comando

O script `calcula_horas_uteis.py` é executado via terminal e aceita os seguintes parâmetros:

-   `--pais`: (Obrigatório) O código de duas letras do país (ex: `BR`, `US`, `PT`).
-   `--estado`: (Opcional) A sigla do estado/província para feriados locais (ex: `PE`, `SP`, `CA`).

**Exemplos:**

```bash
# Calcular horas úteis para Pernambuco, Brasil
python calcula_horas_uteis.py --pais BR --estado PE

# Calcular horas úteis considerando apenas feriados nacionais do Brasil
python calcula_horas_uteis.py --pais BR

# Ver as opções de ajuda
python calcula_horas_uteis.py --help
```

---

## (Avançado) Criando um Executável

Você pode empacotar o script em um único arquivo executável usando o PyInstaller. Isso permite que ele seja executado em máquinas que não possuem Python ou as dependências instaladas.

1.  **Execute o PyInstaller:**
    O comando abaixo inclui uma instrução específica (`--hidden-import`) para garantir que a biblioteca `holidays` seja corretamente incluída.

    ```bash
    pyinstaller --onefile --hidden-import="holidays.countries.brazil" calcula_horas_uteis.py
    ```

2.  **Encontre o executável:**
    O arquivo final estará na pasta `dist/`.