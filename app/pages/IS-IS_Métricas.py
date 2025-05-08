import streamlit as st
import re
import pandas as pd
import os
import plotly.express as px

st.title("FRRouting IS-IS Monitor")


def parse_isis_detail_file(filepath, router_name):
    with open(filepath, "r") as file:
        data = file.read()

    lsp_blocks = re.split(r'\n(?=\w{12}\.\w{2}-\w{2})', data)
    metricas = []

    for block in lsp_blocks:
        router_info = {"Router": router_name}

        header_match = re.match(r'(\w{12})\.\w{2}-\w{2}.*?(0x[0-9a-fA-F]+).*?(\d+)\s+(\d+/\d+/\d+)', block)
        if header_match:
            router_info["LSP ID"] = header_match.group(1)
            router_info["Holdtime"] = header_match.group(3)

        hostname_match = re.search(r'Hostname:\s+(\S+)', block)
        if hostname_match:
            router_info["Hostname"] = hostname_match.group(1)

        te_router_id = re.search(r'TE Router ID:\s+(\S+)', block)
        if te_router_id:
            router_info["TE Router ID"] = te_router_id.group(1)

        reachability = re.findall(r'Extended IP Reachability:\s+([\d./]+) \(Metric: (\d+)\)', block)
        router_info["IP Reachability"] = ', '.join([f"{net} (m: {metric})" for net, metric in reachability])

        neighbors = re.findall(r'Extended Reachability:\s+([\w.]+) \(Metric: (\d+)\)', block)
        router_info["Neighbors"] = ', '.join([f"{nb} (m: {metric})" for nb, metric in neighbors])

        if router_info.get("TE Router ID"):
            metricas.append(router_info)

    return metricas

all_metricas = []
for i in range(1, 5):
    filename = f"outputs_isis/r{i}_isis_database_detail.txt"
    if os.path.exists(filename):
        all_metricas.extend(parse_isis_detail_file(filename, f"r{i}"))
    else:
        st.warning(f"Arquivo não encontrado: {filename}")

df_total = pd.DataFrame(all_metricas)
st.subheader("📊 Tabela Consolidada IS-IS (com TE Router ID)")
st.dataframe(df_total)

st.subheader("📄 IS-IS Summary - ")

summary_data = []

def extract_summary(filepath, router_name):
    try:
        with open(filepath, "r") as f:
            content = f.read()

        summary = {"Router": router_name}

        def extract(regex, label):
            match = re.search(regex, content)
            if match:
                summary[label] = match.group(1)

        extract(r"System Id\s+:\s+(\S+)", "System Id")
        extract(r"Up time\s+:\s+(.+?) ago", "Up time")
        extract(r"Net:\s+([\d.]+)", "Net")
        extract(r"L2 IIH:\s+(\d+)", "TX L2 IIH")
        extract(r"L2 LSP:\s+(\d+)", "TX L2 LSP")
        extract(r"L2 CSNP:\s+(\d+)", "TX L2 CSNP")
        extract(r"LSP RXMT:\s+(\d+)", "TX LSP RXMT")
        
        rx_matches = re.findall(r"RX counters per PDU type:\s+(.*?)Level-2:", content, re.DOTALL)
        if rx_matches:
            rx_section = rx_matches[0]
            extract_rx = lambda label, r: extract(fr"{label}:\s+(\d+)", f"RX {label}")
            for label in ["L2 IIH", "L2 LSP", "L2 CSNP", "L2 PSNP"]:
                extract_rx(label, rx_section)
        
        extract(r"LSP0 regenerated:\s+(\d+)", "LSP0 regenerated")
        extract(r"LSPs purged:\s+(\d+)", "LSPs purged")
        extract(r"minimum interval\s+:\s+(\d+)", "SPF Min Interval")
        extract(r"last run elapsed\s+:\s+([\d:]+)", "SPF Last Run Elapsed")
        extract(r"last run duration\s+:\s+(\d+)", "SPF Last Run Duration (usec)")
        extract(r"run count\s+:\s+(\d+)", "SPF Run Count")

        summary_data.append(summary)

    except Exception as e:
        st.warning(f"Erro ao ler {filepath}: {e}")

for i in range(1, 5):
    filepath = f"outputs_isis/r{i}_isis_summary.txt"
    extract_summary(filepath, f"r{i}")

if summary_data:
    df_summaries = pd.DataFrame(summary_data)
    st.dataframe(df_summaries)
else:
    st.warning("Nenhum resumo encontrado.")

if 'SPF Run Count' in df_summaries.columns:
    fig_spf_run_count = px.bar(df_summaries, x="Router", y="SPF Run Count", title="Número de Execuções do SPF por Roteador")
    st.plotly_chart(fig_spf_run_count)
    st.write("Este gráfico mostra o número de execuções do algoritmo SPF (Shortest Path First) por cada roteador. Um número alto pode indicar mudanças frequentes na topologia.")

if 'SPF Last Run Duration (usec)' in df_summaries.columns:
    fig_spf_duration = px.bar(df_summaries, x="Router", y="SPF Last Run Duration (usec)", title="Duração da Última Execução do SPF (em microssegundos)")
    st.plotly_chart(fig_spf_duration)
    st.write("Este gráfico mostra a duração da última execução do algoritmo SPF em microssegundos, por roteador. Um valor alto pode indicar um roteador com desempenho de cálculos de rota mais lento.")

if 'TX L2 IIH' in df_summaries.columns:
    fig_l2_iih = px.bar(df_summaries, x="Router", y="TX L2 IIH", title="TX L2 IIH por Roteador")
    st.plotly_chart(fig_l2_iih)
    st.write("O gráfico acima mostra o número de pacotes L2 IIH (Intermediate Hello) enviados por cada roteador. Esses pacotes são essenciais para manter a comunicação com os vizinhos no protocolo IS-IS.")

if 'TX L2 LSP' in df_summaries.columns:
    fig_l2_lsp = px.bar(df_summaries, x="Router", y="TX L2 LSP", title="TX L2 LSP por Roteador")
    st.plotly_chart(fig_l2_lsp)
    st.write("O gráfico acima mostra o número de pacotes L2 LSP (Link State PDU) enviados por cada roteador. Estes pacotes contêm informações sobre os links conectados ao roteador e são cruciais para atualizar o estado da topologia da rede.")
