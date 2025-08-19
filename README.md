# Calculadora de Horas Úteis

Este é um script de linha de comando em Python que calcula o total de horas úteis desde o primeiro dia do mês atual até a data de hoje. Ele é flexível o suficiente para considerar feriados nacionais e estaduais de diversos países.

## Funcionalidades

- Calcula o total de horas úteis em um intervalo de datas.
- Desconsidera fins de semana (sábados e domingos).
- Utiliza a biblioteca `holidays` para identificar feriados automaticamente, incluindo feriados móveis.
- Aceita parâmetros de linha de comando para especificar o país e o estado, tornando-o adaptável a diferentes localidades.

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

## Como Usar

O script é executado via terminal e aceita os seguintes parâmetros:

- `--pais`: (Obrigatório) O código de duas letras do país (ex: `BR`, `US`, `PT`).
- `--estado`: (Opcional) A sigla do estado/província para feriados locais (ex: `PE`, `SP`, `CA`).

### Exemplos de Uso

*   **Calcular horas úteis para Pernambuco, Brasil:**
    ```bash
    python calcula_horas_uteis.py --pais BR --estado PE
    ```

*   **Calcular horas úteis considerando apenas feriados nacionais do Brasil:**
    ```bash
    python calcula_horas_uteis.py --pais BR
    ```

*   **Ver as opções de ajuda:**
    ```bash
    python calcula_horas_uteis.py --help
    ```

---

## Criando um Executável

Você pode empacotar o script em um único arquivo executável usando o PyInstaller. Isso permite que ele seja executado em máquinas que não possuem Python ou as dependências instaladas.

1.  **Execute o PyInstaller:**
    O comando abaixo inclui uma instrução específica (`--hidden-import`) para garantir que a biblioteca `holidays` seja corretamente incluída.

    ```bash
    pyinstaller --onefile --hidden-import="holidays.countries.brazil" calcula_horas_uteis.py
    ```

2.  **Encontre o executável:**
    O arquivo final estará na pasta `dist/`.

---

## Instalando como Ferramenta de Linha de Comando (macOS/Linux)

Para usar o `calcula_horas_uteis` como um comando global no seu terminal, siga estes passos:

1.  **Crie um diretório para executáveis locais (se não existir):**
    ```bash
    mkdir -p ~/.local/bin
    ```

2.  **Mova o executável para esse diretório:**
    ```bash
    mv dist/calcula_horas_uteis ~/.local/bin/
    ```

3.  **Adicione o diretório ao seu PATH:**
    Abra seu arquivo de configuração do shell (`~/.zshrc`, `~/.bash_profile`, etc.) e adicione a seguinte linha ao final:
    ```shell
    export PATH="$HOME/.local/bin:$PATH"
    ```
    Reinicie seu terminal ou execute `source ~/.zshrc` para aplicar as alterações.

4.  **Use em qualquer lugar:**
    Agora você pode chamar o comando de qualquer pasta.
    ```bash
    calcula_horas_uteis --pais BR --estado SP
    ```