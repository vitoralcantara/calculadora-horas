import datetime
import holidays
from flask import Flask, render_template, request

# Inicializa a aplicação Flask
app = Flask(__name__)

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
        feriados_locais = holidays.CountryHoliday(pais, state=estado)
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
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Recebe os dados do formulário, calcula e mostra o resultado."""
    pais = request.form.get('pais').upper()
    estado = request.form.get('estado').upper()

    horas, erro = calcular_horas_uteis(pais, estado)

    localidade = pais
    if estado:
        localidade += f"-{estado}"

    return render_template('result.html', horas=horas, localidade=localidade, erro=erro)