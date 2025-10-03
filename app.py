import datetime
import holidays
import os
from flask import Flask, render_template, request, session, jsonify
import pycountry, gettext

# Inicializa a aplicação Flask
app = Flask(__name__)

# É necessário uma chave secreta para usar sessões no Flask.
# Em um ambiente de produção, use um valor seguro e não o exponha no código.
app.secret_key = os.urandom(24)

# --- Lógica de Cálculo (reutilizada do script original) ---
HORAS_UTEIS_POR_DIA = 8

def calcular_horas_uteis(pais, estado=None):
    """
    Calcula o total de horas úteis usando a biblioteca 'holidays' para mais precisão.
    """
    hoje = datetime.date.today()
    primeiro_dia_do_mes = hoje.replace(day=1)
    
    # Garante que o estado seja None se for uma string vazia
    if not estado:
        estado = None

    # Inicializa o objeto de feriados para o local especificado
    try:
        feriados_locais = holidays.country_holidays(pais, subdiv=estado)
    except NotImplementedError:
        # Retorna um erro amigável se o país/estado não for encontrado
        return None, f"País '{pais}' ou estado '{estado}' não encontrado na biblioteca de feriados."

    total_horas_uteis = 0
    dia_atual = primeiro_dia_do_mes
    
    while dia_atual <= hoje:
        e_dia_de_semana = dia_atual.weekday() < 5
        nao_e_feriado = dia_atual not in feriados_locais
        
        if e_dia_de_semana and nao_e_feriado:
            total_horas_uteis += HORAS_UTEIS_POR_DIA
        
        dia_atual += datetime.timedelta(days=1)
        
    return total_horas_uteis, None

# --- Rotas da Aplicação Web ---

@app.route('/')
def index():
    """Renderiza a página inicial com o formulário."""
    # Recupera os últimos valores da sessão, se existirem
    ultimo_pais = session.get('pais', '')
    ultimo_estado = session.get('estado', '')

    # Configura o gettext para buscar as traduções para português do pycountry
    try:
        pt_translation = gettext.translation(
            'iso3166-1', pycountry.LOCALES_DIR, languages=['pt']
        )
        _ = pt_translation.gettext
    except FileNotFoundError:
        # Fallback caso o arquivo de tradução não seja encontrado
        _ = lambda s: s

    # 1. Pega os códigos de países suportados pela biblioteca 'holidays'.
    codigos_suportados = holidays.list_supported_countries(include_aliases=False).keys()

    paises_disponiveis = []
    for codigo in codigos_suportados:
        try:
            # 2. Usa pycountry para buscar o objeto do país e traduz o nome.
            pais_obj = pycountry.countries.get(alpha_2=codigo)
            if pais_obj:
                paises_disponiveis.append((codigo, _(pais_obj.name)))
            else:
                # Fallback para códigos não padrão (ex: "ECB" para Banco Central Europeu).
                paises_disponiveis.append((codigo, codigo))
        except (KeyError, AttributeError):
            # Fallback caso algo dê errado na busca.
            paises_disponiveis.append((codigo, codigo))

    # 3. Ordena a lista final pelo nome do país.
    paises_disponiveis.sort(key=lambda item: item[1])

    return render_template('index.html', 
                           paises=paises_disponiveis, 
                           pais_selecionado=ultimo_pais, estado_selecionado=ultimo_estado)

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    """
    Recebe os dados do formulário (POST) ou da URL (GET), 
    calcula e mostra o resultado.
    """
    if request.method == 'POST':
        # Dados vindos do formulário
        pais = request.form.get('pais', '').upper()
        estado = request.form.get('estado', '').upper()
    else: # GET
        # Dados vindos dos parâmetros da URL (ex: /calculate?pais=BR&estado=SP)
        pais = request.args.get('pais', '').upper()
        estado = request.args.get('estado', '').upper()

    # Validação para garantir que o país foi fornecido
    if not pais:
        return render_template('result.html', erro="O parâmetro 'pais' é obrigatório para o cálculo.")
    
    # Armazena os valores na sessão para a próxima visita
    session['pais'] = pais
    session['estado'] = estado

    horas, erro = calcular_horas_uteis(pais, estado)

    localidade = pais
    if estado:
        localidade += f"-{estado}"

    return render_template('result.html', horas=horas, localidade=localidade, erro=erro)

@app.route('/api/states/<country_code>')
def get_states(country_code):
    """Endpoint da API para obter os estados de um país."""
    country_code_upper = country_code.upper()
    try:
        # Acessa o dicionário de países. O valor pode ser a classe do país ou já a lista de subdivisões.
        country_data = holidays.list_supported_countries(include_aliases=True).get(country_code_upper)

        # Log para depuração: imprime o que foi encontrado no console do Flask
        print(f"[DEBUG] País: {country_code_upper}, Dados encontrados: {country_data}")
    
        # Caso 1: Os dados retornados já são a lista de subdivisões (ex: para 'BR')
        if isinstance(country_data, list):
            return jsonify(sorted(country_data))

        # Caso 2: Os dados são a classe do país, que contém o atributo 'subdivisions' (ex: para 'US')
        if country_data and hasattr(country_data, 'subdivisions'):
            # Retorna a lista de estados em formato JSON, ordenada.
            return jsonify(sorted(country_data.subdivisions))
        
        return jsonify([])
    except Exception as e:
        # Em caso de erro, retorna uma lista vazia para não quebrar o frontend.
        print(f"[ERROR] Erro ao buscar estados para {country_code_upper}: {e}")
        return jsonify([])

# Bloco para executar a aplicação em modo de desenvolvimento (debug)
if __name__ == '__main__':
    # O debug=True ativa o recarregamento automático ao salvar alterações no código.
    app.run(debug=True)