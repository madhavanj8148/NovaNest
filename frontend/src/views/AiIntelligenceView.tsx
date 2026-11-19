import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Send,
  Database,
  ShieldCheck,
  Code,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  Sliders,
  TrendingUp,
  Cpu,
  Layers,
  HelpCircle,
  Search,
  Zap,
  ArrowRight,
  Copy,
  Check,
  Terminal,
  Calculator,
  BookOpen
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { api, ChatResponse, TelemetryEvent } from '../services/api';
import { AgentTelemetryCard } from '../components/AgentTelemetryCard';
import { ApiErrorState } from '../components/ApiStatePanel';
import { formatTimeToIST } from '../utils/formatters';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: ChatResponse;
  timestamp: string;
}

const CHART_COLORS = ['#2563EB', '#F97316', '#0EA5E9', '#16A34A', '#F59E0B', '#DC2626'];

/**
 * Custom CodeBlock component with copy functionality
 */
const CodeBlock: React.FC<{ language: string; code: string }> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 rounded-xl overflow-hidden border border-slate-800 bg-obsidian-950 font-mono text-xs shadow-lg">
      <div className="flex items-center justify-between px-3.5 py-1.5 bg-slate-900/90 border-b border-slate-800 text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5 font-bold uppercase text-sapphire-400">
          <Terminal size={12} />
          <span>{language || 'code'}</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-0.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          title="Copy code to clipboard"
        >
          {copied ? <Check size={12} className="text-green-600" /> : <Copy size={12} />}
          <span className="text-[10px]">{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      <div className="p-3.5 overflow-x-auto text-slate-200 leading-relaxed font-mono">
        <pre><code>{code}</code></pre>
      </div>
    </div>
  );
};

/**
 * Lightweight, robust Markdown content renderer supporting headers, code blocks,
 * markdown tables, bullet lists, bold text, inline code, and blockquotes.
 */
