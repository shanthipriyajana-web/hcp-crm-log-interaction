import { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { addMessage, setLoading } from "../store/chatSlice";
import { applyAgentUpdate, setValidation, setSuggestedFollowups } from "../store/formSlice";
import { sendChatMessage } from "../api/client";

export default function ChatPanel() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.chat);
  const formData = useSelector((state) => state.form.data);
  const [input, setInput] = useState("");
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages]);

  const send = async (text) => {
    const message = text ?? input;
    if (!message.trim() || loading) return;

    dispatch(addMessage({ role: "user", content: message, toolTag: null }));
    setInput("");
    dispatch(setLoading(true));

    try {
      const result = await sendChatMessage(message, formData, messages);
      dispatch(applyAgentUpdate(result.form_state));
      if (result.validation) dispatch(setValidation(result.validation));
      if (result.suggested_followups) dispatch(setSuggestedFollowups(result.suggested_followups));
      dispatch(
        addMessage({
          role: "assistant",
          content: result.reply,
          toolTag: result.tool_called,
        })
      );
    } catch (e) {
      dispatch(
        addMessage({
          role: "assistant",
          content: `Something went wrong talking to the agent: ${e.message}`,
          toolTag: null,
        })
      );
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="panel chat-panel">
      <p className="panel-title">
        <span className="assistant-icon">◐</span> AI Assistant
      </p>
      <p className="panel-subtitle">Log interaction via chat</p>

      <div className="chat-log" ref={logRef}>
        {messages.map((m, i) => (
          <div key={i}>
            {m.toolTag && <div className="bubble tool-tag">🔧 {m.toolTag}</div>}
            <div className={`bubble ${m.role}`}>{m.content}</div>
          </div>
        ))}
        {loading && <div className="bubble assistant">Thinking…</div>}
      </div>

      <div className="chat-input-row">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Describe interaction…"
          disabled={loading}
        />
        <button onClick={() => send()} disabled={loading}>
          ⤴ Log
        </button>
      </div>
    </div>
  );
}