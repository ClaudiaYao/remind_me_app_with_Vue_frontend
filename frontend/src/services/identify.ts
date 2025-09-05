import { API_BASE_URL } from "@/config/config";
import axios from "axios";

export interface IdentifyResponse {
  status: string;
  job_id: string;
}

export interface RemindeeInfo {
  person: string;
  summary: string;
  image: string;
}

export interface InferenceResult {
  status: string;
  person: string | null;
  data?: RemindeeInfo | undefined;
}

export async function isInferenceComplete(token: string, jobId: string): Promise<InferenceResult> {
  try {
    const response = await axios.get(`${API_BASE_URL}/operation/check-inference-status?job_id=${jobId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200 && response.data) {
      return response.data;
    } else {
      throw new Error("Unexpected response format");
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || "Failed to check inference status";
      throw new Error(message);
    } else if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("An unknown error occurred while checking inference status");
    }
  }
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
