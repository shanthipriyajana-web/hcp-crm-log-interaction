import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  messages: [
    {
      role: "assistant",
      content:
        "Hi, I'm your interaction assistant. Tell me about a visit and I'll fill in the form for you - for example: \"I met Dr. Smith today, discussed Product X, sentiment was positive, and I shared brochures.\"",
      toolTag: null,
    },
  ],
  loading: false,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage(state, action) {
      state.messages.push(action.payload);
    },
    setLoading(state, action) {
      state.loading = action.payload;
    },
  },
});

export const { addMessage, setLoading } = chatSlice.actions;
export default chatSlice.reducer;
