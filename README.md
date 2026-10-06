# Nexus BI Engine 🚀

**High-Performance Lakehouse & AI-Powered Business Intelligence Platform**

Nexus BI Engine es una plataforma empresarial moderna de inteligencia de datos diseñada para procesar millones de registros con latencia sub-segundo en Linux. Combina una arquitectura Data Lakehouse (Bronze, Silver, Gold), una Capa Semántica de Compresión Cognitiva para modelos de IA y un dashboard visual interactivo de alta fidelidad.

## Características Principales
- **Arquitectura Medallón**: Capas Bronze (ingesta raw), Silver (limpieza y particionado columnar Parquet) y Gold (Star Schema dimensional Kimball).
- **Motor OLAP de Ultra-Velocidad**: Cómputo analítico vectorizado con DuckDB.
- **Capa Semántica ("Compresión Cognitiva")**: Catálogo de esquemas y métricas que reduce el contexto del LLM a <350 tokens garantizando 0% alucinaciones numéricas.
- **Text-to-SQL Determinista & Sandbox**: Ejecución de consultas analíticas seguras y auditadas en tiempo récord.
- **Frontend Dark Luxury**: Interfaz empresarial oscura construida con React, Vite y Tailwind CSS inspirada en paneles analíticos de última generación.
- **Ejecución Unificada**: Corre absolutamente todo con un solo comando `./run`.

## Inicio Rápido
```bash
./run
```
