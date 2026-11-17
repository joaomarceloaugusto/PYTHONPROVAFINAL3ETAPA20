import pandas as pd
import openpyxl

df = pd.read_excel("dados-educacao.xlsx")


def _ler_bruto(origem):
    """Lê CSV (utf-8 ou latin-1) ou Excel, sem cabeçalho."""
    nome = origem if isinstance(origem, str) else origem.name
    nome = nome.lower()

    if nome.endswith(".csv"):
        for enc in ("utf-8", "latin-1"):
            try:
                if not isinstance(origem, str):
                    origem.seek(0)
                return pd.read_csv(origem, header=None, encoding=enc, sep=None, engine="python")
            except UnicodeDecodeError:
                continue
        raise ValueError("Não foi possível ler o CSV (encoding).")

    if not isinstance(origem, str):
        origem.seek(0)
    if nome.endswith(".xls"):
        return pd.read_excel(origem, header=None, engine="xlrd")
    return pd.read_excel(origem, header=None)

def classificar(genero):
   homens = 0
mulheres = 0

for row in sheet.iter_rows(min_row=2, values_only=True):

  linha_texto = [str(celula).strip() for celula in row if celula is not None]


  if 'Mestrado' in linha_texto:

    if 'Masculino' in linha_texto or 'Homem' in linha_texto or 'M' in linha_texto:
      homens += 1
    elif (
        'Feminino' in linha_texto or 'Mulher' in linha_texto or 'F' in linha_texto
    ):
      mulheres += 1

print(f'Total com Mestrado - Homens: {homens}')
print(f'Total com Mestrado - Mulheres: {mulheres}')


st.sidebar.title(" Menu & Filtros")

st.sidebar.subheader(" Arquivo de entrada")
arquivo = st.sidebar.file_uploader("Upload da Tabela 4 (IDHM):", type=["csv", "xls", "xlsx"])

df, anos = None, None
try:
    if arquivo is not None:
        df, anos = carregar_idhm(arquivo)
    elif os.path.exists(path):
        df, anos = carregar_idhm(path)
except Exception as e:
    st.sidebar.error(f"Erro ao carregar a tabela: {e}")

if df is None:
    st.warning(" **Aguardando leitura dos dados.**")
    st.info(f"Arquivo `{path}` não encontrado. Use o campo de upload na barra lateral.")
    st.stop()

st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Selecione a Visualização:",
    [" Visão Geral", " Evolução Temporal", " Ranking e Dispersão", " Notícias e Projetos"],
)

st.sidebar.markdown("---")
st.sidebar.subheader(" Filtros")

regioes_sel = st.sidebar.multiselect("Região:", list(regioes.keys()), default=list(regioes.keys()))
ufs_regiao = df[df["regiao"].isin(regioes_sel)]["sigla"].tolist()
ufs_sel = st.sidebar.multiselect("UF:", ufs_regiao, default=ufs_regiao)

ano_ini, ano_fim = st.sidebar.select_slider(
    "Período:", options=anos, value=(anos[0], anos[-1])
)
anos_periodo = [a for a in anos if int(ano_ini) <= int(a) <= int(ano_fim)]

df_fil = df[df["sigla"].isin(ufs_sel)].copy()

if df_fil.empty:
    st.warning("Selecione ao menos uma UF na barra lateral.")
    st.stop()

df_long = df_fil.melt(
    id_vars=["sigla", "estado", "regiao"],
    value_vars=anos_periodo,
    var_name="ano",
    value_name="idhm",
)
df_long["ano"] = df_long["ano"].astype(int)

media_ufs_por_ano = df_long.groupby("ano")["idhm"].mean().reset_index()


if pagina == " Visão Geral":
    st.title(" Painel IDHM — Consórcio de Governadores")
    st.markdown(
        "Análise do **Índice de Desenvolvimento Humano Municipal (IDHM)** por Unidade da Federação, "
        "para apoiar a criação de um fundo regional de redução de desigualdades."
    )

    col_ref = ano_fim
    serie = df_fil.set_index("sigla")[col_ref].dropna()

    maior_uf, menor_uf = serie.idxmax(), serie.idxmin()
    media = serie.mean()
    desvio = serie.std()
    iqr = serie.quantile(0.75) - serie.quantile(0.25)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"Média das UFs ({col_ref})", f"{media:.3f}")
    c2.metric("Maior IDHM", f"{maior_uf} • {serie.max():.3f}")
    c3.metric("Menor IDHM", f"{menor_uf} • {serie.min():.3f}")
    c4.metric("Desvio-padrão", f"{desvio:.3f}")
    c5.metric("IQR", f"{iqr:.3f}")

    base = df_fil[ano_ini].mean()
    st.caption(
        f"Média das UFs selecionadas em {ano_ini}: **{base:.3f}** → em {ano_fim}: **{media:.3f}** "
        f"({media - base:+.3f})."
    )

    st.markdown("---")
    st.subheader(f"Distribuição das UFs por faixa de desenvolvimento ({col_ref})")
    df_faixa = df_fil[["sigla", "estado", "regiao", col_ref]].copy()
    df_faixa["faixa"] = df_faixa[col_ref].apply(classificar)
    ordem = ["Muito baixo", "Baixo", "Médio", "Alto", "Muito alto"]
    contagem = (
        df_faixa["faixa"].value_counts().reindex(ordem).fillna(0).astype(int).reset_index()
    )
    contagem.columns = ["faixa", "ufs"]
    fig_faixa = px.bar(
        contagem, x="faixa", y="ufs", text="ufs",
        labels={"faixa": "Faixa do IDHM", "ufs": "Nº de UFs"},
        color="faixa",
        color_discrete_sequence=px.colors.sequential.Viridis,
    )
    fig_faixa.update_layout(showlegend=False)
    st.plotly_chart(fig_faixa, use_container_width=True)

    st.subheader(" Tabela tratada")
    st.dataframe(df_fil[["sigla", "estado", "regiao"] + anos_periodo], use_container_width=True)



