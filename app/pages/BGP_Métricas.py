import streamlit as st
import pandas as pd
import os
import re
import plotly.express as px

def parse_bgp_routes(text):
    route_lines = []
    capture = False
    for line in text.splitlines():
        if re.match(r'\s*Network\s+Next Hop', line):
            capture = True
            continue
        if capture:
            if not line.strip() or 'Displayed' in line:
                break
            route_lines.append(line.strip())

    data = []
    for line in route_lines:
        parts = line.split()
        if len(parts) >= 7:
            network = parts[1] if parts[0] in ('*', '*i', '*>', '*>i', '=') else parts[0]
            nexthop = parts[2] if parts[0] in ('*', '*i', '*>', '*>i', '=') else parts[1]
            path = parts[-1]
            data.append({'Network': network, 'NextHop': nexthop, 'Path': path})

    return pd.DataFrame(data)

def parse_bgp_summary(text):
    lines = text.splitlines()
    peers_start = 0
    peers = []

    for i, line in enumerate(lines):
        if re.match(r'^\s*Neighbor\s+V\s+AS\s+MsgRcvd', line):
            peers_start = i + 1
            break

    for line in lines[peers_start:]:
        if not line.strip() or line.startswith("Total number"):
            break
        parts = line.split()
        if len(parts) >= 12:
            peers.append({
                "Neighbor": parts[0],
                "Version": parts[1],
                "AS": parts[2],
                "MsgRcvd": parts[3],
                "MsgSent": parts[4],
                "UpDown": parts[8],
            })

    return pd.DataFrame(peers)

def parse_ping_results(directory):
    ping_data = {}
    for filename in os.listdir(directory):
        if filename.startswith('r') and '_ping' in filename:
            parts = filename.split('_ping')
            if len(parts) != 2:
                continue
            router = parts[0]
            target_ip = parts[1].replace('.txt', '')
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                match = re.search(r'round-trip min/avg/max = ([\d\.]+)/([\d\.]+)/([\d\.]+)', content)
                if match:
                    min_time = float(match.group(1))
                    avg_time = float(match.group(2))
                    max_time = float(match.group(3))
                    if router not in ping_data:
                        ping_data[router] = []
                    ping_data[router].append({
                        'Target IP': target_ip,
                        'Min (ms)': min_time,
                        'Avg (ms)': avg_time,
                        'Max (ms)': max_time
                    })
    return ping_data

def load_files():
    routers = ['r1', 'r2', 'r3', 'r4']
    routes_data = {}
    summary_data = {}

    for r in routers:
        with open(f'outputs_bgp/{r}_bgp_routes.txt') as f:
            routes_data[r] = parse_bgp_routes(f.read())

        with open(f'outputs_bgp/{r}_bgp_summary.txt') as f:
            summary_data[r] = parse_bgp_summary(f.read())

    return routes_data, summary_data

st.set_page_config(layout="wide")
st.title("📊 FRRouting BGP Monitor")

routes, summaries = load_files()
ping_results = parse_ping_results('outputs')

selected_router = st.selectbox("Selecione o roteador", options=['r1', 'r2', 'r3', 'r4'])

st.subheader(f"📘 Rotas BGP - {selected_router}")
st.dataframe(routes[selected_router], use_container_width=True)

st.subheader(f"🧾 Resumo BGP - {selected_router}")
st.dataframe(summaries[selected_router], use_container_width=True)

st.subheader(f"📈 Mensagens BGP - {selected_router}")
if not summaries[selected_router].empty:
    df_summary = summaries[selected_router].copy()
    df_summary['MsgRcvd'] = pd.to_numeric(df_summary['MsgRcvd'], errors='coerce')
    df_summary['MsgSent'] = pd.to_numeric(df_summary['MsgSent'], errors='coerce')

    fig = px.bar(
        df_summary,
        x='Neighbor',
        y=['MsgRcvd', 'MsgSent'],
        barmode='group',
        labels={'value': 'Mensagens', 'variable': 'Tipo'},
        title=f"Mensagens BGP por Vizinho - {selected_router.upper()}"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(
        "Este gráfico exibe as mensagens BGP enviadas e recebidas para cada vizinho BGP. "
        "A comparação entre as mensagens enviadas e recebidas ajuda a entender o tráfego entre os vizinhos BGP."
    )
else:
    st.warning("Nenhum dado de resumo BGP disponível para este roteador.")

st.subheader(f"📶 Resultados de Ping - {selected_router}")
if selected_router in ping_results:
    df_ping = pd.DataFrame(ping_results[selected_router])

    # Transformar os resultados de ping em um formato adequado para gráfico de barras horizontais
    df_ping_melted = df_ping.melt(id_vars=["Target IP"], value_vars=["Min (ms)", "Avg (ms)", "Max (ms)"],
                                  var_name="Tipo de Ping", value_name="Tempo (ms)")
    
    fig_ping = px.bar(
        df_ping_melted,
        y='Target IP',
        x='Tempo (ms)',
        color='Tipo de Ping',
        orientation='h',  # Barra horizontal
        labels={'Tempo (ms)': 'Tempo (ms)', 'Tipo de Ping': 'Tipo de Ping'},
        title=f"Resultados de Ping para {selected_router.upper()}",
        color_discrete_map={
            "Min (ms)": "green",
            "Avg (ms)": "blue",
            "Max (ms)": "red"
        }
    )

    st.plotly_chart(fig_ping, use_container_width=True)
    st.write(
        "Este gráfico de barras horizontais exibe os tempos de ping (mínimo, médio e máximo) para cada IP de destino. "
        "As barras coloridas representam diferentes tipos de tempo de resposta, permitindo uma análise rápida da latência."
    )
else:
    st.warning("Nenhum resultado de ping disponível para este roteador.")
