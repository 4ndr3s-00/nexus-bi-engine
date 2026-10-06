# Nexus BI Engine 🚀

**Plataforma Empresarial de Data Lakehouse & Business Intelligence con IA**

Nexus BI Engine es una plataforma de analítica de datos de alto rendimiento diseñada para entornos Linux. Permite procesar y analizar **millones de registros con latencia sub-100ms**, ejecutar consultas en lenguaje natural mediante una **Capa Semántica de Compresión Cognitiva**, y generar **informes ejecutivos instantáneos** con visualizaciones interactivas de alta fidelidad estilo Power BI.

---

## 🏛️ Arquitectura del Sistema

```
  [ INGESTA MASIVA DE DATOS ]
     (1,000,000 - 5,000,000+ eventos en segundos)
                         │
                         ▼
        ┌──────────────────────────────────┐
        │       ARQUITECTURA MEDALLÓN      │
        │                                  │
        │  🥉 BRONZE: Ingesta Raw (Parquet)│
        │  🥈 SILVER: Limpieza & ZSTD      │
        │  🥇 GOLD: Star Schema (Kimball)  │
        │     - fact_sales (atómico)       │
        │     - dim_date, dim_product, ... │
        └─────────────────┬────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │  MOTOR ANALÍTICO OLAP VECTORIZADO│
        │      (DuckDB Columnar Engine)    │
        │   Consultas analíticas en <50ms  │
        └─────────────────┬────────────────┘
                          ▲
                          │ SQL Determinista Validado
        ┌─────────────────┴────────────────┐
        │   CAPA SEMÁNTICA ("COMPRESIÓN")   │
        │   - Catálogo de Esquemas & KPIs  │
        │   - Contexto ultra-compacto (<200t)
        │   - Validador Zero-Trust Sandbox │
        └─────────────────▲────────────────┘
                          │
       ┌──────────────────┴──────────────────┐
       │   AGENTE ANALÍTICO (TEXT-TO-SQL)     │
       │    Consultas en Lenguaje Natural    │
       └──────────────────▲──────────────────┘
                          │
                          ▼
       ┌─────────────────────────────────────┐
       │     FRONTEND VITE + REACT + TAILWIND │
       │  - Dark Luxury UI (Tema corporativo)│
       │  - Scorecard de 4 KPIs con tendencia│
       │  - Gráficos interactivos de curvas  │
       │  - Informes Ejecutivos Descargables │
       └─────────────────────────────────────┘
```

---

## ✨ Características Principales

1. **Arquitectura Medallón & Modelo Kimball**:
   - **Bronze**: Almacenamiento raw sin transformar.
   - **Silver**: Limpieza, deduplicación y tipado estricto con compresión columnar Parquet.
   - **Gold**: Esquema en estrella con `fact_sales`, `dim_date`, `dim_product`, `dim_customer` y `dim_channel`.
2. **Motor OLAP Vectorizado (DuckDB)**:
   - Cómputo en memoria y disco NVMe sin latencia de red.
   - Procesa 1,000,000 de filas en **26 a 46 milisegundos**.
3. **Capa Semántica ("Compresión Cognitiva")**:
   - Condensa todo el catálogo de métricas y dimensiones a **< 200 tokens**.
   - Garantiza **0% alucinaciones numéricas**: las métricas las calcula el motor SQL, la IA redacta la síntesis gerencial.
4. **Query Guard Zero-Trust**:
   - Sandbox que bloquea inyecciones SQL, `DROP`, `DELETE`, `UPDATE` o llamadas al sistema operativo.
5. **Frontend Dark Luxury en React**:
   - Interfaz moderna en modo oscuro (`#0d0e12`), tarjetas KPI con indicadores de tendencia, gráficos de tendencias financieras y desglose por categorías.
   - Exportación de informes en 1 clic a formato **HTML interactivo autónomo** o **JSON**.
6. **Comando Único `./run`**:
   - Ejecuta backend y frontend concurrentemente desde una sola terminal.

---

## 🚀 Inicio Rápido (Un Solo Comando)

Para levantar absolutamente todo el sistema (backend FastAPI + DuckDB y frontend Vite + React):

```bash
./run
```

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Documentación Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Verificación del Sistema y Tests

```bash
./run --check
```

### Benchmark de 1,000,000 de Registros

```bash
.venv/bin/python scripts/benchmark_1m.py
```

---

## 📡 Endpoints de la API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/health` | Estado del servicio y rutas del Lakehouse |
| `GET` | `/api/v1/lakehouse/stats` | Conteo de filas en vivo por capa y tamaño en disco |
| `POST` | `/api/v1/lakehouse/seed` | Ingesta de 50k a 5M de filas transaccionales |
| `GET` | `/api/v1/dashboard/overview` | Métricas y gráficos de visión general |
| `POST` | `/api/v1/query` | Consulta en lenguaje natural $\rightarrow$ SQL $\rightarrow$ Datos |
| `POST` | `/api/v1/report/generate` | Genera informe ejecutivo completo con IA |
| `POST` | `/api/v1/report/export-html` | Descarga informe interactivo en HTML autónomo |

---

## 🧪 Estructura de Pruebas

El proyecto cuenta con una suite completa de pruebas unitarias y de integración:
```bash
.venv/bin/pytest tests/ -v
```
- `tests/test_smoke.py`: Comprobaciones de entorno y arranque.
- `tests/test_warehouse.py`: Pruebas de integridad del esquema estrella y SLA < 100ms.
- `tests/test_semantic_ai.py`: Pruebas de compresión de tokens, QueryGuard y Text-to-SQL.
- `tests/test_api.py`: Integración de endpoints REST y bloqueo de inyecciones.
- `tests/test_e2e_integration.py`: Flujo completo desde ingesta hasta exportación HTML.
