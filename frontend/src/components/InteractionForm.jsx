import { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { clearFlash, setSubmitStatus } from "../store/formSlice";
import { submitInteraction } from "../api/client";

function sentimentClass(sentiment) {
  if (!sentiment) return "";
  const s = sentiment.toLowerCase();
  if (s === "positive") return "positive";
  if (s === "negative") return "negative";
  return "neutral";
}

function DisplayInput({ value, placeholder }) {
  const empty = value === null || value === undefined || value === "";
  return (
    <div className={`display-input ${empty ? "empty" : ""}`}>
      {empty ? placeholder : value}
    </div>
  );
}

function TagList({ items, emptyLabel }) {
  if (!items || items.length === 0) {
    return <div className="display-input empty">{emptyLabel}</div>;
  }
  return (
    <div className="tag-list">
      {items.map((item, i) => (
        <span className="tag-chip" key={i}>
          {item}
        </span>
      ))}
    </div>
  );
}

export default function InteractionForm() {
  const dispatch = useDispatch();
  const {
    data,
    lastChangedFields,
    validation,
    suggestedFollowups,
    submitStatus,
    submitMessage,
  } = useSelector((state) => state.form);

  useEffect(() => {
    if (lastChangedFields.length === 0) return;
    const timer = setTimeout(() => dispatch(clearFlash()), 1400);
    return () => clearTimeout(timer);
  }, [lastChangedFields, dispatch]);

  const isChanged = (key) => lastChangedFields.includes(key);
  const canSubmit = data.hcp_name && data.date && data.interaction_type && data.sentiment;

  const handleSubmit = async () => {
    try {
      await submitInteraction(data);
      dispatch(setSubmitStatus({ status: "success", message: "Interaction saved to CRM." }));
    } catch (e) {
      dispatch(setSubmitStatus({ status: "error", message: e.message }));
    }
  };

  return (
    <div className="panel">
      <p className="panel-title">Interaction Details</p>
      <div className="locked-note">
        This form is controlled by the AI Assistant. Describe the visit in chat and the fields
        below fill in automatically.
      </div>

      <div className="field-row">
        <div className={`field half ${isChanged("hcp_name") ? "flash" : ""}`}>
          <label>HCP Name</label>
          <DisplayInput value={data.hcp_name} placeholder="Search or select HCP…" />
        </div>
        <div className={`field half ${isChanged("interaction_type") ? "flash" : ""}`}>
          <label>Interaction Type</label>
          <DisplayInput value={data.interaction_type} placeholder="Meeting / Call / Email" />
        </div>
      </div>

      <div className="field-row">
        <div className={`field half ${isChanged("date") ? "flash" : ""}`}>
          <label>Date</label>
          <DisplayInput value={data.date} placeholder="DD-MM-YYYY" />
        </div>
        <div className={`field half ${isChanged("time") ? "flash" : ""}`}>
          <label>Time</label>
          <DisplayInput value={data.time} placeholder="--:--" />
        </div>
      </div>

      <div className={`field ${isChanged("attendees") ? "flash" : ""}`}>
        <label>Attendees</label>
        <DisplayInput value={data.attendees} placeholder="Enter names or search…" />
      </div>

      <div className={`field ${isChanged("topics_discussed") ? "flash" : ""}`}>
        <label>Topics Discussed</label>
        <DisplayInput value={data.topics_discussed} placeholder="Enter key discussion points…" />
      </div>

      <div className="field-group">
        <label className="group-label">Materials Shared / Samples Distributed</label>

        <div className={`field ${isChanged("materials_shared") ? "flash" : ""}`}>
          <div className="sub-row">
            <span className="sub-label">Materials Shared</span>
          </div>
          <TagList items={data.materials_shared} emptyLabel="No materials added" />
        </div>

        <div className={`field ${isChanged("samples_distributed") ? "flash" : ""}`}>
          <div className="sub-row">
            <span className="sub-label">Samples Distributed</span>
          </div>
          <TagList items={data.samples_distributed} emptyLabel="No samples added" />
        </div>
      </div>

      <div className={`field ${isChanged("sentiment") ? "flash" : ""}`}>
        <label>Observed / Inferred HCP Sentiment</label>
        <div className="radio-row">
          {["Positive", "Neutral", "Negative"].map((option) => (
            <label className="radio-option" key={option}>
              <input type="radio" checked={data.sentiment === option} disabled readOnly />
              <span className={data.sentiment === option ? `sentiment-tag ${sentimentClass(option)}` : ""}>
                {option}
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className={`field ${isChanged("outcomes") ? "flash" : ""}`}>
        <label>Outcomes</label>
        <DisplayInput value={data.outcomes} placeholder="Key outcomes or agreements…" />
      </div>

      <div className={`field ${isChanged("follow_up_actions") ? "flash" : ""}`}>
        <label>Follow-up Actions</label>
        <DisplayInput value={data.follow_up_actions} placeholder="Enter next steps or tasks…" />
      </div>

      {suggestedFollowups && suggestedFollowups.length > 0 && (
        <div className="field ai-followups">
          <label>AI Suggested Follow-ups</label>
          <ul>
            {suggestedFollowups.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {validation && !validation.ready && (
        <div
          className="locked-note"
          style={{ borderColor: "var(--negative)", background: "var(--negative-soft)" }}
        >
          Missing: {validation.missing.join(", ")}
        </div>
      )}

      <button className="submit-btn" disabled={!canSubmit} onClick={handleSubmit}>
        Submit Interaction
      </button>
      {submitStatus && (
        <div className={`submit-feedback ${submitStatus === "success" ? "ok" : "err"}`}>
          {submitMessage}
        </div>
      )}
    </div>
  );
}
