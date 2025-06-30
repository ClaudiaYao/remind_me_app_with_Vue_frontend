export interface UserSummary {
  nick_name: string;
  description: string;
  age: number;
  phone_number: string;
}

export interface UserProfile {
  user_summary: UserSummary;
  email: string;
  avatar_url: string;
}

export type LoginType = {
  email: string;
  password: string;
};
