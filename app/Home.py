import streamlit as st

st.set_page_config(page_title="Projeto GA - Redes II", layout="wide")
st.title(" Projeto GA - Redes II")
st.write("Use o menu lateral para acessar as páginas de métricas IS-IS e BGP.")

st.markdown("""
### Topologia da Rede

Este projeto simula uma rede de roteadores em Docker para testar e monitorar o desempenho de protocolos de roteamento, como IS-IS e BGP.

A topologia é composta por **quatro roteadores** (r1, r2, r3, r4), conectados conforme descrito abaixo:

- **Roteador r1**: Conectado a r2 (10.0.1.11) e r3 (10.0.2.11).
- **Roteador r2**: Conectado a r1 (10.0.1.2) e r4 (10.0.3.2).
- **Roteador r3**: Conectado a r1 (10.0.2.3) e r4 (10.0.3.3).
- **Roteador r4**: Conectado a r2 (10.0.3.4) e r3 (10.0.4.4).

Cada roteador executa **IS-IS** para roteamento interno e **BGP** para troca de informações de roteamento entre os roteadores. As redes estão segmentadas em sub-redes, como 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24 e 10.0.4.0/24.

### Tecnologias Utilizadas

**Docker**:  
O projeto utiliza o **Docker** para criar containers que simulam os roteadores da rede.  Através do Docker Compose, os containers são configurados e conectados, criando a infraestrutura necessária para a simulação de roteadores.

**FRRouting (FRR)**:  
Neste projeto, o **FRR** é utilizado para configurar e gerenciar os protocolos de roteamento nos roteadores simulados.  
- **IS-IS** (Intermediate System to Intermediate System) é utilizado para roteamento interno entre os roteadores. Ele é um protocolo de roteamento de link-state utilizado em redes grandes e complexas.
- **BGP** (Border Gateway Protocol) é utilizado para a troca de informações de roteamento entre os roteadores, permitindo a comunicação entre diferentes redes.

### Visão Geral do Projeto

Com essa configuração, o sistema coleta e exibe métricas de desempenho da rede, como tabelas de roteamento, pacotes enviados, taxa de transmissão e delay. O **Dashboard** desenvolvido em **Streamlit** permite visualizar essas métricas em tempo real, ajudando a analisar o desempenho da rede e a otimizar a configuração dos protocolos de roteamento.
""")
