import {
  User, UserUpdate, LoginRequest,
  Hobby, HobbyCreate, HobbyUpdate,
  HobbyType, HobbyTypeCreate, HobbyTypeUpdate,
  Entry, EntryCreate, EntryUpdate, EntryListItem,
  EntryProp, EntryPropBase, EntryMedia,
  PaginatedResponse, SearchRequest
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

class APIError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const config: RequestInit = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);
  
  if (!response.ok) {
    let errorData: any = {};
    try {
      errorData = await response.json();
    } catch {
      // If JSON parsing fails, use default error
    }
    
    throw new APIError(
      response.status,
      errorData.code || 'UNKNOWN_ERROR',
      errorData.message || `HTTP ${response.status}`
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// Auth API
export const authAPI = {
  async login(credentials: LoginRequest): Promise<{ message: string }> {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  async logout(): Promise<{ message: string }> {
    return request('/auth/logout', {
      method: 'POST',
    });
  },
};

// Users API
export const usersAPI = {
  async getCurrentUser(): Promise<User> {
    return request('/users/me');
  },

  async updateCurrentUser(data: UserUpdate): Promise<User> {
    return request('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async uploadAvatar(file: File): Promise<User> {
    const formData = new FormData();
    formData.append('file', file);

    return request('/users/me/avatar', {
      method: 'POST',
      headers: {}, // Let fetch set Content-Type for FormData
      body: formData,
    });
  },
};

// Hobbies API
export const hobbiesAPI = {
  async getHobbies(parentId?: number): Promise<Hobby[]> {
    const params = parentId !== undefined ? `?parent_id=${parentId}` : '';
    return request(`/hobbies${params}`);
  },

  async getHobbiesTree(): Promise<Hobby[]> {
    return request('/hobbies/tree');
  },

  async getHobby(id: number): Promise<Hobby> {
    return request(`/hobbies/${id}`);
  },

  async createHobby(data: HobbyCreate): Promise<Hobby> {
    return request('/hobbies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateHobby(id: number, data: HobbyUpdate): Promise<Hobby> {
    return request(`/hobbies/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async deleteHobby(id: number): Promise<{ message: string }> {
    return request(`/hobbies/${id}`, {
      method: 'DELETE',
    });
  },
};

// Hobby Types API
export const hobbyTypesAPI = {
  async getHobbyTypes(): Promise<HobbyType[]> {
    return request('/hobby-types');
  },

  async createHobbyType(data: HobbyTypeCreate): Promise<HobbyType> {
    return request('/hobby-types', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateHobbyType(key: string, data: HobbyTypeUpdate): Promise<HobbyType> {
    return request(`/hobby-types/${key}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async deleteHobbyType(key: string): Promise<{ message: string }> {
    return request(`/hobby-types/${key}`, {
      method: 'DELETE',
    });
  },
};

// Entries API
export const entriesAPI = {
  async getEntries(params?: {
    q?: string;
    hobby_id?: number;
    type_key?: string;
    tag?: string;
    limit?: number;
    offset?: number;
  }): Promise<PaginatedResponse<EntryListItem>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    const query = searchParams.toString();
    return request(`/entries${query ? `?${query}` : ''}`);
  },

  async getEntry(id: number): Promise<Entry> {
    return request(`/entries/${id}`);
  },

  async createEntry(data: EntryCreate): Promise<Entry> {
    return request('/entries', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateEntry(id: number, data: EntryUpdate): Promise<Entry> {
    return request(`/entries/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async deleteEntry(id: number): Promise<{ message: string }> {
    return request(`/entries/${id}`, {
      method: 'DELETE',
    });
  },

  // Entry Properties
  async getEntryProps(entryId: number): Promise<EntryProp[]> {
    return request(`/entries/${entryId}/props`);
  },

  async setEntryProps(entryId: number, props: EntryPropBase[]): Promise<EntryProp[]> {
    return request(`/entries/${entryId}/props`, {
      method: 'POST',
      body: JSON.stringify({ props }),
    });
  },

  async deleteEntryProp(entryId: number, key: string): Promise<{ message: string }> {
    return request(`/entries/${entryId}/props/${key}`, {
      method: 'DELETE',
    });
  },

  // Entry Media
  async getEntryMedia(entryId: number): Promise<EntryMedia[]> {
    return request(`/entries/${entryId}/media`);
  },

  async uploadMedia(entryId: number, file: File, kind?: string): Promise<EntryMedia> {
    const formData = new FormData();
    formData.append('file', file);
    if (kind) {
      formData.append('kind', kind);
    }

    return request(`/entries/${entryId}/media`, {
      method: 'POST',
      headers: {}, // Let fetch set Content-Type for FormData
      body: formData,
    });
  },

  async deleteMedia(entryId: number, mediaId: number): Promise<{ message: string }> {
    return request(`/entries/${entryId}/media/${mediaId}`, {
      method: 'DELETE',
    });
  },
};

// Search API
export const searchAPI = {
  async search(params: SearchRequest & {
    limit?: number;
    offset?: number;
  }): Promise<PaginatedResponse<EntryListItem>> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    return request(`/search?${searchParams.toString()}`);
  },
};