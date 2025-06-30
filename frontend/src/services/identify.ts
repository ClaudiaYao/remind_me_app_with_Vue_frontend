import { API_BASE_URL } from "@/config/config";
import axios from "axios";

export interface IdentifyResponse {
  success: boolean;
  message: string;
  data: RemindeeInfo;
}

export interface RemindeeInfo {
  person: string;
  summary: string;
  image: string;
}

export const identify = async (token: string, file: File): Promise<IdentifyResponse> => {
  if (!file) {
    throw new Error("No image provided");
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_BASE_URL}/operation/identify`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || "Image identification failed";
      throw new Error(message);
    } else if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("An unknown error occurred");
    }
  }
};
