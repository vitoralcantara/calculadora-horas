# /home/user/calcula_horas_uteis_avancado.py
import datetime
import holidays
import argparse

# --- Configurações ---
HORAS_UTEIS_POR_DIA = 8
# --------------------

def calcular_horas_uteis_com_biblioteca(pais, estado=None, dias_de_ferias=None):
    """
    Calcula o total de horas úteis usando a biblioteca 'holidays' para mais precisão,
    com base nos parâmetros de país e estado.
    """
    hoje = datetime.date.today()
    primeiro_dia_do_mes = hoje.replace(day=1)
    ferias_no_mes = dias_de_ferias or []
    
    # Inicializa o objeto de feriados para o local especificado
    feriados_locais = holidays.CountryHoliday(pais, state=estado)
    
    total_horas_uteis = 0
    dia_atual = primeiro_dia_do_mes
    
    while dia_atual <= hoje:
        e_dia_de_semana = dia_atual.weekday() < 5
        nao_e_ferias = dia_atual not in ferias_no_mes
        nao_e_feriado = dia_atual not in feriados_locais
        
        if e_dia_de_semana and nao_e_feriado and nao_e_ferias:
            total_horas_uteis += HORAS_UTEIS_POR_DIA
        
        dia_atual += datetime.timedelta(days=1)
        
    return total_horas_uteis

def main():
    """
    Função principal que analisa os argumentos da linha de comando e executa o cálculo.
    """
    parser = argparse.ArgumentParser(
        description="Calcula as horas úteis do início do mês até hoje."
    )
    parser.add_argument(
        "--pais",
        required=True,
        help="Código do país para os feriados (ex: BR, US, PT)."
    )
    parser.add_argument(
        "--estado",
        default=None,
        help="Opcional: Código do estado/província (ex: PE, SP, CA)."
    )
    parser.add_argument(
        "--ferias",
        default="",
        help="Opcional: Dias de férias no mês, separados por vírgula (ex: 10,15,22)."
    )
    args = parser.parse_args()

    try:
        dias_de_ferias = []
        if args.ferias:
            try:
                hoje = datetime.date.today()
                # Converte a string "10,11,22" em uma lista de objetos date
                dias_int = [int(dia.strip()) for dia in args.ferias.split(',')]
                dias_de_ferias = [datetime.date(hoje.year, hoje.month, dia) for dia in dias_int]
            except (ValueError, TypeError):
                print("Erro: Formato inválido para dias de férias. Use números separados por vírgula.")
                return

        horas_calculadas = calcular_horas_uteis_com_biblioteca(args.pais, args.estado, dias_de_ferias)
        localidade = args.pais.upper()
        if args.estado:
            localidade += f"-{args.estado.upper()}"
        
        mensagem = f"Desde o início do mês até hoje, tivemos {horas_calculadas} horas úteis (considerando feriados de {localidade})."
        if args.ferias:
            mensagem += f"\nDias de férias desconsiderados: {args.ferias}."
        print(mensagem)
    except ImportError:
        print("A biblioteca 'holidays' não está instalada.")
        print("Por favor, instale-a com o comando: pip install holidays")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()