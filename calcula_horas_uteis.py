# /home/user/calcula_horas_uteis_avancado.py
import datetime
import holidays

# --- Configurações ---
HORAS_UTEIS_POR_DIA = 8
# Especifique o país e, opcionalmente, o estado/província para feriados mais precisos.
# Para o Brasil, você pode especificar o estado, ex: 'SP', 'RJ', 'MG'.
PAIS_FERIADOS = 'BR' 
ESTADO_FERIADOS = 'PE' # Use None se quiser apenas feriados nacionais
# --------------------

def calcular_horas_uteis_com_biblioteca():
    """
    Calcula o total de horas úteis usando a biblioteca 'holidays' para mais precisão.
    """
    hoje = datetime.date.today()
    primeiro_dia_do_mes = hoje.replace(day=1)
    
    # Inicializa o objeto de feriados para o local especificado
    feriados_locais = holidays.CountryHoliday(PAIS_FERIADOS, state=ESTADO_FERIADOS)
    
    total_horas_uteis = 0
    dia_atual = primeiro_dia_do_mes
    
    while dia_atual <= hoje:
        e_dia_de_semana = dia_atual.weekday() < 5
        nao_e_feriado = dia_atual not in feriados_locais
        
        if e_dia_de_semana and nao_e_feriado:
            total_horas_uteis += HORAS_UTEIS_POR_DIA
        
        dia_atual += datetime.timedelta(days=1)
        
    return total_horas_uteis

if __name__ == "__main__":
    try:
        horas_calculadas = calcular_horas_uteis_com_biblioteca()
        localidade = PAIS_FERIADOS
        if ESTADO_FERIADOS:
            localidade += f"-{ESTADO_FERIADOS}"
        print(f"Desde o início do mês até hoje, tivemos {horas_calculadas} horas úteis (considerando feriados de {localidade}).")
    except ImportError:
        print("A biblioteca 'holidays' não está instalada.")
        print("Por favor, instale-a com o comando: pip install holidays")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")