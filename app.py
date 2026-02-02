import datetime
import holidays
import os
from flask import Flask, render_template, request, session, jsonify
import pycountry, gettext, calendar

# Inicializa a aplicação Flask
app = Flask(__name__)

# É necessário uma chave secreta para usar sessões no Flask.
# Em um ambiente de produção, use um valor seguro e não o exponha no código.
app.secret_key = os.urandom(24)

# --- Lógica de Cálculo (reutilizada do script original) ---
HORAS_UTEIS_POR_DIA = 8

def calcular_horas_uteis(ano, mes, pais, estado=None, dias_de_ferias=None):
    """
    Calcula o total de horas úteis para um mês e ano específicos.
    """
    try:
        data_inicio = datetime.date(ano, mes, 1)
        _, ultimo_dia = calendar.monthrange(ano, mes)
        data_fim = datetime.date(ano, mes, ultimo_dia)
    except ValueError:
        return None, f"Data inválida: Ano={ano}, Mês={mes}."

    ferias_no_mes = dias_de_ferias or []
    
    # Garante que o estado seja None se for uma string vazia
    if not estado:
        estado = None

    try:
        # Passa o ano para a biblioteca de feriados para garantir a precisão
        feriados_locais = holidays.country_holidays(pais, subdiv=estado, years=ano)
    except NotImplementedError:
        return None, f"País '{pais}' ou estado '{estado}' não encontrado na biblioteca de feriados."

    total_horas_uteis = 0
    dia_atual = data_inicio
    
    while dia_atual <= data_fim:
        e_dia_de_semana = dia_atual.weekday() < 5
        nao_e_ferias = dia_atual not in ferias_no_mes
        nao_e_feriado = dia_atual not in feriados_locais
        
        if e_dia_de_semana and nao_e_feriado and nao_e_ferias:
            total_horas_uteis += HORAS_UTEIS_POR_DIA
        
        dia_atual += datetime.timedelta(days=1)
        
    return total_horas_uteis, None

# --- Rotas da Aplicação Web ---

@app.route('/')
def index():
    """Renderiza a página inicial com o formulário."""
    hoje = datetime.date.today()
    # Recupera os últimos valores da sessão, se existirem
    ultimo_pais = session.get('pais', '')
    ultimo_estado = session.get('estado', '')
    ultimas_ferias = session.get('ferias', '')
    # Define o padrão para o ano/mês atual se não estiver na sessão
    ultimo_ano = session.get('ano', hoje.year)
    ultimo_mes = session.get('mes', hoje.month)

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

    # Gera a lista de anos para o dropdown (ex: 2020 até o ano atual + 1)
    anos_disponiveis = list(range(2020, hoje.year + 2))

    return render_template('index.html', 
                           paises=paises_disponiveis,
                           anos=anos_disponiveis,
                           meses=list(range(1, 13)),
                           pais_selecionado=ultimo_pais,
                           estado_selecionado=ultimo_estado,
                           ferias_selecionadas=ultimas_ferias,
                           ano_selecionado=ultimo_ano,
                           mes_selecionado=ultimo_mes)

@app.route('/calculate')
def calculate():
    """
    Recebe os dados da URL (GET), calcula as horas de um mês inteiro e mostra o resultado.
    """
    pais = request.args.get('pais', '').upper()
    estado = request.args.get('estado', '').upper()
    ferias_str = request.args.get('ferias', '')
    hoje = datetime.date.today()
    try:
        ano = int(request.args.get('ano', hoje.year))
        mes = int(request.args.get('mes', hoje.month))
    except (ValueError, TypeError):
        return render_template('result.html', erro="Ano e Mês devem ser números válidos.")

    # Validação para garantir que o país foi fornecido
    if not pais:
        return render_template('result.html', erro="O parâmetro 'país' é obrigatório para o cálculo.")
    
    dias_de_ferias = []
    if ferias_str:
        try:
            hoje = datetime.date.today()
            # Converte a string "10,11,22" em uma lista de objetos date
            dias_int = [int(dia.strip()) for dia in ferias_str.split(',')]
            dias_de_ferias = [datetime.date(ano, mes, dia) for dia in dias_int]
        except (ValueError, TypeError):
            return render_template('result.html', erro="Formato inválido para dias de férias. Use números separados por vírgula (ex: 10,15,22).")

    # Armazena os valores na sessão para a próxima visita
    session['pais'] = pais
    session['estado'] = estado
    session['ferias'] = ferias_str
    session['ano'] = ano
    session['mes'] = mes

    horas, erro = calcular_horas_uteis(ano, mes, pais, estado, dias_de_ferias)

    localidade = pais
    if estado:
        localidade += f"-{estado}"
    
    periodo_str = f"{mes:02d}/{ano}"

    return render_template('result.html', 
                           horas=horas, localidade=localidade, erro=erro,
                           dias_ferias=ferias_str, periodo=periodo_str)

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