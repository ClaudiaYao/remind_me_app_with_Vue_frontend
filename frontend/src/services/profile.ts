import axios from "axios";
import { API_BASE_URL } from "@/config/config";
import type { RemindeeProfile } from "@/types/remindee";
import type { UserSummary, UserProfile } from "@/types/user";
import type { RemindeeSingleRecord } from "@/types/remindee";

interface RemindeeInfo {
  RemindeeList: RemindeeProfile[];
  has_more: boolean;
}

export interface RemindeeInfoAll {
  // isEditing?: boolean;
  records: RemindeeSingleRecord[];
  ai_summary: string | null;
  image_presigned_url: { [key: string]: string };
}

export interface RemindeeUpdate {
  image_object_url: string;
  image_summary: string | "";
  action: string; // "delete" or "update"
}

export interface RemindeeUpdatePayload {
  person_name: string;
  items: RemindeeUpdate[];
}

export const updateRemindeeDetails = async (
  remindeeUpdate: RemindeeUpdatePayload,
  token: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/user/change_remindee_info`,
      remindeeUpdate, // Send object in request body
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (response.data.success === true) {
      return { success: true, message: "Remindee info is updated correctly." };
    } else {
      return { success: false, message: "Update failed on backend." };
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        message: error.response?.data?.message || "Failed to update remindee info.",
      };
    }
    return {
      success: false,
      message: "An unexpected error occurred.",
    };
  }
};

export const fetchRemindeeDetails = async (token: string, person_name: string): Promise<RemindeeInfoAll> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/remindee_info?person_name=${person_name}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.data.success === true) {
      return {
        records: response.data.data.records,
        ai_summary: response.data.data.ai_summary,
        image_presigned_url: response.data.data.image_presigned_url,
      };
    } else {
      return {
        records: [],
        ai_summary: "",
        image_presigned_url: {},
      };
    }
  } catch (error: unknown) {
    console.error("Error fetching remindee detail information", error);
    throw error;
  }
};

export const fetchRemindeeProfile = async (token: string, skip: number, limit: number): Promise<RemindeeInfo> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/user/profile?retrieve_new_profile=true&skip=${skip}&limit=${limit}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    console.log(response.data.data.remindee);
    const data = response.data.data; // extract the inner `data`

    if (data.length == 0) {
      return {
        RemindeeList: [],
        has_more: false,
      };
    }

    const remindees = data.remindee;
    const hasMore = data.has_more;

    return {
      RemindeeList: remindees,
      has_more: hasMore,
    };
  } catch (error: unknown) {
    console.error("Error fetching remindee profile:", error);
    throw error;
  }
};

export const fetchUserProfile = async (token: string): Promise<UserProfile> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/user-profile`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data.data;
  } catch (error: unknown) {
    console.error("Error fetching user profile:", error);
    throw error;
  }
};

export const updateProfile = async (
  token: string,
  userSummary: UserSummary,
  avatar: File | null
): Promise<{ success: boolean; message: string }> => {
  const formData = new FormData();
  formData.append("nick_name", userSummary.nick_name);
  formData.append("description", userSummary.description);
  formData.append("age", userSummary.age.toString());
  formData.append("phone_number", userSummary.phone_number);
  if (avatar) {
    formData.append("avatar", avatar);
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/user/update-profile`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    });

    // Optionally log or inspect response
    console.log("Profile updated:", response.status, response.data);

    return {
      success: response.status === 200,
      message: response.data?.message ?? "Profile updated successfully.",
    };
  } catch (error: unknown) {
    // More detailed error message
    if (axios.isAxiosError(error)) {
      return {
        success: false,
        message: error.response?.data?.message || "Failed to update profile.",
      };
    }
    return {
      success: false,
      message: "An unexpected error occurred.",
    };
  }
};

// export const fetchUserProfile = async (token: string): Promise<UserProfile> => {
//   const response = await axios.get(`${API_BASE_URL}/user/user-profile`, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//   });
//   console.log(response.data.data);
//   return response.data.data;
//   // const mockUserProfile: UserProfile = {
//   //     user_summary: {
//   //         nick_name: "JohnDoe",
//   //         description: "A passionate software developer",
//   //         age: 30,
//   //         phone_number: "123-456-7890"
//   //     },
//   //     email: "johndoe@example.com",
//   //     avatar_url: "https://example.com/avatar.jpg"
//   // };

//   // return mockUserProfile;
// };

// export const updateProfile = async (token: string, userSummary: UserSummary, avatar: File | null): Promise<void> => {
//   try {
//     const formData = new FormData();
//     formData.append("nick_name", userSummary.nick_name);
//     formData.append("description", userSummary.description);
//     formData.append("age", userSummary.age.toString());
//     formData.append("phone_number", userSummary.phone_number);
//     if (avatar) {
//       formData.append("avatar", avatar);
//     }
//     // formData.append("avatar", avatar);
//     await axios.post(`${API_BASE_URL}/user/update-profile`, formData, {
//       headers: {
//         Authorization: `Bearer ${token}`,
//         "Content-Type": "multipart/form-data",
//       },
//     });
//   } catch (error: unknown) {
//     console.error("Error updating user profile:", error);
//     throw error;
//   }
// };
