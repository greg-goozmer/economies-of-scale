import { configureStore, createAsyncThunk, createSlice, isAnyOf } from '@reduxjs/toolkit';
import { useDispatch, useSelector } from 'react-redux';
import axios from 'axios';
import { costsApi, costError } from '../api/costsClient';
import type { BodyCreateCost, CostPublish, CostRead, UserRead } from '../api/generated/CostsApi';
import { COSTS_MOCK, filterCosts } from '../modules/costsMock';

export interface CostsState {
  user: UserRead | null;
  minimum: string;
  maximum: string;
  appliedMinimum: string;
  appliedMaximum: string;
  items: CostRead[];
  feed: CostRead | null;
  draft: CostRead | null;
  pending: number;
  authBusy: boolean;
  error: string;
  mock: boolean;
  listRequest: string;
  feedRequest: string;
}

const initialState: CostsState = {
  user: null, minimum: '', maximum: '', appliedMinimum: '', appliedMaximum: '',
  items: [], feed: null, draft: null, pending: 0, authBusy: false,
  error: '', mock: false, listRequest: '', feedRequest: '',
};
type CostsThunk = { state: { costs: CostsState }; rejectValue: string };

export const mockCost = (cost: (typeof COSTS_MOCK)[number]): CostRead => ({
  ...cost, cost_status: 'published', cost_creator_id: 0, cost_created_at: '',
  cost_formed_at: null, is_owner: 0, is_liked: 0,
});

function offlineForGuest(error: unknown, user: UserRead | null) {
  return !user && axios.isAxiosError(error) && !axios.isCancel(error) &&
    (!error.response || [502, 503, 504].includes(error.response.status));
}

export const loadCosts = createAsyncThunk<
  { items: CostRead[]; mock: boolean; minimum: string; maximum: string },
  { minimum: string; maximum: string }, CostsThunk
>('costs/loadCosts', async (filter, { getState, rejectWithValue, signal }) => {
  try {
    const result = await costsApi.api.listCosts({
      min_cost_code: filter.minimum === '' ? undefined : Number(filter.minimum),
      max_cost_code: filter.maximum === '' ? undefined : Number(filter.maximum),
    }, { signal });
    return { items: result.data, mock: false, ...filter };
  } catch (error) {
    if (offlineForGuest(error, getState().costs.user)) {
      return { items: filterCosts(COSTS_MOCK, filter.minimum, filter.maximum).map(mockCost), mock: true, ...filter };
    }
    return rejectWithValue(costError(error));
  }
});

export const loadCostFeed = createAsyncThunk<
  { cost: CostRead | null; mock: boolean }, { cost_id?: number; next?: boolean }, CostsThunk
>('costs/loadCostFeed', async (query, { getState, rejectWithValue, signal }) => {
  try {
    return { cost: (await costsApi.api.getCostFeed(query, { signal })).data, mock: false };
  } catch (error) {
    if (offlineForGuest(error, getState().costs.user)) {
      const costs = filterCosts(COSTS_MOCK, getState().costs.appliedMinimum, getState().costs.appliedMaximum);
      let cost = costs.find(item => item.cost_id === query.cost_id);
      if (query.cost_id === undefined) cost = costs[0];
      else if (query.next && cost) cost = costs[(costs.indexOf(cost) + 1) % costs.length];
      return { cost: cost ? mockCost(cost) : null, mock: true };
    }
    return rejectWithValue(costError(error));
  }
});

export const loadCostDraft = createAsyncThunk<CostRead | null, void, CostsThunk>(
  'costs/loadCostDraft', async (_, { rejectWithValue }) => {
    try { return (await costsApi.api.getCostDraft()).data; }
    catch (error) { return rejectWithValue(costError(error)); }
  },
);
export const createCostDraft = createAsyncThunk<CostRead, BodyCreateCost, CostsThunk>(
  'costs/createCostDraft', async (data, { rejectWithValue }) => {
    try { return (await costsApi.api.createCost(data)).data; }
    catch (error) { return rejectWithValue(costError(error)); }
  },
);
export const publishCostDraft = createAsyncThunk<CostRead, { id: number; data: CostPublish }, CostsThunk>(
  'costs/publishCostDraft', async ({ id, data }, { rejectWithValue }) => {
    try { return (await costsApi.api.publishCost({ costId: id }, data)).data; }
    catch (error) { return rejectWithValue(costError(error)); }
  },
);
export const deleteOwnCost = createAsyncThunk<number, number, CostsThunk>(
  'costs/deleteOwnCost', async (id, { rejectWithValue }) => {
    try { await costsApi.api.deleteCost({ costId: id }); return id; }
    catch (error) { return rejectWithValue(costError(error)); }
  },
);
export const changeCostLike = createAsyncThunk<
  { cost_id: number; is_liked: 0 | 1; like_count: number }, { id: number; liked: 0 | 1 }, CostsThunk
