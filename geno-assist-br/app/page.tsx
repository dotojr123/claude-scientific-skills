import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Upload, FileText, Activity, Search, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function Home() {
  const [variant, setVariant] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!variant) return;
    setLoading(true);
    setError('');
    setReport(null);

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          variant: variant,
          api_keys: { OPENAI_API_KEY: apiKey } // Or GOOGLE_API_KEY
        })
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setReport(data);
      }
    } catch (err) {
      setError('Falha na conexão com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="text-blue-600 h-6 w-6" />
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-700 to-blue-500 bg-clip-text text-transparent">
              GenoAssist BR
            </h1>
            <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-medium">BETA</span>
          </div>
          <div className="text-sm text-slate-500 hidden sm:block">
            Assistente de Genética Clínica
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10 space-y-8">

        {/* Intro */}
        <section className="text-center space-y-4 max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold tracking-tight text-slate-800">
            Do VCF ao Laudo em segundos.
          </h2>
          <p className="text-slate-600 text-lg">
            Analise variantes genéticas com a precisão do ClinVar e a fluidez da IA,
            gerando relatórios prontos em Português.
          </p>
        </section>

        {/* Input Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 sm:p-8 max-w-2xl mx-auto space-y-6">

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Variante (HGVS ou Gene + Alteração)
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Ex: BRCA1 c.68_69del ou TP53 R175H"
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  value={variant}
                  onChange={(e) => setVariant(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                API Key (OpenAI ou Gemini)
                <span className="text-slate-400 font-normal text-xs ml-2">(Opcional se configurado no servidor)</span>
              </label>
              <input
                type="password"
                placeholder="sk-..."
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none transition-all font-mono text-sm"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              onClick={handleAnalyze}
              disabled={loading || !variant}
              className={`w-full py-3 px-4 rounded-lg font-medium text-white shadow-sm transition-all flex items-center justify-center gap-2
                ${loading || !variant
                  ? 'bg-slate-300 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 active:scale-[0.98]'}`}
            >
              {loading ? (
                <>
                  <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analisando bases de dados...
                </>
              ) : (
                <>
                  <FileText className="h-5 w-5" />
                  Gerar Laudo Clínico
                </>
              )}
            </button>
          </div>

          <div className="bg-slate-50 rounded-lg p-4 border border-slate-100 flex gap-3">
             <div className="p-2 bg-blue-100 rounded-full h-fit">
                <Upload className="h-4 w-4 text-blue-600" />
             </div>
             <div>
                <h4 className="text-sm font-semibold text-slate-800">Upload de VCF</h4>
                <p className="text-xs text-slate-500 mt-0.5">
                  Em breve: Arraste seu arquivo .vcf ou .txt para analisar lote de variantes.
                </p>
             </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto bg-red-50 border border-red-100 rounded-lg p-4 flex gap-3 text-red-700">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Results Area */}
        {report && (
          <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Status Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                <div className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">ClinVar</div>
                <div className="flex items-center gap-2">
                  {report.clinvar_data.found ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      <span className="font-semibold text-slate-800">Encontrado</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-4 w-4 text-amber-500" />
                      <span className="font-semibold text-slate-800">Não listado</span>
                    </>
                  )}
                </div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                 <div className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">Literatura</div>
                 <div className="font-semibold text-slate-800">
                    {report.pubmed_count} artigos recentes
                 </div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                 <div className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">Classificação</div>
                 <div className="font-semibold text-slate-800 truncate" title={report.clinvar_data.clinical_significance}>
                    {report.clinvar_data.clinical_significance || "Em análise"}
                 </div>
              </div>
            </div>

            {/* Main Report */}
            <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  Laudo Genético Preliminar
                </h3>
                <button className="text-xs font-medium text-blue-600 hover:text-blue-700 hover:underline">
                  Baixar PDF
                </button>
              </div>

              <div className="p-8 prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-800 prose-p:text-slate-600 prose-strong:text-slate-900">
                <ReactMarkdown>{report.report}</ReactMarkdown>
              </div>

              <div className="bg-amber-50 px-6 py-4 border-t border-amber-100 text-xs text-amber-800 flex gap-2">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <p>
                  <strong>Aviso Legal:</strong> Este relatório é gerado por Inteligência Artificial (GenoAssist BR) e serve apenas como suporte à decisão.
                  A validação final deve ser realizada por um geneticista certificado. Não utilize para diagnóstico direto sem revisão humana.
                </p>
              </div>
            </div>

          </div>
        )}

      </main>
    </div>
  );
}