const FormattedContent: React.FC<{ content: string }> = ({ content }) => {
  if (!content) return null;

  // Split content by code block markers (```)
  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="space-y-2 text-xs sm:text-sm leading-relaxed text-slate-200">
      {parts.map((part, pIdx) => {
        if (part.startsWith('```') && part.endsWith('```')) {
          const firstLineEnd = part.indexOf('\n');
          const lang = part.substring(3, firstLineEnd).trim();
          const code = part.substring(firstLineEnd + 1, part.length - 3).trim();
          return <CodeBlock key={pIdx} language={lang} code={code} />;
        }

        // Parse paragraphs, tables, lists, and headers in non-code text
        const lines = part.split('\n');
        const elements: React.ReactNode[] = [];
        let inTable = false;
        let tableRows: string[][] = [];

        const flushTable = (key: string) => {
          if (tableRows.length > 0) {
            const [header, , ...body] = tableRows;
            elements.push(
              <div key={key} className="my-3 overflow-x-auto rounded-lg border border-slate-800">
                <table className="w-full text-left text-xs border-collapse font-sans">
                  {header && (
                    <thead className="bg-slate-900/90 text-slate-300 border-b border-slate-800 uppercase font-semibold text-[10px]">
                      <tr>
                        {header.map((col, cIdx) => (
                          <th key={cIdx} className="p-2 border-r border-slate-800/60 last:border-r-0">{col.trim()}</th>
                        ))}
                      </tr>
                    </thead>
                  )}
                  <tbody className="divide-y divide-slate-800/60 bg-obsidian-950/60 font-mono text-[11px]">
                    {body.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-800/30">
                        {row.map((cell, cIdx) => (
                          <td key={cIdx} className="p-2 text-slate-300 border-r border-slate-800/40 last:border-r-0 font-sans">{cell.trim()}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
            tableRows = [];
          }
          inTable = false;
        };

        lines.forEach((line, lIdx) => {
          const trimmed = line.trim();

          // Table row detection
          if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
            inTable = true;
            const cells = trimmed.slice(1, -1).split('|');
            tableRows.push(cells);
            return;
          } else if (inTable) {
            flushTable(`tbl_${pIdx}_${lIdx}`);
          }

          if (!trimmed) {
            elements.push(<div key={`sp_${lIdx}`} className="h-1.5" />);
            return;
          }

          // Headers
          if (trimmed.startsWith('### ')) {
            elements.push(
              <h3 key={`h3_${lIdx}`} className="text-sm sm:text-base font-bold text-white mt-3 mb-1 text-sapphire-300">
                {trimmed.replace('### ', '')}
              </h3>
            );
          } else if (trimmed.startsWith('## ')) {
            elements.push(
              <h2 key={`h2_${lIdx}`} className="text-base sm:text-lg font-extrabold text-white mt-4 mb-1.5 text-sapphire-400">
                {trimmed.replace('## ', '')}
              </h2>
            );
          } else if (trimmed.startsWith('# ')) {
            elements.push(
              <h1 key={`h1_${lIdx}`} className="text-lg sm:text-xl font-extrabold text-white mt-4 mb-2">
                {trimmed.replace('# ', '')}
              </h1>
            );
          }
          // Bullet points
          else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            const cleanBullet = trimmed.replace(/^[-*]\s+/, '');
            elements.push(
              <div key={`li_${lIdx}`} className="flex items-start gap-2 pl-2 my-0.5">
                <span className="text-sapphire-400 font-bold mt-1 text-xs">•</span>
                <span className="flex-1">{renderInlineStyles(cleanBullet)}</span>
              </div>
            );
          }
          // Numbered lists
          else if (/^\d+\.\s+/.test(trimmed)) {
            const num = trimmed.match(/^(\d+)\.\s+/)?.[1];
            const cleanText = trimmed.replace(/^\d+\.\s+/, '');
            elements.push(
              <div key={`nli_${lIdx}`} className="flex items-start gap-2 pl-2 my-0.5">
                <span className="text-cyan-400 font-bold font-mono text-xs">{num}.</span>
                <span className="flex-1">{renderInlineStyles(cleanText)}</span>
              </div>
            );
          }
          // Blockquotes
          else if (trimmed.startsWith('> ')) {
            elements.push(
              <blockquote key={`bq_${lIdx}`} className="p-2.5 my-2 border-l-2 border-sapphire-500 bg-sapphire-500/10 rounded-r-lg text-slate-300 italic text-xs">
                {renderInlineStyles(trimmed.replace('> ', ''))}
              </blockquote>
            );
          }
          // General paragraph line
          else {
            elements.push(
              <p key={`p_${lIdx}`} className="my-1">
                {renderInlineStyles(trimmed)}
              </p>
            );
          }
        });

        if (inTable) {
          flushTable(`tbl_${pIdx}_end`);
        }

        return <div key={pIdx}>{elements}</div>;
      })}
    </div>
  );
};

/**
 * Formats inline bold (**text**), italics (*text*), and inline code (`code`)
 */
function renderInlineStyles(text: string): React.ReactNode {
  // First split by inline code
  const codeParts = text.split(/(`[^`]+`)/g);

  return (
    <>
      {codeParts.map((cPart, cIdx) => {
        if (cPart.startsWith('`') && cPart.endsWith('`')) {
          return (
            <code key={cIdx} className="px-1.5 py-0.5 mx-0.5 rounded bg-black/60 border border-slate-800 text-cyan-300 font-mono text-[11px]">
              {cPart.slice(1, -1)}
            </code>
          );
        }

        // Bold formatting
        const boldParts = cPart.split(/(\*\*[^*]+\*\*)/g);
        return (
          <React.Fragment key={cIdx}>
            {boldParts.map((bPart, bIdx) => {
              if (bPart.startsWith('**') && bPart.endsWith('**')) {
                return <strong key={bIdx} className="font-bold text-white">{bPart.slice(2, -2)}</strong>;
              }
              return bPart;
            })}
          </React.Fragment>
        );
      })}
    </>
  );
}

export const AiIntelligenceView: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>(() => `sess_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [liveTelemetry, setLiveTelemetry] = useState<TelemetryEvent[]>([]);
  const [errorObj, setErrorObj] = useState<unknown>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastFailedQuery, setLastFailedQuery] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `### Welcome to NovaNest Universal AI Assistant\n\nI combine **general-purpose technical intelligence** (software engineering, mathematics, machine learning, conceptual problem solving) with **data-grounded Food Delivery Decision Intelligence**.\n\nYou can ask open-ended questions like:\n- *"Explain machine learning in simple words"*\n- *"What is the difference between SQL and NoSQL?"*\n- *"Write a Python program to calculate the average of a list"*\n- *"Calculate compound interest on 2000 at 20% for 2 years"*\n- *"What is our total revenue and cancellation rate?"*\n- *"What happens if commission increases by 2%?"*`,
      timestamp: new Date().toISOString()
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQueries = [
    { label: 'Machine Learning', query: 'Explain machine learning in simple words', icon: Sparkles },
    { label: 'SQL vs NoSQL', query: 'What is the difference between SQL and NoSQL?', icon: Database },
    { label: 'Python Coding', query: 'Write a Python program to calculate the average of a list', icon: Code },
    { label: 'Math & Interest', query: 'Calculate compound interest on 2000 at 20% for 2 years', icon: Calculator },
    { label: 'Platform Revenue', query: 'What is our total revenue?', icon: TrendingUp },
    { label: 'Order Cancellations', query: 'Why are order cancellations increasing?', icon: Search },
    { label: 'What-If Simulation', query: 'What happens if commission increases by 2%?', icon: Sliders },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleAsk = (queryText: string) => {
    const cleanQ = queryText.trim();
    if (!cleanQ || loading) return;

    setErrorObj(null);
    setErrorMsg(null);
    setLastFailedQuery(null);
    const userMsg: Message = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content: cleanQ,
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);
    setLiveTelemetry([]);

    api
      .askAiStream(cleanQ, sessionId, undefined, (evt) => {
        setLiveTelemetry((prev) => [...prev, evt]);
      })
      .then((res) => {
        const assistantMsg: Message = {
          id: `asst_${Date.now()}`,
          role: 'assistant',
          content: res.answer,
          response: res,
          timestamp: res.timestamp || new Date().toISOString()
        };
        setMessages((prev) => [...prev, assistantMsg]);
      })
      .catch((err) => {
        console.error('AskNovaNest Error:', err);
        setLastFailedQuery(cleanQ);
        setErrorObj(err);
        setErrorMsg(
          err?.message || 'Unable to contact the AI Analyst service. Please ensure the local backend is running.'
        );
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleReset = () => {
    const oldId = sessionId;
    const newId = `sess_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    setSessionId(newId);
    api.resetAiSession(oldId).catch((e) => console.warn('Reset error:', e));

    setMessages([
      {
        id: `welcome_${Date.now()}`,
        role: 'assistant',
        content: `Conversation context has been reset. Fresh multi-turn session initialized. What question, coding challenge, or business scenario would you like to explore?`,
        timestamp: new Date().toISOString()
      }
    ]);
    setErrorObj(null);
    setErrorMsg(null);
    setLastFailedQuery(null);
  };

  const renderSuggestedChart = (chart: ChatResponse['suggested_chart']) => {
    if (!chart || !chart.data || chart.data.length === 0) return null;

    return (
      <div className="mt-4 p-4 rounded-xl bg-obsidian-950/80 border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <TrendingUp size={15} className="text-sapphire-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">{chart.title}</h4>
          </div>
          <span className="text-[10px] font-mono uppercase bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
            Interactive {chart.type}
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            {chart.type === 'bar' ? (
              <BarChart data={chart.data} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--theme-chart-grid, #1E293B)" />
                <XAxis
                  dataKey={chart.x_key}
                  tick={{ fill: 'var(--theme-chart-text, #94a3b8)', fontSize: 10 }}
                  interval={0}
                  angle={-15}
                  textAnchor="end"
                />
                <YAxis tick={{ fill: 'var(--theme-chart-text, #94a3b8)', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--theme-tooltip-bg, #0F1622)', borderColor: 'var(--theme-tooltip-border, #334155)', borderRadius: '8px', fontSize: '11px', color: 'var(--theme-tooltip-text, #f8fafc)' }}
                />
                {chart.data[0] && 'Baseline' in chart.data[0] && 'Simulated' in chart.data[0] ? (
                  <>
                    <Bar dataKey="Baseline" fill="var(--theme-chart-axis, #64748b)" radius={[4, 4, 0, 0]} name="Baseline" />
                    <Bar dataKey="Simulated" fill="var(--theme-chart-primary, #3b82f6)" radius={[4, 4, 0, 0]} name="Simulated Scenario" />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px', color: 'var(--theme-chart-text, #94a3b8)' }} />
                  </>
                ) : (
                  <Bar dataKey={chart.y_key} fill="var(--theme-chart-primary, #3b82f6)" radius={[4, 4, 0, 0]}>
                    {chart.data.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                )}
              </BarChart>
            ) : chart.type === 'line' ? (
              <LineChart data={chart.data} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--theme-chart-grid, #1E293B)" />
                <XAxis dataKey={chart.x_key} tick={{ fill: 'var(--theme-chart-text, #94a3b8)', fontSize: 10 }} />
                <YAxis tick={{ fill: 'var(--theme-chart-text, #94a3b8)', fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--theme-tooltip-bg, #0F1622)', borderColor: 'var(--theme-tooltip-border, #334155)', borderRadius: '8px', fontSize: '11px', color: 'var(--theme-tooltip-text, #f8fafc)' }}
                />
                <Line
                  type="monotone"
                  dataKey={chart.y_key}
                  stroke="var(--theme-chart-secondary, #06b6d4)"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: 'var(--theme-chart-secondary, #06b6d4)' }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            ) : (
              <PieChart>
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--theme-tooltip-bg, #0F1622)', borderColor: 'var(--theme-tooltip-border, #334155)', borderRadius: '8px', fontSize: '11px', color: 'var(--theme-tooltip-text, #f8fafc)' }}
                />
                <Pie
                  data={chart.data}
                  dataKey={chart.y_key}
                  nameKey={chart.x_key}
                  cx="50%"
                  cy="50%"
                  outerRadius={75}
                  innerRadius={35}
                  paddingAngle={3}
                >
                  {chart.data.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Legend wrapperStyle={{ fontSize: '10px' }} />
              </PieChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto pb-12">
      {/* HEADER BAR */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-card p-6 border-slate-800 bg-obsidian-900/90 shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-[11px] font-bold uppercase tracking-widest text-sapphire-400 flex items-center gap-1.5">
              <Cpu size={13} /> UNIVERSAL INTELLIGENCE
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-xs text-slate-400">General AI Assistant & Decision Intelligence Analyst</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2.5">
            Ask NovaNest AI
            <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-sapphire-500/10 text-sapphire-300 border border-sapphire-500/30">
              v2.5 Universal
            </span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
            Conversational general AI assistant combined with data-grounded business intelligence, programming assistance, mathematical reasoning, and what-if simulation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="px-3.5 py-2 rounded-xl bg-obsidian-950 hover:bg-slate-800 border border-slate-700 hover:border-slate-600 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
            title="Reset conversation memory and start a new session"
          >
            <RotateCcw size={14} />
            <span>New Chat</span>
          </button>
        </div>
      </div>

      {/* ERROR ALERT */}
      {errorMsg && (
        <ApiErrorState
          title="Ask NovaNest AI Connection Issue"
          error={errorObj || errorMsg}
          onRetry={() => {
            const retryQ = lastFailedQuery;
            setErrorObj(null);
            setErrorMsg(null);
            setLastFailedQuery(null);
            if (retryQ) {
              handleAsk(retryQ);
            }
          }}
        />
      )}

      {/* CONVERSATION THREAD */}
      <div className="space-y-6">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          const res = msg.response;

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-2`}
            >
              {/* Message Header info */}
              <div className="flex items-center gap-2 px-1 text-[11px] text-slate-400">
                <span className="font-semibold text-slate-300">
                  {isUser ? 'User Inquiry' : 'NovaNest AI'}
                </span>
                <span>•</span>
                <span className="font-mono">{formatTimeToIST(msg.timestamp)}</span>
                {res && (
                  <>
                    <span>•</span>
                    <span className="px-2 py-0.5 rounded-md bg-sapphire-950 text-sapphire-300 border border-sapphire-800/60 font-mono text-[10px]">
                      Intent: {res.intent || res.route || 'GENERAL'}
                    </span>
                    {res.provider_status === 'ready' ? (
                      <span className="px-2 py-0.5 rounded-md bg-green-50 text-green-700 border border-green-200 text-[10px] flex items-center gap-1">
                        <Zap size={10} /> Gemini Live LLM
                      </span>
                    ) : res.provider_status === 'mock' ? (
                      <span className="px-2 py-0.5 rounded-md bg-amber-950 text-amber-300 border border-amber-800/60 text-[10px]">
                        Mock AI Provider
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700 text-[10px]">
                        Local Intelligence Engine
                      </span>
                    )}
                  </>
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`w-full max-w-4xl p-5 sm:p-6 rounded-2xl ${
                  isUser
                    ? 'bg-sapphire-600/15 border border-sapphire-500/30 text-white shadow-lg'
                    : 'glass-card border-slate-800 bg-obsidian-900/95 shadow-xl text-slate-200'
                }`}
              >
                {/* Resolved Query Callout if contextual */}
                {res?.resolved_query && (
                  <div className="mb-4 p-2.5 rounded-lg bg-sapphire-950/60 border border-sapphire-800/50 text-[11px] text-sapphire-300 flex items-center gap-2">
                    <Sliders size={13} className="text-sapphire-400 flex-shrink-0" />
                    <span>
                      <strong>Contextual follow-up resolved to:</strong> "{res.resolved_query}"
                    </span>
                  </div>
                )}

                {/* PHASE 06.5 MULTI-AGENT TELEMETRY CARD */}
                {res && res.agents_invoked && res.agents_invoked.length > 0 && (
                  <AgentTelemetryCard
                    agentsInvoked={res.agents_invoked}
                    verificationOutcome={res.verification_outcome}
                    isVerified={res.grounding_verified}
                    totalElapsedMs={res.agents_invoked.reduce((acc, a) => acc + (a.elapsed_ms || 0), 0)}
                    isLive={false}
                  />
                )}

                {/* PHASE 06.3 ORCHESTRATION & VERIFICATION TELEMETRY BAR */}
                {res && (res.agents_invoked?.length || res.verification_outcome || res.orchestration_mode) && (
                  <div className="mb-4 p-3 rounded-xl bg-obsidian-950/85 border border-slate-800/90 space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-[10px]">
                      <div className="flex flex-wrap items-center gap-1.5">
                        {res.orchestration_mode && (
                          <span className="px-2 py-0.5 rounded bg-sapphire-500/15 border border-sapphire-500/30 text-sapphire-300 font-mono uppercase">
                            {res.orchestration_mode.replace('_', ' ')}
                          </span>
                        )}
                        {res.verification_outcome && (
                          <span
                            className={`px-2 py-0.5 rounded font-semibold uppercase flex items-center gap-1 border ${
                              res.grounding_verified
                                ? 'bg-green-50 border-green-200 text-green-700'
                                : res.verification_outcome === 'partial'
                                ? 'bg-amber-50 border-amber-200 text-amber-700'
                                : 'bg-red-50 border-red-200 text-red-700'
                            }`}
                          >
                            <CheckCircle size={11} />
                            Verification: {res.verification_outcome}
                          </span>
                        )}
                      </div>
                      {res.trace_id && (
                        <span className="text-slate-500 font-mono">Trace: {res.trace_id}</span>
                      )}
                    </div>

                    {res.agents_invoked && res.agents_invoked.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <span className="text-[10px] font-semibold text-slate-500 mr-1">Agents:</span>
                        {res.agents_invoked.map((ag, aIdx) => (
                          <span
                            key={`${ag.agent_id}_${aIdx}`}
                            className={`text-[10px] px-2 py-0.5 rounded-md font-mono border ${
                              ag.status === 'success'
                                ? 'bg-green-50 border-green-200 text-green-700'
                                : ag.status === 'partial'
                                ? 'bg-amber-50 border-amber-200 text-amber-700'
                                : 'bg-red-50 border-red-200 text-red-700'
                            }`}
                          >
                            S{ag.stage} • {ag.agent_id} ({ag.status}, {Math.round(ag.elapsed_ms)}ms)
                          </span>
                        ))}
                      </div>
                    )}

                    {res.data_source_badges && res.data_source_badges.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <span className="text-[10px] font-semibold text-slate-400 mr-1">Sources:</span>
                        {res.data_source_badges.slice(0, 8).map((badge, bIdx) => (
                          <span
                            key={bIdx}
                            className="text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-700/70 text-slate-300 font-mono"
                          >
                            {badge}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Formatted Content Body */}
                <FormattedContent content={msg.content} />

                {/* VERIFIED METRICS KPI ROW (Only when present and not empty) */}
                {res?.verified_metrics && res.verified_metrics.length > 0 && (
                  <div className="mt-5 pt-4 border-t border-slate-800/80">
                    <div className="flex items-center gap-1.5 mb-2.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      <Database size={13} className="text-sapphire-400" />
                      <span>Verified Business Metrics</span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                      {res.verified_metrics.map((m, mIdx) => (
                        <div
                          key={mIdx}
                          className="p-3 rounded-xl bg-obsidian-950 border border-slate-800/80 hover:border-slate-700 transition-colors"
                        >
                          <div className="text-[10px] text-slate-400 truncate">{m.label}</div>
                          <div className="text-base sm:text-lg font-extrabold text-white font-mono mt-0.5">
                            {String(m.value)}
                          </div>
                          {m.delta && (
                            <div className="text-[10px] text-green-600 font-semibold mt-0.5">{m.delta}</div>
                          )}
                          {m.provenance && (
                            <div className="text-[9px] text-slate-500 truncate mt-1">Source: {m.provenance}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* INTERACTIVE CHART VISUALIZATION */}
                {res?.suggested_chart && renderSuggestedChart(res.suggested_chart)}

                {/* ROOT CAUSE ANALYSIS BREAKDOWN */}
                {res?.root_cause_analysis && (
                  <div className="mt-5 p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3.5">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                      <div className="flex items-center gap-2">
                        <Search size={14} className="text-amber-500" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                          Root-Cause Investigation: {res.root_cause_analysis.investigation_target}
                        </h4>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
                        Evidence Grounded
                      </span>
                    </div>

                    {/* Observed Facts */}
                    <div>
                      <div className="text-[11px] font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
                        <CheckCircle size={12} className="text-green-600" /> Confirmed Empirical Facts:
                      </div>
                      <ul className="list-disc list-inside text-xs text-slate-400 space-y-0.5 pl-1">
                        {res.root_cause_analysis.observed_facts.map((fact, fIdx) => (
                          <li key={fIdx}>{fact}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Contributing Factors */}
                    {res.root_cause_analysis.contributing_factors.length > 0 && (
                      <div>
                        <div className="text-[11px] font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                          <Layers size={12} className="text-sapphire-400" /> Contributing Factors & Evidence:
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {res.root_cause_analysis.contributing_factors.map((cf, cIdx) => (
                            <div key={cIdx} className="p-2.5 rounded-lg bg-obsidian-900 border border-slate-800 text-xs">
                              <div className="flex items-center justify-between text-[11px] font-bold text-slate-200">
                                <span>{cf.factor}</span>
                                <span className="text-[10px] text-sapphire-400 bg-sapphire-500/10 px-1.5 py-0.5 rounded">
                                  {cf.correlation || (cf as any).correlation_strength || 'Observed'}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-400 mt-1">{cf.evidence}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Uncertainties */}
                    {res.root_cause_analysis.uncertainties.length > 0 && (
                      <div className="p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-200/80">
                        <div className="font-semibold flex items-center gap-1 text-amber-300 mb-0.5">
                          <HelpCircle size={12} /> Stated Uncertainties & Missing Observations:
                        </div>
                        <ul className="list-disc list-inside space-y-0.5 pl-1">
                          {res.root_cause_analysis.uncertainties.map((u, uIdx) => (
                            <li key={uIdx}>{u}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* DECISION SIMULATION SUMMARY */}
                {res?.simulation_results && (
                  <div className="mt-5 p-4 rounded-xl bg-obsidian-950/90 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <Sliders size={14} className="text-sapphire-400" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-sapphire-300">
                          Decision Simulator: {res.simulation_results.scenario_name}
                        </h4>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-sapphire-500/10 text-sapphire-300 border border-sapphire-500/20">
                        Scenario Engine Output
                      </span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      <div className="p-2.5 rounded-lg bg-obsidian-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400">Revenue Impact</div>
                        <div
                          className={`text-sm font-extrabold font-mono mt-0.5 ${
                            res.simulation_results.financial_impact.revenue_diff >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {res.simulation_results.financial_impact.revenue_diff >= 0 ? '+' : ''}₹
                          {res.simulation_results.financial_impact.revenue_diff.toLocaleString()}
                        </div>
                      </div>
                      <div className="p-2.5 rounded-lg bg-obsidian-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400">Margin Shift</div>
                        <div
                          className={`text-sm font-extrabold font-mono mt-0.5 ${
                            res.simulation_results.financial_impact.margin_diff_pct >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {res.simulation_results.financial_impact.margin_diff_pct >= 0 ? '+' : ''}
                          {res.simulation_results.financial_impact.margin_diff_pct.toFixed(2)}%
                        </div>
                      </div>
                      <div className="p-2.5 rounded-lg bg-obsidian-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400">Recommended Stance</div>
                        <div className="text-xs font-bold text-amber-300 mt-0.5">
                          {res.simulation_results.recommendation.Decision}
                        </div>
                      </div>
                      <div className="p-2.5 rounded-lg bg-obsidian-900 border border-slate-800">
                        <div className="text-[10px] text-slate-400">Key Risk Factor</div>
                        <div className="text-[10px] text-slate-300 mt-0.5 truncate" title={res.simulation_results.recommendation.Main_Risk}>
                          {res.simulation_results.recommendation.Main_Risk}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* SQL QUERY & SECURITY AUDIT (Only when present and not empty) */}
                {res?.sql_query && res.sql_query.trim().length > 0 && (
                  <div className="mt-4 p-3.5 rounded-xl bg-obsidian-950/90 border border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-300">
                        <Code size={14} className="text-cyan-400" />
                        <span>SQL Security Audit & Execution</span>
                      </div>
                      <div
                        className={`flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full border ${
                          res.sql_valid
                            ? 'bg-green-50 text-green-700 border-green-200'
                            : 'bg-red-50 text-red-700 border-red-200'
                        }`}
                      >
                        <ShieldCheck size={12} /> {res.validation_message || (res.sql_valid ? 'Validated Read-Only SELECT' : 'Rejected')}
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-black/60 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto">
                      <code>{res.sql_query}</code>
                    </div>
                  </div>
                )}

                {/* VERIFIED DATA TABLE (Only when rows exist) */}
                {res?.data_rows && res.data_rows.length > 0 && (
                  <div className="mt-4 p-3.5 rounded-xl bg-obsidian-950 border border-slate-800">
                    <div className="flex items-center gap-1.5 mb-2.5 text-xs font-bold text-slate-200">
                      <Database size={13} className="text-sapphire-400" />
                      <span>Verified Dataset Rows ({res.data_rows.length} rows returned)</span>
                    </div>
                    <div className="overflow-x-auto max-h-56 scrollbar-thin">
                      <table className="w-full text-left text-[11px]">
                        <thead className="sticky top-0 bg-obsidian-900 border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                          <tr>
                            {Object.keys(res.data_rows[0]).map((col) => (
                              <th key={col} className="pb-1.5 px-2 font-semibold">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-mono">
                          {res.data_rows.map((row, rIdx) => (
                            <tr key={rIdx} className="hover:bg-slate-800/30">
                              {Object.values(row).map((val: any, cIdx) => (
                                <td key={cIdx} className="py-1.5 px-2 text-slate-300">
                                  {String(val)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* KPI FORMULA / CALCULATION EXPLANATIONS */}
                {res?.calculation_steps && res.calculation_steps.length > 0 && (
                  <details className="mt-4 p-3 rounded-xl bg-obsidian-950/90 border border-slate-800 text-xs">
                    <summary className="cursor-pointer font-bold text-slate-300 flex items-center gap-1.5 select-none">
                      <Calculator size={13} className="text-cyan-400" />
                      <span>Certified KPI Formulas & Calculation Trace ({res.calculation_steps.length})</span>
                    </summary>
                    <div className="mt-2.5 space-y-1.5 text-[11px]">
                      {res.calculation_steps.map((step, sIdx) => (
                        <div key={sIdx} className="p-2 rounded bg-slate-900/70 border border-slate-800/70 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
                          <div>
                            <span className="font-semibold text-white">{step.name}</span>
                            {step.kpi_id && <span className="ml-1.5 text-[10px] text-cyan-400 font-mono">[{step.kpi_id}]</span>}
                            <div className="text-[10px] text-slate-400 font-mono">{step.formula}</div>
                          </div>
                          <div className="text-right">
                            <span className="font-mono font-bold text-green-700">
                              {String(step.value)} {step.unit || ''}
                            </span>
                            {step.source_tables && (
                              <div className="text-[9px] text-slate-500">{step.source_tables}</div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                {/* EXPERIMENTAL ML WARNINGS */}
                {res?.ml_confidence_warnings && res.ml_confidence_warnings.length > 0 && (
                  <div className="mt-4 p-3 rounded-xl bg-amber-950/30 border border-amber-700/40 text-xs space-y-1">
                    <div className="font-bold text-amber-300 flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                      <AlertTriangle size={13} />
                      <span>Experimental ML Disclosures (Not Production-Ready)</span>
                    </div>
                    <ul className="list-disc list-inside text-[11px] text-amber-200/90 space-y-0.5">
                      {res.ml_confidence_warnings.map((warn, wIdx) => (
                        <li key={wIdx}>{warn}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* LIMITATIONS / PARTIAL FAILURES */}
                {res?.limitations && res.limitations.length > 0 && (
                  <div className="mt-4 p-3 rounded-xl bg-crimson-950/30 border border-crimson-700/40 text-xs space-y-1">
                    <div className="font-bold text-crimson-300 flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                      <AlertTriangle size={13} />
                      <span>Partial Coverage & Limitations</span>
                    </div>
                    <ul className="list-disc list-inside text-[11px] text-crimson-200/90 space-y-0.5">
                      {res.limitations.map((lim, lIdx) => (
                        <li key={lIdx}>{lim}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* RECOMMENDATIONS */}
                {res?.recommendations && res.recommendations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800/80">
                    <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                      <Zap size={13} className="text-amber-400" />
                      <span>Actionable Recommendations</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {res.recommendations.map((rec, rIdx) => (
                        <div key={rIdx} className="p-2.5 rounded-lg bg-obsidian-950 border border-slate-800 text-xs">
                          <div className="font-bold text-white text-[11px]">{rec.title}</div>
                          <div className="text-[10px] text-slate-400 mt-1">{rec.evidence}</div>
                          <div className="text-[10px] text-blue-600 font-semibold mt-1">
                            Action: {rec.action}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* CONTEXT-AWARE FOLLOW-UP SUGGESTIONS */}
                {res?.follow_up_suggestions && res.follow_up_suggestions.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800/80">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                      Suggested Follow-Up Explorations:
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {res.follow_up_suggestions.map((sug, sIdx) => (
                        <button
                          key={sIdx}
                          onClick={() => handleAsk(sug)}
                          className="text-[11px] px-2.5 py-1 rounded-lg bg-obsidian-950 hover:bg-sapphire-600/20 border border-slate-800 hover:border-sapphire-500/40 text-slate-300 hover:text-white transition-all text-left flex items-center gap-1.5"
                        >
                          <span>{sug}</span>
                          <ArrowRight size={11} className="text-sapphire-400" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* PROVENANCE FOOTER */}
                {res?.provenance && (
                  <div className="mt-4 pt-2 border-t border-slate-800/50 flex flex-wrap items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Engine: {res.provenance.data_source}</span>
                    <span>Access Mode: {res.provenance.access_mode || 'Secure Read-Only'}</span>
                    <span>Multi-Turn Session: Active</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex flex-col space-y-3 w-full">
            <div className="glass-card p-3 rounded-xl border-slate-800 bg-obsidian-900/90 text-slate-300 text-xs flex items-center gap-3">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-cyan-400 border-t-transparent" />
              <span>Coordinating domain intelligence agents and verifying business metrics...</span>
            </div>
            {liveTelemetry.length > 0 && (
              <AgentTelemetryCard events={liveTelemetry} isLive={true} />
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* INPUT AREA */}
      <div className="glass-card p-4 sm:p-5 border-slate-700 bg-obsidian-900/95 sticky bottom-4 shadow-2xl z-20">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk(question);
          }}
          className="flex items-center gap-3"
        >
          <div className="relative flex-1">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything (e.g. 'Explain ML in simple words', 'Calculate compound interest...', 'What is our total revenue?', 'Write Python code...')"
              className="w-full bg-obsidian-950 border border-slate-700 rounded-xl pl-4 pr-10 py-3 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sapphire-500 transition-colors"
            />
            <Sparkles className="absolute right-3.5 top-3.5 text-sapphire-400" size={16} />
          </div>
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-5 py-3 rounded-xl bg-sapphire-600 hover:bg-sapphire-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-semibold text-xs sm:text-sm flex items-center gap-2 transition-all shadow-lg shadow-sapphire-500/25 flex-shrink-0"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            ) : (
              <Send size={15} />
            )}
            <span className="hidden sm:inline">Ask AI</span>
          </button>
        </form>

        {/* Global Suggested Starter Prompts */}
        <div className="mt-3 pt-3 border-t border-slate-800/80">
          <div className="flex items-center gap-1 text-[11px] text-slate-400 mb-1.5 font-medium">
            <BookOpen size={13} className="text-sapphire-400" />
            <span>Universal Starter Inquiries (General, Programming, Math & Business):</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {suggestedQueries.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={() => handleAsk(item.query)}
                  className="text-[11px] px-2.5 py-1 rounded-lg bg-obsidian-950 hover:bg-sapphire-600/20 border border-slate-800 hover:border-sapphire-500/40 text-slate-300 hover:text-white transition-all text-left flex items-center gap-1.5"
                >
                  <Icon size={12} className="text-sapphire-400" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
