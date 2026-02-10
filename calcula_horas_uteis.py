# /home/user/calcula_horas_uteis_avancado.py
import datetime
import argparse
import calendar
from core_calculator import calcular_horas_uteis, parse_ferias

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
        help="Opcional: Dias ou intervalos de férias, separados por vírgula (ex: 10,15,20-25)."
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

        data_inicio = datetime.date(ano_calculo, mes_calculo, 1)
        
        if ano_calculo == hoje.year and mes_calculo == hoje.month:
            data_fim = hoje
            periodo_str = f"o início do mês até hoje ({data_fim.strftime('%d/%m/%Y')})"
        else:
            _, ultimo_dia = calendar.monthrange(ano_calculo, mes_calculo)
            data_fim = datetime.date(ano_calculo, mes_calculo, ultimo_dia)
            periodo_str = f"o mês de {mes_calculo:02d}/{ano_calculo}"

        dias_de_ferias = parse_ferias(args.ferias, ano_calculo, mes_calculo)

        horas_calculadas = calcular_horas_uteis(data_inicio, data_fim, args.pais, args.estado, dias_de_ferias)
        localidade = args.pais.upper()
        if args.estado:
            localidade += f"-{args.estado.upper()}"
        
        mensagem = f"Para {periodo_str}, o total foi de {horas_calculadas} horas úteis (considerando feriados de {localidade})."
        if args.ferias:
            mensagem += f"\nDias de férias desconsiderados no mês {mes_calculo:02d}/{ano_calculo}: {args.ferias}."
        print(mensagem)
    except (ValueError, NotImplementedError) as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()