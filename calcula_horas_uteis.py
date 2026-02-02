# /home/user/calcula_horas_uteis_avancado.py
import datetime
import holidays
import argparse
import calendar

# --- Configurações ---
HORAS_UTEIS_POR_DIA = 8
# --------------------

def calcular_horas_uteis_com_biblioteca(data_inicio, data_fim, pais, estado=None, dias_de_ferias=None):
    """
    Calcula o total de horas úteis em um intervalo de datas, considerando feriados.
    """
    ferias_no_mes = dias_de_ferias or []
    
    # Inicializa o objeto de feriados para o local especificado
    # Otimiza a busca de feriados para o intervalo de anos necessário
    anos_necessarios = range(data_inicio.year, data_fim.year + 1)
    feriados_locais = holidays.CountryHoliday(pais, state=estado, years=anos_necessarios)
    
    total_horas_uteis = 0
    dia_atual = data_inicio
    
    while dia_atual <= data_fim:
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
        description="Calcula as horas úteis de um determinado período."
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
    parser.add_argument(
        "--ano",
        type=int,
        help="Opcional: Ano para o cálculo. Se omitido, usa o ano atual."
    )
    parser.add_argument(
        "--mes",
        type=int,
        help="Opcional: Mês para o cálculo. Se omitido, usa o mês atual."
    )
    args = parser.parse_args()

    try:
        hoje = datetime.date.today()
        ano_calculo = args.ano or hoje.year
        mes_calculo = args.mes or hoje.month

        # Define o período de cálculo
        if args.ano and args.mes:
            # Calcula para o mês inteiro especificado
            data_inicio = datetime.date(ano_calculo, mes_calculo, 1)
            _, ultimo_dia = calendar.monthrange(ano_calculo, mes_calculo)
            data_fim = datetime.date(ano_calculo, mes_calculo, ultimo_dia)
            periodo_str = f"o mês de {mes_calculo:02d}/{ano_calculo}"
        else:
            # Comportamento padrão: do início do mês atual até hoje
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
            periodo_str = f"o início do mês até hoje ({data_fim.strftime('%d/%m/%Y')})"

        dias_de_ferias = []
        if args.ferias:
            try:
                # Converte a string "10,11,22" em uma lista de objetos date
                dias_int = [int(dia.strip()) for dia in args.ferias.split(',')]
                dias_de_ferias = [datetime.date(ano_calculo, mes_calculo, dia) for dia in dias_int]
            except (ValueError, TypeError):
                print("Erro: Formato inválido para dias de férias. Use números separados por vírgula.")
                return

        horas_calculadas = calcular_horas_uteis_com_biblioteca(data_inicio, data_fim, args.pais, args.estado, dias_de_ferias)
        localidade = args.pais.upper()
        if args.estado:
            localidade += f"-{args.estado.upper()}"
        
        mensagem = f"Para {periodo_str}, o total foi de {horas_calculadas} horas úteis (considerando feriados de {localidade})."
        if args.ferias:
            mensagem += f"\nDias de férias desconsiderados no mês {mes_calculo:02d}/{ano_calculo}: {args.ferias}."
        print(mensagem)
    except ImportError:
        print("A biblioteca 'holidays' não está instalada.")
        print("Por favor, instale-a com o comando: pip install holidays")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()