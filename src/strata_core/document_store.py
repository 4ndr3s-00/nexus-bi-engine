import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid

class AuditorDecision(BaseModel):
    decision: str  # 'Aprobado', 'Glosado', 'Subsanación'
    auditor_id: str
    auditor_name: str
    motivo_glosa: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_decision: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

class MedicalDocumentItem(BaseModel):
    id: str
    numero_radicado: str
    document_type: str  # 'Factura RIPS', 'Incapacidad Médica', 'Fórmula Médica', 'Orden de Procedimiento'
    ips_emisora: str
    eps_receptora: str
    paciente_hash: str
    fecha_radicacion: str
    valor_reclamado: float
    estado: str = "Pendiente"  # 'Pendiente', 'Aprobado', 'Glosado', 'Subsanación'
    prioridad: str = "Media"    # 'Alta', 'Media', 'Baja'
    dias_restantes_normativa: int = 15  # Plazo legal Supersalud (ej. 30 días hábiles)
    
    # Document content / perception metadata
    extracted_text: str
    cie10_code: str
    cie10_desc: str
    medico_tratante: str
    registro_medico: str
    sello_detectado: bool
    firma_detectada: bool
    riesgo_glosa_detectado: bool
    motivo_alerta: Optional[str] = None
    confidence_score: float = 0.96
    
    # Decision history
    historial_auditoria: List[AuditorDecision] = []

    # Custom upload metadata
    image_url: Optional[str] = None
    file_name: Optional[str] = None
    is_user_uploaded: bool = False

