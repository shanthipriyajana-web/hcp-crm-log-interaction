import InteractionForm from "./InteractionForm";
import ChatPanel from "./ChatPanel";

export default function Layout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <p className="eyebrow">AI-First CRM · HCP Module</p>
        <h1 className="app-title">Log Interaction</h1>
      </header>
      <div className="split-layout">
        <InteractionForm />
        <ChatPanel />
      </div>
    </div>
  );
}
