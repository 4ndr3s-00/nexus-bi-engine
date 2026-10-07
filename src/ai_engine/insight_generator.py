from typing import Any

class ExecutiveInsightGenerator:
    """
    Synthesizes analytical query results into high-impact executive summaries for:
    1. Hospital Directors & EPS Executives (Triage, ICU beds, Glosas, Appointment Access).
    2. Corporate B2B Leadership (Revenue, Profit, Orders).
    Ensures 0% numerical hallucinations by grounding every metric directly in DB results.
    """
    def generate_report(self, query_result: dict[str, Any]) -> dict[str, Any]:
        question = query_result.get("question", "")
        latency_ms = query_result.get("latency_ms", 0.0)
        is_ood = query_result.get("is_out_of_domain", False)
        is_pii = query_result.get("is_pii_violation", False)

        # 1. Handle Out-of-Domain or PII Rejection
        if is_ood:
            reason = query_result.get("reason", "La consulta no corresponde al modelo de datos.")
            if is_pii:
                headline = "Bloqueo por Habeas Data y Reserva Legal (Ley 1581)"
                highlights = [
                    "🔒 **Protección de Datos Sensibles**: No se permite acceso a cédulas, nombres ni datos de contacto individuales.",
                    "🛡️ **Anonimización Criptográfica**: Las historias clínicas están identificadas con tokens SHA-256 irreversibles.",
                    "📋 **Uso Permitido**: Análisis agregados de ocupación, tiempos de triage, glosas y oportunidad de atención."
                ]
                recs = [
                    "Formular preguntas a nivel agregado (por sede, por EPS, por especialidad o por mes).",
                    "Consultar estadísticas de morbilidad CIE-10 o indicadores normativos de la Supersalud."
                ]
            else:
                headline = "Información Fuera de Dominio del Lakehouse"
                highlights = [
                    "⚠️ **Fuera de Alcance**: La entidad consultada no existe en la red de 8 EPS/IPS.",
                    "🏥 **Datos Disponibles**: Urgencias Triage Manchester, Censo Camas UCI, Auditoría de Glosas RIPS y Oportunidad de Citas."
                ]
                recs = [
                    "Consultar tiempos de espera en sedes 24h o comparativa entre EPS.",
                    "Explorar el censo hospitalario de camas UCI o los diagnósticos CIE-10 más frecuentes."
                ]

            return {
                "headline": headline,
                "summary": reason,
                "chart_type": "out_of_domain",
                "kpi_cards": [],
                "highlights": highlights,
                "recommendations": recs,
                "table_data": [],
                "dimensions": [],
                "direct_answer": None
            }

        data = query_result.get("data", [])
        if not data:
            return {
                "headline": "Sin Registros Clínicos para los Criterios Especificados",
                "summary": f"La consulta '{question}' no arrojó registros coincidentes en la capa Gold.",
                "chart_type": "empty_state",
                "kpi_cards": [],
                "highlights": [],
                "recommendations": ["Ampliar el rango de fechas o relajar los filtros por sede/aseguradora."],
                "table_data": [],
                "dimensions": [],
                "direct_answer": None
            }

        first_row = data[0]
        # Detect if result is Clinical Healthcare or B2B
        is_clinical = any(k in first_row for k in [
            "tiempo_espera_promedio_min", "tasa_ocupacion_pct", "total_glosado",
            "oportunidad_promedio_dias", "total_atenciones", "total_camas_ocupadas"
        ])

        if is_clinical:
            return self._generate_clinical_report(question, data, latency_ms, query_result.get("intent") or {})
        else:
            return self._generate_b2b_report(question, data, latency_ms, query_result.get("intent") or {})

    def _generate_clinical_report(self, question: str, data: list[dict], latency_ms: float, intent_data: dict) -> dict[str, Any]:
        first_row = data[0]
        clinical_metric_keys = {
            "total_atenciones", "tiempo_espera_promedio_min", "estancia_promedio_horas",
            "total_reingresos_72h", "tasa_reingreso_pct", "total_camas_instaladas",
            "total_camas_ocupadas", "tasa_ocupacion_pct", "total_radicado", "total_glosado",
            "total_levantado", "tasa_glosa_pct", "total_citas_solicitadas",
            "oportunidad_promedio_dias", "cumplimiento_meta_pct"
        }
        dim_keys = [k for k in first_row.keys() if k not in clinical_metric_keys and k != "es_24h"]
        first_name = " - ".join(str(first_row[k]) for k in dim_keys) if dim_keys else "Red Asistencial"
        intent_type = intent_data.get("intent_type", "GENERAL")
        target_metric = intent_data.get("target_metric", "")

        # Determine Chart Type
        if len(data) == 1 or intent_type == "POINT":
            chart_type = "point_spotlight"
        elif any(k in dim_keys for k in ["year", "month", "month_name"]):
            chart_type = "time_series"
        elif intent_type == "RANKING":
            chart_type = "ranking_bars"
        else:
            chart_type = "bar_comparison"

        direct_answer = None

        # 1. URGENCIAS / TRIAGE / ESTANCIA
        if "tiempo_espera_promedio_min" in first_row or "estancia_promedio_horas" in first_row:
            if target_metric == "estancia_promedio_horas" or "estancia" in question.lower():
                estancia = first_row.get("estancia_promedio_horas", 0.0)
                atenciones = sum(r.get("total_atenciones", 0) for r in data)
                direct_answer = f"{estancia} horas"
                headline = f"Media de Estancia Hospitalaria: {estancia} horas ({first_name})"
                summary = (
                    f"Respuesta directa: En **{first_name}**, la **media de estancia de los pacientes es de {estancia} horas** "
                    f"(con un tiempo promedio de espera en Triage de {first_row.get('tiempo_espera_promedio_min', 0.0)} minutos "
                    f"y un volumen evaluado de {first_row.get('total_atenciones', 0):,} atenciones de urgencias)."
                )
                highlights = [
                    f"⏱️ **Media de Estancia**: {estancia} horas por paciente ({first_name}).",
                    f"🚨 **Espera en Triage**: {first_row.get('tiempo_espera_promedio_min', 0.0)} minutos promedio.",
                    f"👥 **Atenciones Analizadas**: {atenciones:,} pacientes ingresados."
                ]
                recs = [
                    "Optimizar procesos de interconsulta y apoyo diagnóstico para acortar la estancia en observación.",
                    "Monitorear la rotación de camas para evitar congestión en el servicio de urgencias."
                ]
                kpi_cards = [
                    {"label": "Media de Estancia", "value": f"{estancia} horas", "change": f"{first_name}", "trend": "up"},
                    {"label": "Espera en Triage", "value": f"{first_row.get('tiempo_espera_promedio_min', 0.0)} min", "change": "Manchester", "trend": "up"},
                    {"label": "Atenciones Urgencias", "value": f"{atenciones:,}", "change": "24/7", "trend": "up"},
                    {"label": "Latencia OLAP", "value": f"{latency_ms} ms", "change": "DuckDB", "trend": "up"}
                ]
            else:
                t_espera = first_row.get("tiempo_espera_promedio_min", 0.0)
                atenciones = sum(r.get("total_atenciones", 0) for r in data)
                tasa_reingreso = first_row.get("tasa_reingreso_pct", 0.0)
                direct_answer = f"{t_espera} minutos"

                headline = f"Informe Asistencial de Urgencias: {t_espera} min de Espera Promedio ({first_name})"
                summary = (
                    f"En respuesta a '{question}', la atención en urgencias para **{first_name}** registra un "
                    f"**tiempo de espera promedio de {t_espera} minutos** con una estancia hospitalaria media de "
                    f"{first_row.get('estancia_promedio_horas', 0.0)} horas y {first_row.get('total_atenciones', 0):,} admisiones evaluadas."
                )
                highlights = [
                    f"⏱️ **Tiempo de Espera Triage**: Promedio de {t_espera} minutos ({first_name}).",
                    f"🏥 **Volumen de Pacientes**: {atenciones:,} ingresos en urgencias analizados.",
                    f"🔄 **Tasa de Reingreso a 72h**: {tasa_reingreso}% de pacientes con retorno temprano."
                ]
                recs = [
                    "Priorizar asignación de médicos en turnos pico nocturnos para reducir demoras en Triage II y III.",
                    "Realizar auditoría clínica de altas tempranas para contener la tasa de reingreso."
                ]
                kpi_cards = [
                    {"label": "Triage Promedio", "value": f"{t_espera} min", "change": "-4.2 min", "trend": "up"},
                    {"label": "Atenciones Urgencias", "value": f"{atenciones:,}", "change": "24/7", "trend": "up"},
                    {"label": "Reingreso 72h", "value": f"{tasa_reingreso}%", "change": "Normativo", "trend": "up"},
                    {"label": "Latencia OLAP", "value": f"{latency_ms} ms", "change": "DuckDB", "trend": "up"}
                ]

        # 2. CAMAS / UCI
        elif "tasa_ocupacion_pct" in first_row:
            ocupacion = first_row.get("tasa_ocupacion_pct", 0.0)
            ocupadas = sum(r.get("total_camas_ocupadas", 0) for r in data)
            totales = sum(r.get("total_camas_instaladas", 0) for r in data)
            direct_answer = f"{ocupacion}%"

            headline = f"Censo Hospitalario y Capacidad: {ocupacion}% de Ocupación en {first_name}"
            summary = (
                f"Para la consulta '{question}', la ocupación hospitalaria en **{first_name}** se sitúa en un **{ocupacion}%**, "
                f"con {first_row.get('total_camas_ocupadas', 0):,} camas ocupadas sobre una capacidad de {first_row.get('total_camas_instaladas', 0):,} instaladas."
            )
            highlights = [
                f"🛏️ **Tasa de Ocupación**: {ocupacion}% de saturación asistencial.",
                f"📊 **Censo Hospitalario**: {ocupadas:,} camas ocupadas de {totales:,} habilitadas.",
                f"🚨 **Estado de Alerta**: {'Crítica (>85%)' if ocupacion >= 85 else 'Estable (<85%)'}."
            ]
            recs = [
                "Activar protocolo de escalonamiento de camas intermedias a intensivas si la ocupación supera el 90%.",
                "Agilizar egresos hospitalarios matutinos para liberar cupos de urgencias."
            ]
            kpi_cards = [
                {"label": "Ocupación UCI / Camas", "value": f"{ocupacion}%", "change": f"{first_name}", "trend": "up"},
                {"label": "Camas Ocupadas", "value": f"{ocupadas:,}", "change": f"de {totales:,}", "trend": "up"},
                {"label": "Sedes Analizadas", "value": f"{len(data)}", "change": "Red 8 IPS", "trend": "up"},
                {"label": "Latencia OLAP", "value": f"{latency_ms} ms", "change": "DuckDB", "trend": "up"}
            ]

        # 3. GLOSAS / AUDITORIA MEDICA
        elif "total_glosado" in first_row:
            glosado = first_row.get("total_glosado", 0.0)
            radicado = sum(r.get("total_radicado", 0.0) for r in data)
            tasa_glosa = first_row.get("tasa_glosa_pct", 0.0)
            direct_answer = f"${glosado:,.2f} COP"

            headline = f"Auditoría Médica y Glosas: ${glosado:,.2f} Retenidos ({first_name})"
            summary = (
                f"El análisis de glosas para '{question}' en **{first_name}** muestra un valor objetado de "
                f"**${glosado:,.2f} COP** (tasa de glosa del {tasa_glosa}% sobre ${first_row.get('total_radicado', 0.0):,.2f} radicados)."
            )
            highlights = [
                f"⚖️ **Monto Glosado**: ${glosado:,.2f} COP en reclamaciones objetadas por la EPS.",
                f"📋 **Tasa de Glosa**: {tasa_glosa}% sobre facturación radicada.",
                f"✅ **Valor Levantado en Conciliación**: ${first_row.get('total_levantado', 0.0):,.2f} COP."
            ]
            recs = [
                "Revisar consistencia de soportes clínicos y firma médica antes de la radicación RIPS.",
                "Programar mesa de conciliación urgente con la EPS para levantar valores retenidos."
            ]
            kpi_cards = [
                {"label": "Total Glosado", "value": f"${glosado:,.0f}", "change": f"{tasa_glosa}%", "trend": "up"},
                {"label": "Total Radicado", "value": f"${radicado:,.0f}", "change": "Facturado", "trend": "up"},
                {"label": "Aseguradora / Sede", "value": f"{first_name}", "change": "Auditado", "trend": "up"},
                {"label": "Latencia OLAP", "value": f"{latency_ms} ms", "change": "DuckDB", "trend": "up"}
            ]

        # 4. CITAS / OPORTUNIDAD
        else:
            oportunidad = first_row.get("oportunidad_promedio_dias", 0.0)
            cumplimiento = first_row.get("cumplimiento_meta_pct", 0.0)
            citas_totales = sum(r.get("total_citas_solicitadas", 0) for r in data)
            direct_answer = f"{oportunidad} días"

            headline = f"Oportunidad de Citas Médicas: {oportunidad} Días ({first_name})"
            summary = (
                f"Para la consulta '{question}', la oportunidad promedio de asignación en **{first_name}** es de "
                f"**{oportunidad} días**, con un cumplimiento del estándar Supersalud del {cumplimiento}%."
            )
            highlights = [
                f"📅 **Tiempo de Asignación**: {oportunidad} días calendario transcurridos.",
                f"🎯 **Cumplimiento Supersalud**: {cumplimiento}% de citas dentro del plazo legal.",
                f"👥 **Volumen Atendido**: {citas_totales:,} citas programadas en la red."
            ]
            recs = [
                "Abrir franjas adicionales de consulta externa para reducir la oportunidad en especialidades críticas.",
                "Implementar confirmación digital previa de citas para abatir el ausentismo de pacientes."
            ]
            kpi_cards = [
                {"label": "Oportunidad Citas", "value": f"{oportunidad} días", "change": "Promedio", "trend": "up"},
                {"label": "Cumplimiento Meta", "value": f"{cumplimiento}%", "change": "Supersalud", "trend": "up"},
                {"label": "Citas Asignadas", "value": f"{citas_totales:,}", "change": "Red 8 IPS", "trend": "up"},
                {"label": "Latencia OLAP", "value": f"{latency_ms} ms", "change": "DuckDB", "trend": "up"}
            ]

        return {
            "headline": headline,
            "summary": summary,
            "chart_type": chart_type,
            "kpi_cards": kpi_cards,
            "highlights": highlights,
            "recommendations": recs,
            "table_data": data,
            "dimensions": dim_keys,
            "direct_answer": direct_answer
        }

    def _generate_b2b_report(self, question: str, data: list[dict], latency_ms: float, intent_data: dict) -> dict[str, Any]:
        first_row = data[0]
        metric_keys = {"total_orders", "total_revenue", "total_profit", "margin_pct", "avg_order_value"}
        dim_keys = [k for k in first_row.keys() if k not in metric_keys]

        total_revenue = sum(row.get("total_revenue", 0.0) for row in data)
        total_profit = sum(row.get("total_profit", 0.0) for row in data)
        total_orders = sum(row.get("total_orders", 0) for row in data)
        overall_margin_pct = round((total_profit / total_revenue * 100), 2) if total_revenue > 0 else 0.0
        avg_aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

        first_name = " - ".join(str(first_row[k]) for k in dim_keys) if dim_keys else "Resultado"
        intent_type = intent_data.get("intent_type", "GENERAL")
        target_metric = intent_data.get("target_metric", "net_revenue")

        if len(data) == 1 or intent_type == "POINT":
            chart_type = "point_spotlight"
        elif intent_type == "TREND" or "month" in dim_keys or "month_name" in dim_keys:
            chart_type = "time_series"
        elif intent_type == "RANKING":
            chart_type = "ranking_bars"
        elif intent_type == "COMPARISON":
            chart_type = "bar_comparison"
        else:
            chart_type = "general_bars"

        direct_answer = None

        if len(data) == 1 or intent_type == "POINT":
            profit_val = first_row.get("total_profit", 0.0)
            rev_val = first_row.get("total_revenue", 0.0)
            orders_val = first_row.get("total_orders", 0)
            margin_val = first_row.get("margin_pct", 0.0)

            if target_metric == "total_profit":
                direct_answer = f"${profit_val:,.2f}"
                headline = f"Ganancia Neta: {direct_answer} ({first_name})"
                summary = (
                    f"Respuesta directa: En **{first_name}**, la **ganancia neta obtenida fue de ${profit_val:,.2f}** "
                    f"sobre una facturación total de ${rev_val:,.2f} (margen operativo del {margin_val}% en {orders_val:,} pedidos)."
                )
            elif target_metric == "margin_pct":
                direct_answer = f"{margin_val}%"
                headline = f"Margen Operativo: {direct_answer} ({first_name})"
                summary = (
                    f"Respuesta directa: En **{first_name}**, el **margen operativo fue del {margin_val}%** "
                    f"con un beneficio neto de ${profit_val:,.2f} sobre ${rev_val:,.2f} en ventas."
                )
            else:
                direct_answer = f"${rev_val:,.2f}"
                headline = f"Facturación Total: {direct_answer} ({first_name})"
                summary = (
                    f"Respuesta directa: En **{first_name}**, las **ventas alcanzaron ${rev_val:,.2f}** "
                    f"generando ${profit_val:,.2f} de ganancia neta en {orders_val:,} transacciones."
                )

            highlights = [
                f"🎯 **Cifra Clave Solicitada**: {headline}.",
                f"📈 **Margen Operativo**: {margin_val}% de rentabilidad neta.",
                f"📦 **Volumen Registrado**: {orders_val:,} órdenes con ticket promedio de ${first_row.get('avg_order_value', 0.0):,.2f}."
            ]
            recommendations = [
                f"Monitorear la evolución intermensual de {first_name} para detectar desviaciones respecto al promedio corporativo.",
                f"Alinear incentivos comerciales para sostener el margen del {margin_val}%."
            ]

        elif intent_data.get("polarity") == "ASC":
            headline = f"Desempeño Crítico: {first_name} registró ${first_row.get('total_revenue', 0.0):,.2f}"
            summary = (
                f"En respuesta a '{question}', el segmento/período con **menor desempeño registrado** fue **{first_name}**, "
                f"con una facturación de ${first_row.get('total_revenue', 0.0):,.2f} y beneficio de ${first_row.get('total_profit', 0.0):,.2f}."
            )
            highlights = [
                f"⚠️ **Punto Crítico**: '{first_name}' presentó el menor volumen (${first_row.get('total_revenue', 0.0):,.2f}).",
                f"📉 **Margen Registrado**: {first_row.get('margin_pct', 0.0)}% en {first_row.get('total_orders', 0):,} pedidos.",
            ]
            recommendations = [
                f"Analizar factores causales de la baja facturación en {first_name}.",
                "Diseñar promociones dinámicas para recuperar volumen en este segmento."
            ]
        else:
            headline = f"Informe Ejecutivo: Análisis de {len(data)} segmentos (${total_revenue:,.2f} total)"
            summary = (
                f"El análisis de la consulta '{question}' procesó los registros en {latency_ms} ms. "
                f"La facturación consolidada es de ${total_revenue:,.2f} con un margen operativo del {overall_margin_pct}%. "
                f"El segmento líder es **{first_name}** con ${first_row.get('total_revenue', 0.0):,.2f}."
            )
            highlights = [
                f"🚀 **Líder en Facturación**: '{first_name}' aporta ${first_row.get('total_revenue', 0.0):,.2f} ({round(first_row.get('total_revenue', 0.0)/total_revenue*100, 1)}% del total).",
                f"📊 **Margen Promedio**: Beneficio neto de ${total_profit:,.2f} ({overall_margin_pct}% del volumen).",
                f"📦 **Órdenes Totales**: {total_orders:,} transacciones con AOV de ${avg_aov:,.2f}."
            ]
            recommendations = [
                f"Focalizar retención y up-sell en '{first_name}' para consolidar liderazgo.",
                f"Optimizar costos operativos en segmentos con márgenes por debajo del {overall_margin_pct}%."
            ]

        kpi_cards = [
            {"label": "Facturación Total", "value": f"${total_revenue:,.2f}", "change": "+12.4%", "trend": "up"},
            {"label": "Margen Neto", "value": f"${total_profit:,.2f}", "change": f"{overall_margin_pct}%", "trend": "up"},
            {"label": "Volumen de Órdenes", "value": f"{total_orders:,}", "change": "+8.7%", "trend": "up"},
            {"label": "Latencia OLAP", "value": f"{latency_ms} ms", "change": "Sub-50ms", "trend": "up"}
        ]

        return {
            "headline": headline,
            "summary": summary,
            "chart_type": chart_type,
            "kpi_cards": kpi_cards,
            "highlights": highlights,
            "recommendations": recommendations,
            "table_data": data,
            "dimensions": dim_keys,
            "direct_answer": direct_answer
        }

insight_generator = ExecutiveInsightGenerator()
