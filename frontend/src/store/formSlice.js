import { createSlice } from "@reduxjs/toolkit";

const emptyForm = {
  hcp_name: null,
  interaction_type: null,
  date: null,
  time: null,
  attendees: null,
  topics_discussed: null,
  materials_shared: null,
  samples_distributed: null,
  sentiment: null,
  outcomes: null,
  follow_up_actions: null,
  notes: null,
};

const initialState = {
  data: { ...emptyForm },
  lastChangedFields: [],
  validation: null,
  suggestedFollowups: [],
  submitStatus: null, // 'success' | 'error' | null
  submitMessage: "",
};

const formSlice = createSlice({
  name: "form",
  initialState,
  reducers: {
    // The ONLY way the form is ever mutated in the UI - always driven by the
    // AI agent's response, never by a user typing into a field directly.
    applyAgentUpdate(state, action) {
      const nextForm = action.payload;
      const changed = Object.keys(nextForm).filter(
        (key) => JSON.stringify(nextForm[key]) !== JSON.stringify(state.data[key])
      );
      state.data = nextForm;
      state.lastChangedFields = changed;
    },
    setValidation(state, action) {
      state.validation = action.payload;
    },
    setSuggestedFollowups(state, action) {
      state.suggestedFollowups = action.payload || [];
    },
    clearFlash(state) {
      state.lastChangedFields = [];
    },
    setSubmitStatus(state, action) {
      state.submitStatus = action.payload.status;
      state.submitMessage = action.payload.message;
    },
    resetSubmitStatus(state) {
      state.submitStatus = null;
      state.submitMessage = "";
    },
  },
});

export const {
  applyAgentUpdate,
  setValidation,
  setSuggestedFollowups,
  clearFlash,
  setSubmitStatus,
  resetSubmitStatus,
} = formSlice.actions;
export default formSlice.reducer;