>('costs/changeCostLike', async ({ id, liked }, { rejectWithValue }) => {
  try { return (await costsApi.api.changeCostLike({ costId: id }, { is_liked: liked })).data; }
  catch (error) { return rejectWithValue(costError(error)); }
});

const requests = [loadCosts, loadCostFeed, loadCostDraft, createCostDraft, publishCostDraft, deleteOwnCost, changeCostLike];
const costsSlice = createSlice({
  name: 'costs', initialState,
  reducers: {
    setCostMinimum(state, action: { payload: string }) { state.minimum = action.payload; },
    setCostMaximum(state, action: { payload: string }) { state.maximum = action.payload; },
    setCostUser(state, action: { payload: UserRead }) {
      state.user = action.payload;
      state.error = '';
      state.draft = null;
      state.feed = null;
      state.items = [];
    },
    resetCostUser: () => ({ ...initialState }),
    setCostAuthBusy(state, action: { payload: boolean }) { state.authBusy = action.payload; },
    clearCostError(state) { state.error = ''; },
  },
  extraReducers(builder) {
    builder
      .addCase(loadCosts.pending, (state, action) => { state.listRequest = action.meta.requestId; })
      .addCase(loadCosts.fulfilled, (state, action) => {
        if (action.meta.requestId !== state.listRequest) return;
        state.items = action.payload.items;
        state.mock = action.payload.mock;
        state.appliedMinimum = action.payload.minimum;
        state.appliedMaximum = action.payload.maximum;
      })
      .addCase(loadCostFeed.pending, (state, action) => {
        state.feedRequest = action.meta.requestId;
        state.feed = null;
      })
      .addCase(loadCostFeed.fulfilled, (state, action) => {
        if (action.meta.requestId !== state.feedRequest) return;
        state.feed = action.payload.cost;
        state.mock = action.payload.mock;
      })
      .addCase(loadCostDraft.fulfilled, (state, action) => { state.draft = action.payload; })
      .addCase(createCostDraft.fulfilled, (state, action) => { state.draft = action.payload; })
      .addCase(publishCostDraft.fulfilled, state => { state.draft = null; })
      .addCase(deleteOwnCost.fulfilled, (state, action) => {
        state.items = state.items.filter(item => item.cost_id !== action.payload);
        if (state.draft?.cost_id === action.payload) state.draft = null;
      })
      .addCase(changeCostLike.fulfilled, (state, action) => {
        const cost = state.items.find(item => item.cost_id === action.payload.cost_id);
        if (cost) Object.assign(cost, action.payload);
        if (state.feed?.cost_id === action.payload.cost_id) Object.assign(state.feed, action.payload);
      })
      .addMatcher(isAnyOf(...requests.map(request => request.pending)), state => {
        state.pending += 1;
        state.error = '';
      })
      .addMatcher(isAnyOf(...requests.map(request => request.fulfilled), ...requests.map(request => request.rejected)), (state, action) => {
        state.pending = Math.max(0, state.pending - 1);
        if (action.meta.requestStatus === 'rejected' && !action.meta.aborted) {
          state.error = (action as { payload?: string }).payload || 'Ошибка запроса';
          if (state.error === 'Сессия истекла. Войдите снова.') {
            state.user = null;
            state.draft = null;
          }
        }
      });
  },
});

export const { setCostMinimum, setCostMaximum, setCostUser, resetCostUser, setCostAuthBusy, clearCostError } = costsSlice.actions;
export const createCostsStore = () => configureStore({ reducer: { costs: costsSlice.reducer } });
export const costsStore = createCostsStore();
export type CostsRootState = ReturnType<typeof costsStore.getState>;
export const useCostsDispatch = useDispatch.withTypes<typeof costsStore.dispatch>();
export const useCostsSelector = useSelector.withTypes<CostsRootState>();
