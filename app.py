import datetime
import holidays
import os
from flask import Flask, render_template, request, session, jsonify
import pycountry, gettext, calendar
from core_calculator import calcular_horas_uteis as core_calcular_horas, parse_ferias

# Inicializa a aplicação Flask
app = Flask(__name__)

# É necessário uma chave secreta para usar sessões no Flask.
# Em um ambiente de produção, use um valor seguro e não o exponha no código.
app.secret_key = os.urandom(24)

# Cache para armazenar as listas de estados já processadas
_states_cache = {}

# --- Rotas da Aplicação Web ---

@app.route('/')
def index():
    """Renderiza a página inicial com o formulário."""
    hoje = datetime.date.today()
    # Recupera os últimos valores da sessão ou define 'BR' como padrão
    ultimo_pais = session.get('pais', 'BR')
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
    
    data_inicio = datetime.date(ano, mes, 1)
    try:
        if ano == hoje.year and mes == hoje.month:
            data_fim = hoje
        else:
            _, ultimo_dia = calendar.monthrange(ano, mes)
            data_fim = datetime.date(ano, mes, ultimo_dia)

        dias_de_ferias = parse_ferias(ferias_str, ano, mes)
        horas = core_calcular_horas(data_inicio, data_fim, pais, estado, dias_de_ferias)
        erro = None
    except (ValueError, NotImplementedError) as e:
        return render_template('result.html', erro=str(e))

    # Armazena os valores na sessão para a próxima visita
    session['pais'] = pais
    session['estado'] = estado
    session['ferias'] = ferias_str
    session['ano'] = ano
    session['mes'] = mes

    localidade = pais
    if estado:
        localidade += f"-{estado}"
    
    periodo_str = f"{mes:02d}/{ano}"

    return render_template('result.html', 
                           horas=horas, localidade=localidade, erro=erro,
                           dias_ferias=ferias_str, periodo=periodo_str)

@app.route('/api/states/<country_code>')
def get_states(country_code):
    """Endpoint da API para obter os estados de um país com seus nomes e códigos."""
    country_code_upper = country_code.upper()
    if country_code_upper in _states_cache:
        return jsonify(_states_cache[country_code_upper])

    states = []
    try:
        # Instancia a classe de feriados para o país.
        # Isso levanta NotImplementedError se o país não for suportado.
        country = holidays.country_holidays(country_code_upper)
        
        # Nem todos os países têm subdivisões.
        if hasattr(country, 'subdivisions') and country.subdivisions:
            subdivision_codes = country.subdivisions
            
            for code in subdivision_codes:
                name = code  # Define um nome padrão (o próprio código)
                try:
                    # Tenta buscar o nome completo da subdivisão
                    subdivision = pycountry.subdivisions.get(code=f"{country_code_upper}-{code}")
                    if subdivision:
                        name = subdivision.name
                except KeyError:
                    # Se não encontrar, o nome já está definido como o código, então não faz nada.
                    pass
                states.append({"code": code, "name": name})
            
            states.sort(key=lambda x: x['name'])
    except NotImplementedError:
        # País não suportado pela biblioteca 'holidays', retorna lista vazia.
        print(f"[INFO] País '{country_code_upper}' não tem subdivisões na biblioteca 'holidays'.")
    except Exception as e:
        # Captura outros erros inesperados para não quebrar o frontend.
        print(f"[ERROR] Erro inesperado ao buscar estados para {country_code_upper}: {e}")
        states = []  # Garante que uma lista vazia seja retornada em caso de erro.

    # Armazena o resultado no cache para futuras requisições.
    _states_cache[country_code_upper] = states
    return jsonify(states)

# Bloco para executar a aplicação em modo de desenvolvimento (debug)
if __name__ == '__main__':
    # O debug=True ativa o recarregamento automático ao salvar alterações no código.
    app.run(debug=True)