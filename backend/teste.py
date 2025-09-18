import sidrapy


def teste(id_table):
    try:
        data = sidrapy.get_table(
            table_code = id_table,
        territorial_level = "1",
        ibge_territorial_code = "all",
        classifications = {"11278": "33460", "166": "3067,3327"},
        period = "202002",
        header = 'n',
        format = 'list')

        return data

    except Exception as e:
        import traceback
        print("Erro ao buscar/processar dados:", e)
        traceback.print_exc()
        return []




if __name__ == '__main__':
    print(teste("5459"))