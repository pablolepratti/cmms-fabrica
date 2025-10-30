"""Visualización de grafo CMMS con Streamlit, NetworkX y Pyvis."""

from __future__ import annotations

from typing import Dict, Optional

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from modulos.conexion_mongo import get_db

# Colores corporativos consistentes para cada tipo de nodo
COLOR_ACTIVO = "#1f77b4"
COLOR_HISTORIAL = "#aaaaaa"
COLOR_ORIGEN = "#ff7f0e"
COLOR_USUARIO = "#2ca02c"
COLOR_PROVEEDOR = "#d62728"


def construir_grafo(db, filtros: Optional[Dict[str, str]] = None) -> nx.DiGraph:
    """Construye un grafo dirigido representando las relaciones del CMMS."""
    filtros = filtros or {}
    grafo = nx.DiGraph()

    activos_filter: Dict[str, str] = {}
    historial_filter: Dict[str, str] = {}

    if "id_activo_tecnico" in filtros and filtros["id_activo_tecnico"]:
        activos_filter["id_activo_tecnico"] = filtros["id_activo_tecnico"]
        historial_filter["id_activo_tecnico"] = filtros["id_activo_tecnico"]

    activos = list(db["activos_tecnicos"].find(activos_filter))
    historial = list(db["historial"].find(historial_filter))

    for activo in activos:
        activo_id = activo.get("id_activo_tecnico")
        if not activo_id:
            continue
        grafo.add_node(
            activo_id,
            label=activo.get("nombre", activo_id),
            title=f"Activo: {activo.get('nombre', activo_id)}",
            tipo="activo",
            color=COLOR_ACTIVO,
        )

    for evento in historial:
        activo_id = evento.get("id_activo_tecnico")
        if not activo_id:
            continue

        nodo_historial = str(evento.get("_id"))
        descripcion = evento.get("descripcion", "Evento en historial")
        fecha = evento.get("fecha_evento")
        fecha_txt = fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha or "")

        grafo.add_node(
            nodo_historial,
            label=fecha_txt or nodo_historial,
            title=f"Historial: {descripcion}",
            tipo="historial",
            color=COLOR_HISTORIAL,
        )

        if activo_id in grafo:
            grafo.add_edge(activo_id, nodo_historial)

        tipo_evento = evento.get("tipo_evento")
        id_origen = evento.get("id_origen")
        if tipo_evento and id_origen:
            nodo_origen = f"{tipo_evento}::{id_origen}"
            grafo.add_node(
                nodo_origen,
                label=id_origen,
                title=f"Origen ({tipo_evento}): {id_origen}",
                tipo="origen",
                color=COLOR_ORIGEN,
            )
            grafo.add_edge(nodo_historial, nodo_origen)

        usuario = evento.get("usuario_registro")
        if usuario:
            nodo_usuario = f"usuario::{usuario}"
            grafo.add_node(
                nodo_usuario,
                label=usuario,
                title=f"Usuario: {usuario}",
                tipo="usuario",
                color=COLOR_USUARIO,
            )
            grafo.add_edge(nodo_usuario, nodo_historial)

        proveedor = evento.get("proveedor_externo")
        if proveedor:
            nodo_proveedor = f"proveedor::{proveedor}"
            grafo.add_node(
                nodo_proveedor,
                label=proveedor,
                title=f"Proveedor externo: {proveedor}",
                tipo="proveedor",
                color=COLOR_PROVEEDOR,
            )
            grafo.add_edge(nodo_historial, nodo_proveedor)

    return grafo


def mostrar_grafo(grafo: nx.DiGraph) -> None:
    """Renderiza el grafo utilizando Pyvis y lo incrusta en Streamlit."""
    net = Network(height="700px", width="100%", directed=True, notebook=False)
    net.toggle_physics(True)

    for node_id, atributos in grafo.nodes(data=True):
        net.add_node(node_id, **atributos)

    for origen, destino, atributos in grafo.edges(data=True):
        net.add_edge(origen, destino, **atributos)

    net.write_html("grafo_cmms.html")

    with open("grafo_cmms.html", "r", encoding="utf-8") as archivo_html:
        components.html(archivo_html.read(), height=750, scrolling=True)


def app() -> None:
    """Punto de entrada principal del módulo Streamlit."""
    st.title("🔗 Grafo CMMS")
    db = get_db()

    if db is None:
        st.error("No se pudo conectar a la base de datos. Verifique la configuración de MongoDB.")
        return

    activos_cursor = db["activos_tecnicos"].find({}, {"_id": 0, "id_activo_tecnico": 1})
    activos_disponibles = sorted({doc.get("id_activo_tecnico") for doc in activos_cursor if doc.get("id_activo_tecnico")})
    opciones = ["(all)"] + activos_disponibles

    seleccion = st.selectbox("Filtrar por activo técnico", opciones)

    filtros: Optional[Dict[str, str]] = None
    if seleccion != "(all)":
        filtros = {"id_activo_tecnico": seleccion}

    grafo = construir_grafo(db, filtros)

    st.info(f"Nodos: {grafo.number_of_nodes()} | Aristas: {grafo.number_of_edges()}")
    mostrar_grafo(grafo)