class MedicalDocumentStore:
    """
    In-memory / persistent queue of scanned healthcare documents
    for rapid manual review by EPS/IPS auditing personnel.
    """
    def __init__(self):
        self._documents: Dict[str, MedicalDocumentItem] = {}
        self._seed_sample_documents()

    def _seed_sample_documents(self):
        samples = [
            MedicalDocumentItem(
                id="DOC-2026-001",
                numero_radicado="RAD-COL-89201",
                document_type="Factura RIPS",
                ips_emisora="Hospital Universitario Central",
                eps_receptora="Sura EPS",
                paciente_hash="PAC-e48d39c01bf2",
                fecha_radicacion="2026-10-01",
                valor_reclamado=2850000.0,
                estado="Pendiente",
                prioridad="Alta",
                dias_restantes_normativa=8,
                extracted_text="FACTURA CAMBIARIA DE SALUD NO. FC-8921\nIPS: HOSPITAL UNIVERSITARIO CENTRAL - NIT 890.980.123-1\nPACIENTE: HASH-PAC-e48d39c01bf2 | EDAD: 48\nDIAGNÓSTICO: I10 - HIPERTENSIÓN ESENCIAL PRIMARIA\nSERVICIO: URGENCIAS Y OBSERVACIÓN 48H\nMEDICO TRATANTE: DRA. VALENTINA MORALES VELEZ - RM-482910\nFIRMA: DIGITAL VERIFICADA | SELLO DE HABILITACIÓN ACTIVO",
                cie10_code="I10",
                cie10_desc="Hipertensión esencial primaria",
                medico_tratante="Dra. Valentina Morales Vélez",
                registro_medico="RM-482910",
                sello_detectado=True,
                firma_detectada=True,
                riesgo_glosa_detectado=False,
                confidence_score=0.99
            ),
            MedicalDocumentItem(
                id="DOC-2026-002",
                numero_radicado="RAD-COL-89202",
                document_type="Incapacidad Médica",
                ips_emisora="Clínica Norte 24H",
                eps_receptora="Sanitas EPS",
                paciente_hash="PAC-982ab174e501",
                fecha_radicacion="2026-09-25",
                valor_reclamado=420000.0,
                estado="Pendiente",
                prioridad="Media",
                dias_restantes_normativa=14,
                extracted_text="CERTIFICADO DE INCAPACIDAD TEMPORAL\nCLÍNICA NORTE 24H\nPACIENTE CON DIAGNÓSTICO J069 INFECCIÓN RESPIRATORIA AGUDA\nDÍAS DE INCAPACIDAD: 4 DÍAS\nMEDICO: DR. CARLOS ANDRÉS GÓMEZ - RM-771829\nFIRMA: PRESENTE | SELLO: PRESENTE",
                cie10_code="J069",
                cie10_desc="Infección respiratoria aguda de vías superiores",
                medico_tratante="Dr. Carlos Andrés Gómez",
                registro_medico="RM-771829",
                sello_detectado=True,
                firma_detectada=True,
                riesgo_glosa_detectado=False,
                confidence_score=0.97
            ),
            MedicalDocumentItem(
                id="DOC-2026-003",
                numero_radicado="RAD-COL-89203",
                document_type="Factura RIPS",
                ips_emisora="Hospital San Vicente de Paul",
                eps_receptora="Nueva EPS",
                paciente_hash="PAC-3fa81109bc44",
                fecha_radicacion="2026-08-10",
                valor_reclamado=7400000.0,
                estado="Pendiente",
                prioridad="Alta",
                dias_restantes_normativa=2,
                extracted_text="RADICACIÓN COBRO QUIRÚRGICO APENDICECTOMÍA K358\nATENCIÓN REALIZADA HACE 65 DÍAS.\nRADICACIÓN EXTEMPORÁNEA REPORTADA POR SISTEMA.\nSOPORTE DE HISTORIA CLÍNICA SIN FIRMA DEL ESPECIALISTA.",
                cie10_code="K358",
                cie10_desc="Apendicitis aguda con peritonitis",
                medico_tratante="Dr. Sergio Ramírez",
                registro_medico="RM-319082",
                sello_detectado=False,
                firma_detectada=False,
                riesgo_glosa_detectado=True,
                motivo_alerta="GL-04 Radicación extemporánea (>30 días) y GL-02 Falta firma médica en soporte.",
                confidence_score=0.94
            ),
            MedicalDocumentItem(
                id="DOC-2026-004",
                numero_radicado="RAD-COL-89204",
                document_type="Fórmula Médica",
                ips_emisora="Centro Ambulatorio Especializado Sur",
                eps_receptora="Compensar EPS",
                paciente_hash="PAC-b7128cc84a00",
                fecha_radicacion="2026-10-04",
                valor_reclamado=185000.0,
                estado="Pendiente",
                prioridad="Baja",
                dias_restantes_normativa=26,
                extracted_text="PRESCRIPCIÓN MÉDICA NO POS / MIPRES\nDIAGNÓSTICO: E119 DIABETES MELLITUS TIPO 2\nINSULINA GLARGINA 100 UI/ML\nMEDICO: DRA. CAMILA RESTREPO - RM-992144\nFIRMA DIGITAL VALIDA",
                cie10_code="E119",
                cie10_desc="Diabetes mellitus tipo 2 no insulinodependiente",
                medico_tratante="Dra. Camila Restrepo",
                registro_medico="RM-992144",
                sello_detectado=True,
                firma_detectada=True,
                riesgo_glosa_detectado=False,
                confidence_score=0.98
            ),
            MedicalDocumentItem(
                id="DOC-2026-005",
                numero_radicado="RAD-COL-89205",
                document_type="Orden de Procedimiento",
                ips_emisora="Clínica Pediátrica Infantil 24H",
                eps_receptora="Salud Total EPS",
                paciente_hash="PAC-12ab9901aa77",
                fecha_radicacion="2026-10-02",
                valor_reclamado=1250000.0,
                estado="Pendiente",
                prioridad="Alta",
                dias_restantes_normativa=18,
                extracted_text="ORDEN DE RESONANCIA MAGNÉTICA CEREBRAL\nPACIENTE PEDIÁTRICO\nDIAGNÓSTICO: R104 DOLOR ABDOMINAL AGUDO (INCONSISTENCIA: ORDEN NEUROLÓGICA CON DIAGNÓSTICO ABDOMINAL)\nMEDICO: DR. HERNANDO ROJAS - RM-129983",
                cie10_code="R104",
                cie10_desc="Dolor abdominal agudo no especificado",
                medico_tratante="Dr. Hernando Rojas",
                registro_medico="RM-129983",
                sello_detectado=True,
                firma_detectada=True,
                riesgo_glosa_detectado=True,
                motivo_alerta="Inconsistencia de pertinenica médica entre diagnóstico CIE-10 (abdominal) y procedimiento ordenado (RMN cerebral).",
                confidence_score=0.92
            )
        ]
        for doc in samples:
            self._documents[doc.id] = doc

    def list_documents(
        self,
        eps: Optional[str] = None,
        ips: Optional[str] = None,
        estado: Optional[str] = None,
        doc_type: Optional[str] = None
    ) -> List[MedicalDocumentItem]:
        docs = list(self._documents.values())
        if eps:
            docs = [d for d in docs if eps.lower() in d.eps_receptora.lower()]
        if ips:
            docs = [d for d in docs if ips.lower() in d.ips_emisora.lower()]
        if estado:
            docs = [d for d in docs if d.estado.lower() == estado.lower()]
        if doc_type:
            docs = [d for d in docs if d.document_type.lower() == doc_type.lower()]
        return docs

    def get_document(self, doc_id: str) -> Optional[MedicalDocumentItem]:
        return self._documents.get(doc_id)

    def record_decision(
        self,
        doc_id: str,
        decision: str,
        auditor_id: str,
        auditor_name: str,
        motivo_glosa: Optional[str] = None,
        observaciones: Optional[str] = None
    ) -> Optional[MedicalDocumentItem]:
        doc = self._documents.get(doc_id)
        if not doc:
            return None
        
        valid_decisions = ["Aprobado", "Glosado", "Subsanación"]
        if decision not in valid_decisions:
            raise ValueError(f"Decisión inválida '{decision}'. Opciones válidas: {valid_decisions}")

        doc.estado = decision
        audit_record = AuditorDecision(
            decision=decision,
            auditor_id=auditor_id,
            auditor_name=auditor_name,
            motivo_glosa=motivo_glosa,
            observaciones=observaciones
        )
        doc.historial_auditoria.append(audit_record)
        return doc

    def add_document(self, doc: MedicalDocumentItem) -> MedicalDocumentItem:
        """Adds a document to the top of the queue."""
        new_docs = {doc.id: doc}
        new_docs.update(self._documents)
        self._documents = new_docs
        return doc

document_store = MedicalDocumentStore()
