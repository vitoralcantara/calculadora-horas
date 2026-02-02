import datetime
import calendar
import holidays

HORAS_UTEIS_POR_DIA = 8

def parse_ferias(ferias_str: str, ano: int, mes: int) -> list[datetime.date]:
    """
    Analisa uma string de dias de férias (com dias e intervalos) e retorna uma lista de objetos date.
    Exemplo de string: "10, 15, 20-25"
    """
    if not ferias_str:
        return []

    dias_int = set()
    try:
        partes = ferias_str.split(',')
        for parte in partes:
            parte = parte.strip()
            if not parte:
                continue
            if '-' in parte:
                inicio, fim = map(int, parte.split('-'))
                if inicio > fim:
                    raise ValueError("O início do intervalo de férias não pode ser maior que o fim.")
                dias_int.update(range(inicio, fim + 1))
            else:
                dias_int.add(int(parte))
        
        return [datetime.date(ano, mes, dia) for dia in sorted(list(dias_int))]
    except (ValueError, TypeError) as e:
        raise ValueError(f"Formato inválido para dias de férias: '{ferias_str}'. Use números (ex: 10,15) e/ou intervalos (ex: 20-25).") from e

def calcular_horas_uteis(data_inicio: datetime.date, data_fim: datetime.date, pais: str, estado: str | None = None, dias_de_ferias: list[datetime.date] | None = None) -> int:
    """
    Calcula o total de horas úteis em um intervalo de datas, considerando feriados.
    """
    ferias_no_periodo = dias_de_ferias or []
    
    if not estado:
        estado = None

    anos_necessarios = range(data_inicio.year, data_fim.year + 1)
    
    try:
        feriados_locais = holidays.CountryHoliday(pais, state=estado, years=anos_necessarios)
    except NotImplementedError as e:
        raise NotImplementedError(f"País '{pais}' ou estado '{estado}' não encontrado na biblioteca de feriados.") from e

    total_horas_uteis = 0
    dia_atual = data_inicio
    
    while dia_atual <= data_fim:
        e_dia_de_semana = dia_atual.weekday() < 5
        nao_e_ferias = dia_atual not in ferias_no_periodo
        nao_e_feriado = dia_atual not in feriados_locais
        
        if e_dia_de_semana and nao_e_feriado and nao_e_ferias:
            total_horas_uteis += HORAS_UTEIS_POR_DIA
        
        dia_atual += datetime.timedelta(days=1)
        
    return total_horas_uteis