// User types
export interface User {
  id: number;
  name?: string;
  bio?: string;
  avatar_path?: string;
  created_at: string;
}

export interface UserUpdate {
  name?: string;
  bio?: string;
  avatar_path?: string;
}

export interface LoginRequest {
  password: string;
}

// Hobby types
export interface Hobby {
  id: number;
  name: string;
  color?: string;
  icon?: string;
  parent_id?: number;
  children: Hobby[];
}

export interface HobbyCreate {
  name: string;
  color?: string;
  icon?: string;
  parent_id?: number;
}

export interface HobbyUpdate {
  name?: string;
  color?: string;
  icon?: string;
  parent_id?: number;
}

// Hobby Type types
export interface HobbyType {
  id: number;
  key: string;
  title: string;
  schema_json: string;
}

export interface HobbyTypeCreate {
  key: string;
  title: string;
  schema_json: string;
}

export interface HobbyTypeUpdate {
  title?: string;
  schema_json?: string;
}

// Entry types
export interface EntryProp {
  id: number;
  entry_id: number;
  key: string;
  value_text?: string;
}

export interface EntryPropBase {
  key: string;
  value_text?: string;
}

export interface EntryMedia {
  id: number;
  entry_id: number;
  kind?: "image" | "video" | "audio" | "doc";
  file_path: string;
  width?: number;
  height?: number;
  duration?: number;
  meta_json?: string;
}

export interface Entry {
  id: number;
  hobby_id: number;
  type_key: string;
  title?: string;
  description?: string;
  tags?: string;
  created_at: string;
  updated_at?: string;
  media: EntryMedia[];
  props: EntryProp[];
}

export interface EntryListItem {
  id: number;
  hobby_id: number;
  type_key: string;
  title?: string;
  description?: string;
  tags?: string;
  created_at: string;
  updated_at?: string;
  media_count: number;
  thumbnail_url?: string;
  props: Record<string, any>;
}

export interface EntryCreate {
  hobby_id: number;
  type_key: string;
  title?: string;
  description?: string;
  tags?: string;
}

export interface EntryUpdate {
  title?: string;
  description?: string;
  tags?: string;
}

// Common types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface ErrorResponse {
  status: number;
  code: string;
  message: string;
  details?: string;
}

// Search types
export interface SearchRequest {
  q: string;
  hobby_id?: number;
  type_key?: string;
  tag?: string;
}

export interface SearchResult {
  entry: EntryListItem;
  rank: number;
}