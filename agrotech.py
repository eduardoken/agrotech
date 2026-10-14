import json
import os
import importlib.util

oracle = None
if importlib.util.find_spec("oracledb"):
    oracle = importlib.import_module("oracledb")
elif importlib.util.find_spec("cx_Oracle"):
    oracle = importlib.import_module("cx_Oracle")

def obter_float_positivo(mensagem: str) -> float:
    """Solicita e valida a entrada de um número float positivo."""
    while True:
        try:
            valor = float(input(mensagem).replace(',', '.'))
            if valor < 0:
                print("⚠️ O valor não pode ser negativo. Tente novamente.")
                continue
            return valor
        except ValueError:
            print("⚠️ Entrada inválida! Digite apenas números válidos.")

def obter_texto_nao_vazio(mensagem: str) -> str:
    """Solicita e valida a entrada de uma string não vazia."""
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print("⚠️ O campo não pode ficar em branco.")


def calcular_perda_financeira(area_ha: float, perda_percentual: float, preco_tonelada: float, prod_media_ha: float = 100.0) -> tuple:
    """
    Calcula as toneladas perdidas e o prejuízo financeiro estimado.
    Retorna uma Tupla: (toneladas_perdidas, prejuizo_reais)
    """
    total_toneladas = area_ha * prod_media_ha
    toneladas_perdidas = total_toneladas * (perda_percentual / 100.0)
    prejuizo_reais = toneladas_perdidas * preco_tonelada
    return (round(toneladas_perdidas, 2), round(prejuizo_reais, 2))


def criar_registro_monitoramento(talhao: str, area_ha: float, perda_pct: float, preco_ton: float) -> dict:
    """Gera um dicionário contendo os dados estruturados do monitoramento."""
    ton_perdidas, prejuizo = calcular_perda_financeira(area_ha, perda_pct, preco_ton)
    
    registro = {
        "talhao": talhao,
        "area_ha": area_ha,
        "perda_percentual": perda_pct,
        "toneladas_perdidas": ton_perdidas,
        "prejuizo_estimado_brl": prejuizo
    }
    return registro

def salvar_em_arquivo_texto(lista_registros: list, nome_arquivo: str = "relatorio_perdas.txt") -> None:
    """Exporta os relatórios formatados em um arquivo TXT."""
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arq:
            arq.write("=== RELATÓRIO DE MONITORAMENTO DE PERDAS DA CANA ===\n\n")
            for reg in lista_registros:
                arq.write(f"Talhão: {reg['talhao']}\n")
                arq.write(f"Área (ha): {reg['area_ha']:.2f}\n")
                arq.write(f"Perda (%): {reg['perda_percentual']:.2f}%\n")
                arq.write(f"Cana Perdida: {reg['toneladas_perdidas']:.2f} toneladas\n")
                arq.write(f"Prejuízo Estimado: R$ {reg['prejuizo_estimado_brl']:.2f}\n")
                arq.write("-" * 50 + "\n")
        print(f"✅ Relatório TXT gerado com sucesso: '{nome_arquivo}'")
    except IOError as e:
        print(f"❌ Erro ao salvar arquivo TXT: {e}")


def salvar_em_arquivo_json(lista_registros: list, nome_arquivo: str = "dados_perdas.json") -> None:
    """Exporta a lista de dicionários para um arquivo JSON."""
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arq_json:
            json.dump(lista_registros, arq_json, indent=4, ensure_ascii=False)
        print(f"✅ Arquivo JSON gerado com sucesso: '{nome_arquivo}'")
    except IOError as e:
        print(f"❌ Erro ao salvar arquivo JSON: {e}")

