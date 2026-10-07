import React, { useState, useEffect } from 'react';
import { 
  FileCheck2, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Search, 
  Filter, 
  ShieldCheck, 
  ShieldAlert, 
  FileText, 
  Stethoscope, 
  Building2, 
  UserCheck, 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Send,
  Eye,
  Check,
  Ban,
  HelpCircle,
  Activity,
  Calendar,
  Sparkles,
  Upload,
  FileUp,
  Plus
} from 'lucide-react';

export default function DocumentAuditorView({ onRefreshOverview }) {
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [activeFilterEps, setActiveFilterEps] = useState('');
  const [activeFilterEstado, setActiveFilterEstado] = useState('Pendiente');
  const [isLoading, setIsLoading] = useState(false);
  const [showRawText, setShowRawText] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);
  
  // Modal for Glosa reason
  const [showGlosaModal, setShowGlosaModal] = useState(false);
  const [motivoGlosa, setMotivoGlosa] = useState('GL-04 Autorización o radicación extemporánea');
  const [observacionAuditor, setObservacionAuditor] = useState('');
  const [actionSuccessMsg, setActionSuccessMsg] = useState(null);

  // Modal for Uploading Custom Documents
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [docTypeInput, setDocTypeInput] = useState('Factura RIPS');
  const [ipsInput, setIpsInput] = useState('Hospital Universitario Central');
  const [epsInput, setEpsInput] = useState('Sura EPS');
  const [valorInput, setValorInput] = useState(1850000);
  const [clinicalTextInput, setClinicalTextInput] = useState('');
  const [uploadError, setUploadError] = useState(null);

  // Quick sample templates for testing perception
  const sampleTemplates = [
    {
      name: 'Factura RIPS Válida',
      type: 'Factura RIPS',
      ips: 'Hospital Universitario Central',
      eps: 'Sura EPS',
      valor: 2450000,
      text: 'FACTURA RIPS FC-9081\nIPS: HOSPITAL UNIVERSITARIO CENTRAL - NIT 890.980.123-1\nPACIENTE: JUAN PÉREZ - EDAD 52\nDIAGNÓSTICO: I10 HIPERTENSIÓN ESENCIAL PRIMARIA\nSERVICIO: OBSERVACIÓN URGENCIAS Y MEDICACIÓN CARDIOVASCULAR\nMEDICO TRATANTE: DRA. VALENTINA MORALES VELEZ - RM-482910\nFIRMA: DIGITAL AUTORIZADA | SELLO DE HABILITACIÓN ACTIVO'
    },
    {
      name: 'Incapacidad Médica (Sin Firma - Glosa)',
      type: 'Incapacidad Médica',
      ips: 'Clínica Norte 24H',
      eps: 'Sanitas EPS',
      valor: 480000,
      text: 'CERTIFICADO DE INCAPACIDAD TEMPORAL NO. INC-2026-99\nCLÍNICA NORTE 24H\nDIAGNÓSTICO J069 INFECCIÓN RESPIRATORIA AGUDA\nDÍAS DE INCAPACIDAD: 5 DÍAS\nATENCIÓN SIN FIRMA DEL ESPECIALISTA. ILEGIBLE.'
    },
    {
      name: 'Radicación Extemporánea (>30 días)',
      type: 'Factura RIPS',
      ips: 'Hospital San Vicente de Paul',
      eps: 'Nueva EPS',
      valor: 5800000,
      text: 'COBRO QUIRÚRGICO DE APENDICECTOMÍA K358\nATENCIÓN REALIZADA EL 15 DE JULIO (RADICACIÓN EXTEMPORÁNEA REPORTADA HACE 70 DÍAS).\nMEDICO: DR. SERGIO RAMÍREZ - RM-319082\nFIRMA: PRESENTE | SELLO: PRESENTE'
    },
    {
      name: 'Inconsistencia Diagnóstico vs Procedimiento',
      type: 'Orden de Procedimiento',
      ips: 'Centro Ambulatorio Especializado Sur',
      eps: 'Compensar EPS',
      valor: 1350000,
      text: 'SOLICITUD DE RESONANCIA MAGNÉTICA CEREBRAL CONTRASTADA\nDIAGNÓSTICO R104 DOLOR ABDOMINAL AGUDO (INCONSISTENCIA CLÍNICA DETECTADA: ORDEN NEUROLÓGICA CON DIAGNÓSTICO ABDOMINAL)\nDRA. CAMILA RESTREPO - RM-992144\nFIRMA DIGITAL VALIDA'
    }
  ];

  const handleApplyTemplate = (tpl) => {
    setDocTypeInput(tpl.type);
    setIpsInput(tpl.ips);
    setEpsInput(tpl.eps);
    setValorInput(tpl.valor);
    setClinicalTextInput(tpl.text);
  };

  const handleUploadDocument = async (e) => {
    e?.preventDefault();
    setUploadLoading(true);
    setUploadError(null);
    try {
      const formData = new FormData();
      if (uploadFile) {
        formData.append('file', uploadFile);
      }
      formData.append('document_type', docTypeInput);
      formData.append('ips_emisora', ipsInput);
      formData.append('eps_receptora', epsInput);
      formData.append('valor_reclamado', valorInput);
      if (clinicalTextInput) {
        formData.append('raw_text', clinicalTextInput);
      }
      formData.append('prioridad', 'Alta');

      const res = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Error al radicar documento');
      }

      const data = await res.json();
      const newDoc = data.document;

      // Prepend to current list and select it
      setDocuments(prev => [newDoc, ...prev]);
      setSelectedDocId(newDoc.id);
      setShowUploadModal(false);
      setUploadFile(null);
      setClinicalTextInput('');
      setActionSuccessMsg(`¡Documento radicado exitosamente! ${newDoc.numero_radicado} analizado por Strata Core.`);
      setTimeout(() => setActionSuccessMsg(null), 4000);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploadLoading(false);
    }
  };

  // Fetch documents from API
  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      let url = '/api/v1/documents/pending?';
      if (activeFilterEps) url += `eps=${encodeURIComponent(activeFilterEps)}&`;
      if (activeFilterEstado) url += `estado=${encodeURIComponent(activeFilterEstado)}&`;
      
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setDocuments(data.documents || []);
        if (data.documents && data.documents.length > 0) {
          if (!selectedDocId || !data.documents.some(d => d.id === selectedDocId)) {
            setSelectedDocId(data.documents[0].id);
          }
        } else {
          setSelectedDocId(null);
        }
      }
    } catch (err) {
      console.error('Error fetching documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [activeFilterEps, activeFilterEstado]);

  const activeDoc = documents.find(d => d.id === selectedDocId);

  // Submit Auditor Decision
  const handleDecision = async (decision) => {
    if (!activeDoc) return;
    try {
      const payload = {
        document_id: activeDoc.id,
        decision: decision,
        auditor_id: 'AUD-EMP-849',
        auditor_name: 'Auditor Cuentas Médicas EPS',
        motivo_glosa: decision === 'Glosado' ? motivoGlosa : null,
        observaciones: observacionAuditor || (decision === 'Aprobado' ? 'Cumple con soportes normativos.' : 'Se solicita subsanación técnica.')
      };

      const res = await fetch('/api/v1/documents/decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setActionSuccessMsg(`Radicado ${activeDoc.numero_radicado} marcado como ${decision}.`);
        setShowGlosaModal(false);
        setObservacionAuditor('');
        setTimeout(() => setActionSuccessMsg(null), 3500);
        await fetchDocuments();
        if (onRefreshOverview) onRefreshOverview();
      }
    } catch (err) {
      console.error('Error submitting decision:', err);
    }
  };

  // Keyboard shortcut listener for hotkeys (A = Aprobar, G = Glosar, S = Subsanar)
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't trigger if user is typing in textarea or input
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
      if (e.key === 'a' || e.key === 'A') {
        e.preventDefault();
        handleDecision('Aprobado');
      } else if (e.key === 'g' || e.key === 'G') {
        e.preventDefault();
        setShowGlosaModal(true);
      } else if (e.key === 's' || e.key === 'S') {
        e.preventDefault();
        handleDecision('Subsanación');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeDoc, motivoGlosa, observacionAuditor]);

  return (
    <div className="flex-1 flex flex-col p-6 space-y-5 bg-[#0d0e12] overflow-hidden">
      {/* Top Bar: Title & Filter controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#222533] pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                Portal de Auditoría Rápida Strata Core
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  Percepción IA en Vivo
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Auditoría médica documental para las 8 EPS/IPS con validación de CIE-10, firmas y glosas preventivas.
              </p>
            </div>
          </div>
        </div>

        {/* Filter Badges & Selectors */}
        <div className="flex items-center gap-2.5">
          {/* EPS filter */}
          <select 
            value={activeFilterEps} 
            onChange={(e) => setActiveFilterEps(e.target.value)}
            className="bg-[#161822] border border-[#2d3145] text-xs text-slate-200 rounded-xl px-3 py-2 outline-none focus:border-purple-500"
          >
            <option value="">Todas las EPS (8 Red)</option>
            <option value="Sura">Sura EPS</option>
            <option value="Sanitas">Sanitas EPS</option>
            <option value="Nueva EPS">Nueva EPS</option>
            <option value="Salud Total">Salud Total EPS</option>
            <option value="Compensar">Compensar EPS</option>
          </select>

          {/* Status buttons */}
          <div className="flex bg-[#161822] p-1 rounded-xl border border-[#2d3145] text-xs">
            {['Pendiente', 'Aprobado', 'Glosado', 'Subsanación'].map((st) => (
              <button
                key={st}
                onClick={() => setActiveFilterEstado(st)}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  activeFilterEstado === st 
                    ? 'bg-purple-600 text-white shadow-sm' 
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          <div className="text-[11px] text-slate-500 font-mono bg-[#11131a] border border-[#222533] px-3 py-2 rounded-xl">
            {documents.length} radicados
          </div>

          {/* Radicar Mi Documento Button */}
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 hover:brightness-110 active:scale-95 text-white rounded-xl text-xs font-semibold shadow-md shadow-purple-900/30 transition-all shrink-0 cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Radicar Mi Documento</span>
          </button>
        </div>
      </div>

      {/* Success notification banner */}
      {actionSuccessMsg && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-300 flex items-center justify-between animate-fadeIn">
          <span className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            {actionSuccessMsg}
          </span>
          <span className="text-[10px] text-emerald-500 font-mono">Actualizado en Gold Lakehouse</span>
        </div>
      )}

      {/* Document Queue strip */}
      <div className="flex gap-2.5 overflow-x-auto pb-2 scrollbar-thin">
        {documents.map((doc) => {
          const isSelected = doc.id === selectedDocId;
          const isRisk = doc.riesgo_glosa_detectado;
          return (
            <button
              key={doc.id}
              onClick={() => setSelectedDocId(doc.id)}
              className={`shrink-0 w-64 text-left p-3 rounded-xl border transition-all ${
                isSelected 
                  ? 'bg-[#1a1d29] border-purple-500/60 shadow-lg shadow-purple-950/20 ring-1 ring-purple-500/30' 
                  : 'bg-[#141620] border-[#222533] hover:border-[#2d3145] hover:bg-[#181a26]'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5 truncate">
                  <span className="text-[11px] font-mono text-purple-400 font-semibold">{doc.numero_radicado}</span>
                  {doc.is_user_uploaded && (
                    <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      Propio
                    </span>
                  )}
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  doc.estado === 'Aprobado' ? 'bg-emerald-500/20 text-emerald-400' :
                  doc.estado === 'Glosado' ? 'bg-rose-500/20 text-rose-400' :
                  doc.estado === 'Subsanación' ? 'bg-amber-500/20 text-amber-400' :
                  'bg-slate-700/40 text-slate-300'
                }`}>
                  {doc.estado}
                </span>
              </div>
              <div className="text-xs font-semibold text-slate-200 truncate">{doc.document_type}</div>
              <div className="text-[11px] text-slate-400 truncate">{doc.ips_emisora}</div>
              
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-[#222533] text-[10px] text-slate-400">
                <span className="font-mono">${(doc.valor_reclamado / 1000).toLocaleString()}k COP</span>
                {isRisk ? (
                  <span className="flex items-center gap-1 text-rose-400 font-bold">
                    <AlertTriangle className="w-3 h-3" /> Riesgo Glosa
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-emerald-400 font-medium">
                    <Check className="w-3 h-3" /> Limpio
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Main Split-Screen Auditor Workspace */}
      {activeDoc ? (
        <div className="flex-1 grid grid-cols-12 gap-5 min-h-[520px]">
          {/* LEFT PANE: Scanned Medical Document Viewer */}
          <div className="col-span-12 lg:col-span-7 bg-[#12141c] border border-[#222533] rounded-2xl flex flex-col overflow-hidden">
            {/* Viewer Toolbar */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-[#161822] border-b border-[#222533] text-xs">
              <div className="flex items-center gap-2 text-slate-300 font-medium">
                <FileText className="w-4 h-4 text-purple-400" />
                <span>{activeDoc.document_type} - {activeDoc.numero_radicado}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <button 
                  onClick={() => setZoomLevel(Math.max(70, zoomLevel - 15))}
                  className="p-1 rounded hover:bg-[#202330] hover:text-white"
                  title="Alejar"
                >
                  <ZoomOut className="w-3.5 h-3.5" />
                </button>
                <span className="text-[11px] font-mono px-1">{zoomLevel}%</span>
                <button 
                  onClick={() => setZoomLevel(Math.min(150, zoomLevel + 15))}
                  className="p-1 rounded hover:bg-[#202330] hover:text-white"
                  title="Acercar"
                >
                  <ZoomIn className="w-3.5 h-3.5" />
                </button>
                <div className="w-px h-3.5 bg-slate-700 mx-1"></div>
                <button 
                  onClick={() => setShowRawText(!showRawText)}
                  className={`px-2 py-1 rounded text-[11px] font-medium transition-all ${
                    showRawText ? 'bg-purple-600 text-white' : 'hover:bg-[#202330] text-slate-300'
                  }`}
                >
                  {showRawText ? 'Ver Soportes' : 'Ver Texto OCR'}
                </button>
              </div>
            </div>

            {/* Document Content Canvas */}
            <div className="flex-1 p-6 overflow-y-auto bg-[#0b0c10] flex items-center justify-center">
              {showRawText ? (
                <pre className="w-full h-full text-xs font-mono text-slate-300 bg-[#161822] p-4 rounded-xl border border-[#2d3145] whitespace-pre-wrap overflow-y-auto">
                  {activeDoc.extracted_text}
                </pre>
              ) : activeDoc.image_url ? (
                <div 
                  style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
                  className="w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl transition-transform border border-slate-700 bg-black flex flex-col items-center"
                >
                  <img 
                    src={activeDoc.image_url} 
                    alt="Documento Adjunto" 
                    className="w-full h-auto object-contain max-h-[620px] rounded-t-2xl" 
                  />
                  <div className="w-full bg-[#161822] p-3 text-center border-t border-slate-800 text-xs text-slate-300 flex items-center justify-between px-4">
                    <span className="font-mono text-purple-400 font-bold">{activeDoc.numero_radicado}</span>
                    <span className="text-slate-400 truncate max-w-[220px]">{activeDoc.file_name || 'Imagen Escaneada'}</span>
                  </div>
                </div>
              ) : (
                <div 
                  style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
                  className="w-full max-w-lg bg-white text-slate-900 rounded-lg p-8 shadow-2xl transition-transform border border-slate-200"
                >
                  {/* Realistic Scanned Healthcare Document Sheet */}
                  <div className="border-b-2 border-slate-800 pb-4 mb-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-extrabold text-sm uppercase tracking-wide text-slate-900">{activeDoc.ips_emisora}</h3>
                          {activeDoc.is_user_uploaded && (
                            <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 border border-purple-200">
                              Cargado por Auditor
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] text-slate-600 font-mono">NIT: 890.980.123-1 | RESOLUCIÓN HABILITACIÓN 0489</p>
                        <p className="text-[10px] text-slate-600">Sede Principal - Servicios de Salud y Urgencias 24 Horas</p>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-200 rounded font-mono">
                          {activeDoc.numero_radicado}
                        </span>
                        <p className="text-[10px] text-slate-500 mt-1 font-mono">{activeDoc.fecha_radicacion}</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded border border-slate-200">
                      <div>
                        <span className="text-[10px] font-semibold text-slate-500 uppercase block">Paciente (Anonimizado)</span>
                        <span className="font-mono text-slate-800 text-[11px]">{activeDoc.paciente_hash}</span>
                      </div>
                      <div>
                        <span className="text-[10px] font-semibold text-slate-500 uppercase block">EPS Pagadora</span>
                        <span className="font-semibold text-slate-800">{activeDoc.eps_receptora}</span>
                      </div>
                    </div>

                    <div className="border border-slate-200 rounded p-2.5">
                      <span className="text-[10px] font-semibold text-slate-500 uppercase block mb-1">Diagnóstico Principal (CIE-10)</span>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-indigo-100 text-indigo-900 font-mono font-bold rounded">
                          {activeDoc.cie10_code}
                        </span>
                        <span className="font-medium text-slate-800">{activeDoc.cie10_desc}</span>
                      </div>
                    </div>

                    <div className="border border-slate-200 rounded p-2.5">
                      <span className="text-[10px] font-semibold text-slate-500 uppercase block mb-1">Detalle del Radicado / Cuenta Médica</span>
                      <p className="text-[11px] text-slate-700 leading-relaxed font-sans">
                        Atención médica prestada con cargo al contrato de capitación/evento. Incluye insumos médicos, 
                        medicamentos y derechos de estancia hospitalaria según normativa del Ministerio de Salud.
                      </p>
                      <div className="mt-2 text-right">
                        <span className="text-[10px] text-slate-500 block">Total Facturado a Cobro</span>
                        <span className="font-extrabold text-sm text-slate-900 font-mono">
                          ${activeDoc.valor_reclamado.toLocaleString('es-CO', { minimumFractionDigits: 2 })} COP
                        </span>
                      </div>
                    </div>

                    {/* Seal & Doctor Signature Stamp */}
                    <div className="pt-4 mt-4 border-t border-dashed border-slate-300 flex justify-between items-end">
                      <div className="w-32 h-16 border-2 border-indigo-400 rounded-lg p-1.5 flex flex-col justify-center items-center text-center opacity-85 rotate-[-2deg]">
                        <span className="text-[9px] font-bold text-indigo-900 uppercase">SELLO HABILITACIÓN</span>
                        <span className="text-[8px] text-indigo-700 font-mono">MINSALUD COLOMBIA</span>
                        <span className="text-[8px] text-indigo-600 font-mono">REG: 89402-ACT</span>
                      </div>
                      <div className="text-right">
                        <div className="font-serif italic text-slate-800 text-xs tracking-wide">
                          {activeDoc.medico_tratante}
                        </div>
                        <div className="w-36 h-0.5 bg-slate-400 ml-auto my-1"></div>
                        <p className="text-[10px] font-mono text-slate-600">Registro Médico: {activeDoc.registro_medico}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* RIGHT PANE: Strata Core Perception & Action Center */}
          <div className="col-span-12 lg:col-span-5 flex flex-col space-y-4">
            {/* Perception Analysis Card */}
            <div className="bg-[#12141c] border border-[#222533] rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#222533]">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Análisis de Percepción Strata Core</h3>
                    <p className="text-[10px] text-purple-400 font-mono">Qwen 2.5 Vision Engine (:8001)</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-mono font-bold text-emerald-400">{(activeDoc.confidence_score * 100).toFixed(0)}%</span>
                  <span className="text-[10px] text-slate-500 block">Confianza</span>
                </div>
              </div>

              {/* Clinical Consistency Flag */}
              <div className={`p-3 rounded-xl border flex items-start gap-3 ${
                activeDoc.riesgo_glosa_detectado
                  ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                  : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              }`}>
                {activeDoc.riesgo_glosa_detectado ? (
                  <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                ) : (
                  <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                )}
                <div>
                  <h4 className="text-xs font-bold">
                    {activeDoc.riesgo_glosa_detectado ? 'Riesgo Normativo de Glosa Detectado' : 'Consistencia Clínica Verificada'}
                  </h4>
                  <p className="text-[11px] mt-0.5 leading-relaxed opacity-90">
                    {activeDoc.motivo_alerta || 'Los soportes de historia clínica, códigos CIE-10 y firmas cumplen los estándares de la Supersalud.'}
                  </p>
                </div>
              </div>

              {/* Technical Perception Checklist */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-[#161822] p-2.5 rounded-xl border border-[#2d3145]">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Firma del Especialista</span>
                  <div className="flex items-center gap-1.5 mt-1 font-semibold">
                    {activeDoc.firma_detectada ? (
                      <span className="text-emerald-400 flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" /> Válida y Presente
                      </span>
                    ) : (
                      <span className="text-rose-400 flex items-center gap-1">
                        <XCircle className="w-3.5 h-3.5" /> Ausente / Ilegible
                      </span>
                    )}
                  </div>
                </div>

                <div className="bg-[#161822] p-2.5 rounded-xl border border-[#2d3145]">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Sello Habilitación IPS</span>
                  <div className="flex items-center gap-1.5 mt-1 font-semibold">
                    {activeDoc.sello_detectado ? (
                      <span className="text-emerald-400 flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" /> Detectado
                      </span>
                    ) : (
                      <span className="text-amber-400 flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5" /> Sin Sello
                      </span>
                    )}
                  </div>
                </div>

                <div className="bg-[#161822] p-2.5 rounded-xl border border-[#2d3145]">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Médico & Matrícula</span>
                  <div className="mt-1 text-slate-200 truncate font-medium">
                    {activeDoc.medico_tratante}
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">{activeDoc.registro_medico}</span>
                </div>

                <div className="bg-[#161822] p-2.5 rounded-xl border border-[#2d3145]">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Plazo Normativo Legal</span>
                  <div className="flex items-center gap-1 mt-1 font-mono font-bold text-purple-300">
                    <Clock className="w-3.5 h-3.5 text-purple-400" />
                    <span>{activeDoc.dias_restantes_normativa} días restantes</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Auditor Quick Action Card with Hotkeys */}
            <div className="bg-[#12141c] border border-[#222533] rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Acciones del Auditor
                </h4>
                <span className="text-[10px] font-mono text-purple-400">Atajos: [A] [G] [S]</span>
              </div>

              <div className="grid grid-cols-3 gap-2.5">
                {/* Approve Button */}
                <button
                  onClick={() => handleDecision('Aprobado')}
                  className="flex flex-col items-center justify-center p-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/40 transition-all font-semibold text-xs gap-1 active:scale-95 shadow-sm"
                >
                  <Check className="w-5 h-5 text-emerald-400" />
                  <span>Aprobar</span>
                  <span className="text-[9px] text-emerald-500/80 font-mono">[Tecla A]</span>
                </button>

                {/* Glosa Button */}
                <button
                  onClick={() => setShowGlosaModal(true)}
                  className="flex flex-col items-center justify-center p-3 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/40 transition-all font-semibold text-xs gap-1 active:scale-95 shadow-sm"
                >
                  <Ban className="w-5 h-5 text-rose-400" />
                  <span>Glosar</span>
                  <span className="text-[9px] text-rose-500/80 font-mono">[Tecla G]</span>
                </button>

                {/* Subsanación Button */}
                <button
                  onClick={() => handleDecision('Subsanación')}
                  className="flex flex-col items-center justify-center p-3 rounded-xl bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 border border-amber-500/40 transition-all font-semibold text-xs gap-1 active:scale-95 shadow-sm"
                >
                  <HelpCircle className="w-5 h-5 text-amber-400" />
                  <span>Subsanar</span>
                  <span className="text-[9px] text-amber-500/80 font-mono">[Tecla S]</span>
                </button>
              </div>

              {/* Audit history log */}
              {activeDoc.historial_auditoria && activeDoc.historial_auditoria.length > 0 && (
                <div className="pt-3 border-t border-[#222533]">
                  <span className="text-[10px] text-slate-500 uppercase font-semibold block mb-2">Historial de Decisiones</span>
                  <div className="space-y-1.5 max-h-24 overflow-y-auto">
                    {activeDoc.historial_auditoria.map((hist, i) => (
                      <div key={i} className="text-[11px] bg-[#161822] p-2 rounded-lg border border-[#2d3145]">
                        <div className="flex justify-between font-semibold">
                          <span className={hist.decision === 'Aprobado' ? 'text-emerald-400' : 'text-rose-400'}>{hist.decision}</span>
                          <span className="text-slate-500 font-mono text-[10px]">{hist.fecha_decision.split('T')[0]}</span>
                        </div>
                        <p className="text-slate-400 text-[10px] mt-0.5">{hist.observaciones || hist.motivo_glosa}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center p-12 bg-[#12141c] border border-[#222533] rounded-2xl text-center">
          <FileCheck2 className="w-12 h-12 text-slate-600 mb-3" />
          <h3 className="text-base font-bold text-slate-300">No hay documentos con este filtro</h3>
          <p className="text-xs text-slate-500 max-w-sm mt-1">
            Selecciona otro estado o aseguradora para revisar los radicados de la red de 8 EPS/IPS.
          </p>
        </div>
      )}

      {/* Modal for Glosa Decision */}
      {showGlosaModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#151722] border border-[#2d3145] rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-rose-500/20 text-rose-400">
                <Ban className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Objeción de Cuenta Médica (Glosa)</h3>
                <p className="text-xs text-slate-400">Radicado: {activeDoc?.numero_radicado}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Motivo de Glosa Estándar (RIPS)</label>
                <select
                  value={motivoGlosa}
                  onChange={(e) => setMotivoGlosa(e.target.value)}
                  className="w-full bg-[#1c1f2e] border border-[#2d3145] text-xs text-slate-200 rounded-xl p-2.5 outline-none focus:border-rose-500"
                >
                  <option value="GL-04 Autorización o radicación extemporánea">GL-04 Radicación Extemporánea (&gt;30 días)</option>
                  <option value="GL-02 Soporte incompleto / Firma ausente">GL-02 Soporte Incompleto / Falta Firma o Sello</option>
                  <option value="GL-03 Inconsistencia pertinencia médica">GL-03 Inconsistencia Diagnóstico vs Procedimiento</option>
                  <option value="GL-01 Tarifa no pactada / Exceso de valor">GL-01 Tarifa no Pactada en Contrato</option>
                  <option value="GL-05 Falta de autorización previa">GL-05 Falta de Autorización Previa de EPS</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Observaciones Técnicas del Auditor</label>
                <textarea
                  rows={3}
                  value={observacionAuditor}
                  onChange={(e) => setObservacionAuditor(e.target.value)}
                  placeholder="Detalla la justificación clínica o normativa..."
                  className="w-full bg-[#1c1f2e] border border-[#2d3145] text-xs text-slate-200 rounded-xl p-2.5 outline-none focus:border-rose-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2.5 pt-2">
              <button
                onClick={() => setShowGlosaModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-[#202330]"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleDecision('Glosado')}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-900/30"
              >
                Confirmar Glosa
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for Uploading Custom Document */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-[#151722] border border-[#2d3145] rounded-3xl max-w-2xl w-full p-6 shadow-2xl space-y-5 animate-fadeIn my-8 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-[#232635]">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-purple-600 to-indigo-600 text-white shadow-md shadow-purple-900/30">
                  <Upload className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    Radicar Nuevo Documento Médico
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      Motor Strata Core
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Sube un archivo (PDF, imagen JPG/PNG, o texto) para análisis y auditoría inmediata.
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-white text-lg p-1"
              >
                ✕
              </button>
            </div>

            {uploadError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
                {uploadError}
              </div>
            )}

            {/* Quick Templates Buttons */}
            <div>
              <span className="text-xs font-semibold text-slate-400 block mb-2">
                Opciones Rápidas / Plantillas de Prueba Asistencial:
              </span>
              <div className="grid grid-cols-2 gap-2">
                {sampleTemplates.map((tpl, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleApplyTemplate(tpl)}
                    className="text-left p-2.5 rounded-xl bg-[#1c1f2e] hover:bg-purple-900/20 border border-[#2d3145] hover:border-purple-500/40 text-xs text-slate-300 transition-all flex flex-col justify-between"
                  >
                    <span className="font-semibold text-white">{tpl.name}</span>
                    <span className="text-[10px] text-purple-400 mt-1 font-mono">{tpl.type} • {tpl.eps}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Upload Form */}
            <form onSubmit={handleUploadDocument} className="space-y-4">
              {/* File Dropzone */}
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1.5">
                  Archivo Adjunto (PDF, Imagen PNG/JPG o TXT)
                </label>
                <div className="border-2 border-dashed border-[#2d3145] hover:border-purple-500/50 rounded-2xl p-4 text-center bg-[#131520] transition-colors relative cursor-pointer">
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg,.webp,.txt"
                    onChange={(e) => setUploadFile(e.target.files[0] || null)}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="flex flex-col items-center gap-1.5 pointer-events-none">
                    <FileUp className="w-8 h-8 text-purple-400" />
                    <span className="text-xs font-medium text-slate-300">
                      {uploadFile ? (
                        <span className="text-emerald-400 font-semibold">{uploadFile.name} ({(uploadFile.size / 1024).toFixed(1)} KB)</span>
                      ) : (
                        'Arrastra tu archivo aquí o haz clic para explorar'
                      )}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      Formatos soportados: PDF, PNG, JPG, JPEG, TXT
                    </span>
                  </div>
                </div>
              </div>

              {/* Grid: Document Type, IPS, EPS, Amount */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Tipo de Documento</label>
                  <select
                    value={docTypeInput}
                    onChange={(e) => setDocTypeInput(e.target.value)}
                    className="w-full bg-[#1c1f2e] border border-[#2d3145] text-xs text-slate-200 rounded-xl p-2.5 outline-none focus:border-purple-500"
                  >
                    <option value="Factura RIPS">Factura RIPS</option>
                    <option value="Incapacidad Médica">Incapacidad Médica</option>
                    <option value="Fórmula Médica">Fórmula Médica</option>
                    <option value="Orden de Procedimiento">Orden de Procedimiento</option>
                    <option value="Historia Clínica">Historia Clínica</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Valor Reclamado (COP)</label>
                  <input
                    type="number"
                    value={valorInput}
                    onChange={(e) => setValorInput(Number(e.target.value))}
                    min="0"
                    step="50000"
                    className="w-full bg-[#1c1f2e] border border-[#2d3145] text-xs text-slate-200 rounded-xl p-2.5 outline-none focus:border-purple-500 font-mono"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">IPS Emisora (Red Prestadora)</label>
                  <select
                    value={ipsInput}
                    onChange={(e) => setIpsInput(e.target.value)}
                    className="w-full bg-[#1c1f2e] border border-[#2d3145] text-xs text-slate-200 rounded-xl p-2.5 outline-none focus:border-purple-500"
                  >
                    <option value="Hospital Universitario Central">Hospital Universitario Central</option>
                    <option value="Clínica Norte 24H">Clínica Norte 24H</option>
                    <option value="Hospital San Vicente de Paul">Hospital San Vicente de Paul</option>
                    <option value="Centro Ambulatorio Especializado Sur">Centro Ambulatorio Especializado Sur</option>
                    <option value="Clínica Pediátrica Infantil 24H">Clínica Pediátrica Infantil 24H</option>
                    <option value="Hospital Materno Infantil">Hospital Materno Infantil</option>
                    <option value="Clínica Metropolitana Sur">Clínica Metropolitana Sur</option>
                    <option value="Instituto Cardiovascular de Occidente">Instituto Cardiovascular de Occidente</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">EPS Pagadora (Aseguradora)</label>
                  <select
                    value={epsInput}
                    onChange={(e) => setEpsInput(e.target.value)}
                    className="w-full bg-[#1c1f2e] border border-[#2d3145] text-xs text-slate-200 rounded-xl p-2.5 outline-none focus:border-purple-500"
                  >
                    <option value="Sura EPS">Sura EPS</option>
                    <option value="Sanitas EPS">Sanitas EPS</option>
                    <option value="Nueva EPS">Nueva EPS</option>
                    <option value="Salud Total EPS">Salud Total EPS</option>
                    <option value="Compensar EPS">Compensar EPS</option>
                    <option value="Famisanar EPS">Famisanar EPS</option>
                    <option value="Coosalud EPS">Coosalud EPS</option>
                    <option value="Mutual Ser EPS">Mutual Ser EPS</option>
                  </select>
                </div>
              </div>

              {/* Clinical Text Area */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-semibold text-slate-300 block">
                    Texto / Contenido Clínico Escaneado
                  </label>
                  <span className="text-[10px] text-slate-500">
                    {uploadFile ? '(Opcional: Si se adjunta archivo, se extraerá automáticamente)' : '(Obligatorio si no adjuntas archivo)'}
                  </span>
                </div>
                <textarea
                  rows={4}
                  value={clinicalTextInput}
                  onChange={(e) => setClinicalTextInput(e.target.value)}
                  placeholder="Pega aquí el contenido textual de la factura, diagnóstico CIE-10, médico tratante, registro o soportes..."
                  className="w-full bg-[#1c1f2e] border border-[#2d3145] text-xs text-slate-200 rounded-xl p-3 outline-none focus:border-purple-500 font-mono"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#232635]">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  disabled={uploadLoading}
                  className="px-4 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-[#202330] transition-all"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={uploadLoading || (!uploadFile && !clinicalTextInput.trim())}
                  className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 hover:brightness-110 active:scale-95 text-white shadow-lg shadow-purple-900/30 transition-all flex items-center gap-2 disabled:opacity-50"
                >
                  <Sparkles className={`w-3.5 h-3.5 ${uploadLoading ? 'animate-spin' : ''}`} />
                  <span>{uploadLoading ? 'Procesando en Strata Core...' : 'Radicar & Analizar'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
