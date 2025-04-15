/**
 * Models Slice
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { ModelApiClient } from '@dmac/api';

// Define the state type
interface ModelsState {
  items: any[];
  selectedModel: string | null;
  loading: boolean;
  error: string | null;
}

// Define the initial state
const initialState: ModelsState = {
  items: [],
  selectedModel: null,
  loading: false,
  error: null,
};

// Create async thunks
export const fetchModels = createAsyncThunk(
  'models/fetchModels',
  async (_, { rejectWithValue }) => {
    try {
      const apiClient = new ModelApiClient('http://localhost:3000');
      const models = await apiClient.getModels();
      return models;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

// Create the slice
const modelsSlice = createSlice({
  name: 'models',
  initialState,
  reducers: {
    setSelectedModel: (state, action: PayloadAction<string>) => {
      state.selectedModel = action.payload;
    },
    clearSelectedModel: (state) => {
      state.selectedModel = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchModels.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchModels.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

// Export actions
export const { setSelectedModel, clearSelectedModel } = modelsSlice.actions;

// Export reducer
export default modelsSlice.reducer;