def salvar_no_oracle(lista_registros: list) -> None:
    """
    Função para inserir os dados no Banco de Dados Oracle.
    Ajuste as credenciais (user, password, dsn) conforme seu ambiente.
    """
    usuario = os.getenv("ORACLE_USER", "rm575774")
    senha = os.getenv("ORACLE_PASSWORD", "senha")
    dsn = os.getenv("ORACLE_DSN", "oracle.fiap.com.br:1521/ORCL")

    print("\n--- Conectando ao Banco de Dados Oracle ---")
    try:
        conexao = oracle.connect(user=usuario, password=senha, dsn=dsn)
        cursor = conexao.cursor()

        cursor.execute("""
            BEGIN
                EXECUTE IMMEDIATE 'CREATE TABLE T_MONITORAMENTO_PERDAS (
                    id_monitoramento NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    nm_talhao VARCHAR2(50),
                    vl_area_ha NUMBER(10,2),
                    pc_perda NUMBER(5,2),
                    qt_ton_perdida NUMBER(10,2),
                    vl_prejuizo_brl NUMBER(12,2)
                )';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -955 THEN RAISE; END IF;
            END;
        """)

        query_insert = """
            INSERT INTO T_MONITORAMENTO_PERDAS 
            (nm_talhao, vl_area_ha, pc_perda, qt_ton_perdida, vl_prejuizo_brl)
            VALUES (:1, :2, :3, :4, :5)
        """

        for reg in lista_registros:
            cursor.execute(query_insert, (
                reg["talhao"],
                reg["area_ha"],
                reg["perda_percentual"],
                reg["toneladas_perdidas"],
                reg["prejuizo_estimado_brl"]
            ))

        conexao.commit()
        cursor.close()
        conexao.close()
        print("✅ Dados salvos com sucesso no Banco de Dados Oracle!")
    except Exception as erro:
        print(f"⚠️ Não foi possível salvar no Oracle. Verifique a conexão e credenciais.\nDetalhes: {erro}")

def main():
    print("==================================================")
    print("      AGROTECH: GESTÃO E REDUÇÃO DE PERDAS        ")
    print("           COLHEITA DE CANA-DE-AÇÚCAR             ")
    print("==================================================")

    historico_monitoramentos = []

    preco_tonelada_cana = obter_float_positivo("Informe o preço médio atual da tonelada de cana (R$): ")

    while True:
        print("\n--- NOVO CADASTRO DE MONITORAMENTO ---")
        talhao = obter_texto_nao_vazio("Nome ou Número do Talhão (ex: Talhão 01, Lote A): ")
        area = obter_float_positivo(f"Tamanho da área do talhão '{talhao}' (em hectares): ")
        perda_pct = obter_float_positivo(f"Porcentagem estimada de perda na colheita (%): ")

        registro = criar_registro_monitoramento(talhao, area, perda_pct, preco_tonelada_cana)
        historico_monitoramentos.append(registro)

        print("\n✅ Monitoramento registrado com sucesso!")
        continuar = input("\nDeseja cadastrar outro talhão? (S/N): ").strip().upper()
        if continuar != 'S':
            break

    print("\n" + "="*50)
    print("RESUMO DOS MONITORAMENTOS REGISTRADOS")
    print("="*50)
    for index, item in enumerate(historico_monitoramentos, start=1):
        print(f"\n[{index}] Talhão: {item['talhao']}")
        print(f"    Área: {item['area_ha']} ha | Perda Estimada: {item['perda_percentual']}%")
        print(f"    Volume Perdido: {item['toneladas_perdidas']} toneladas")
        print(f"    Prejuízo Financeiro: R$ {item['prejuizo_estimado_brl']:,.2f}")

    print("\n" + "="*50)
    print("EXPORTAÇÃO E PERSISTÊNCIA DOS DADOS")
    print("="*50)
    salvar_em_arquivo_texto(historico_monitoramentos)
    salvar_em_arquivo_json(historico_monitoramentos)
    salvar_no_oracle(historico_monitoramentos)

    print("\n==================================================")
    print("      Processo concluído com sucesso!")
    print("==================================================")

if __name__ == "__main__":
    main()