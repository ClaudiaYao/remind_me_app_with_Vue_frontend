export interface RemindeeProfile {
  image_object_key: string;
  person_name: string;
  summary: string | null;
  relationship: string;
  ai_summary: string | null;
}

export interface RemindeeSingleRecord {
  image_object_key: string;
  person_name: string;
  summary: string | "";
  relationship: string;
}
