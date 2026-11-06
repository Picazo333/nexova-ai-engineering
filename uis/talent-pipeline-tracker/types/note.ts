export interface Note {
  id: string;
  record_id: string;
  content: string;
  created_at: string;
}

export interface NoteList {
  data: Note[];
  meta: {
    total: number;
  };
}

export interface NoteWrite {
  content: string;
}
