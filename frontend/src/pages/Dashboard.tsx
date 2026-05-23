// frontend/src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
// Ensure you target 'raptor_token' to perfectly align with your login pipeline payload
const token = localStorage.getItem('raptor_token') || '';

interface HealthData {
  backend: string;
  postgresql: string;
  binance_api: string;
  llm_api: string;
}

export const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [wsMessages, setWsMessages] = useState<string[]>([]);
  const [wsStatus, setWsStatus] = useState<string>('Disconnected');
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [inputFrame, setInputFrame] = useState<string>('');

  // Extract the access token minted by the auth layer
  const token = localStorage.getItem('access_token') || '';

  // Ingest health diagnostics on component mount
  useEffect(() => {
    fetch('http://localhost:8000/api/health')
      .then((res) => res.json())
      .then((resBody) => {
        if (resBody.success) {
          setHealth(resBody.data);
        }
      })
      .catch((err) => console.error('Failed to query system telemetry:', err))
      .finally(() => setLoadingHealth(false));
  }, []);

  // Initialize the authenticated real-time network handshake
  const handleTestWebSocket = () => {
    if (socket) {
      socket.close();
    }

    const wsUrl = `ws://localhost:8000/ws/test?token=${encodeURIComponent(token)}`;
    const wsInstance = new WebSocket(wsUrl);

    setWsStatus('Connecting');

    wsInstance.onopen = () => {
      setWsStatus('Connected');
      setWsMessages((prev) => [...prev, '[SYSTEM]: Handshake validated. Pipe active.']);
    };

    wsInstance.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setWsMessages((prev) => [...prev, `[INBOUND - ${data.event.toUpperCase()}]: ${JSON.stringify(data.payload || data.details)}`]);
    };

    wsInstance.onclose = (event) => {
      setWsStatus('Disconnected');
      setWsMessages((prev) => [...prev, `[SYSTEM]: Connection dropped. Code: ${event.code}. Reason: ${event.reason || 'None'}`]);
      setSocket(null);
    };

    wsInstance.onerror = () => {
      setWsStatus('Error');
    };

    setSocket(wsInstance);
  };

  const sendEchoFrame = (e: React.FormEvent) => {
    e.preventDefault();
    if (socket && wsStatus === 'Connected' && inputFrame.trim()) {
      socket.send(inputFrame);
      setWsMessages((prev) => [...prev, `[OUTBOUND]: ${inputFrame}`]);
      setInputFrame('');
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 font-mono selection:bg-emerald-500 selection:text-black">
      {/* Top Console Navigation Banner */}
      <header className="border-b border-slate-800 bg-[#0c1322] px-6 py-4 flex items-center justify-between shadow-md">
        <div className="flex items-center space-x-3">
          <div className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]" />
          <h1 className="text-md font-bold tracking-wider text-slate-200">
            RAPTOR_LEDGER // <span className="text-emerald-400">OPS_CONSOLE_V3</span>
          </h1>
        </div>
        <div className="text-xs text-slate-500 hidden sm:block">
          SYS_STATUS: <span className="text-emerald-500 font-bold">OPERATIONAL</span>
        </div>
      </header>

      {/* Main Workspace Layout Grid */}
      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left Column: Diagnostics Card */}
        <section className="lg:col-span-1 bg-[#0c1322] border border-slate-800 rounded-lg p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <h2 className="text-xs uppercase tracking-widest font-bold text-slate-400">System Core Matrix</h2>
              <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-750">GET /health</span>
            </div>

            {loadingHealth ? (
              <div className="text-xs text-slate-500 animate-pulse">Pinging telemetry streams...</div>
            ) : (
              <div className="space-y-3">
                {health && Object.entries(health).map(([node, status]) => {
                  const isHealthy = status === 'healthy';
                  return (
                    <div
                      key={node}
                      className="flex items-center justify-between p-3 rounded bg-[#111a2e] border border-slate-800/60"
                    >
                      <span className="text-xs text-slate-400 tracking-wide">{node.toUpperCase()}</span>
                      <span className={`text-xs font-bold px-2.5 py-1 rounded uppercase tracking-wider transition-all duration-300 ${
                        isHealthy
                          ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-800/50 shadow-[0_0_12px_rgba(16,185,129,0.05)]'
                          : 'bg-rose-950/40 text-rose-400 border border-rose-800/50'
                      }`}>
                        {status}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/50 text-[11px] text-slate-500">
            Operational statuses evaluate state loops dynamically without throwing top-level exception signatures.
          </div>
        </section>

        {/* Right Column: WebSockets Terminal Control */}
        <section className="lg:col-span-2 bg-[#0c1322] border border-slate-800 rounded-lg p-5 shadow-xl flex flex-col">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <h2 className="text-xs uppercase tracking-widest font-bold text-slate-400">Socket Telemetry Pipe</h2>

            {/* Context Status Badge */}
            <span className={`text-[11px] px-2.5 py-0.5 font-bold rounded border ${
              wsStatus === 'Connected' ? 'bg-emerald-950/50 text-emerald-400 border-emerald-800' :
              wsStatus === 'Connecting' ? 'bg-amber-950/50 text-amber-400 border-amber-800' :
              'bg-slate-800 text-slate-400 border-slate-700'
            }`}>
              {wsStatus.toUpperCase()}
            </span>
          </div>

          <div className="mb-4">
            <button
              onClick={handleTestWebSocket}
              className="w-full sm:w-auto px-4 py-2 text-xs font-bold uppercase tracking-wider bg-indigo-600 hover:bg-indigo-500 text-white rounded transition-all shadow-[0_4px_12px_rgba(79,70,229,0.2)] hover:shadow-[0_4px_16px_rgba(79,70,229,0.4)] cursor-pointer"
            >
              Initialize Network Pipe Handshake
            </button>
          </div>

          {/* Terminal Output Logs */}
          <div className="flex-1 min-h-[260px] bg-[#050810] border border-slate-850 rounded p-4 font-mono text-xs text-emerald-500 overflow-y-auto space-y-1.5 shadow-inner">
            {wsMessages.length === 0 ? (
              <div className="text-slate-600 italic">Console stream idle. Awaiting operational handshake directive...</div>
            ) : (
              wsMessages.map((msg, idx) => {
                let colorClass = 'text-emerald-400';
                if (msg.startsWith('[OUTBOUND]')) colorClass = 'text-indigo-400';
                if (msg.includes('SYSTEM')) colorClass = 'text-amber-400';
                return (
                  <div key={idx} className={`${colorClass} whitespace-pre-wrap selection:bg-slate-800`}>
                    {msg}
                  </div>
                );
              })
            )}
          </div>

          {/* Text Frame Echo Input */}
          {wsStatus === 'Connected' && (
            <form onSubmit={sendEchoFrame} className="mt-4 flex gap-2">
              <input
                type="text"
                value={inputFrame}
                onChange={(e) => setInputFrame(e.target.value)}
                placeholder="Queue diagnostic frame text payload..."
                className="flex-1 bg-[#050810] border border-slate-800 rounded px-4 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-hidden focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-mono"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold uppercase tracking-wider rounded transition-colors cursor-pointer border border-slate-700"
              >
                Transmit
              </button>
            </form>
          )}
        </section>

      </main>
    </div>
  );
};
