import { API_BASE_URL } from "@/config/config";
import type { RemindeeProfile } from "@/types/remindee";
import axios from "axios";

// interface imageItemForUpload {
//     file: File;
//     summary: string;
// }
export interface UploadPayload {
  person_name: string;
  relationship: string;
  summary: string[];
  files: File[];
}

export async function check_model_exist(token: string): Promise<boolean> {
  try {
    const response = await axios.get<{ status: boolean }>(`${API_BASE_URL}/operation/is-model-exist`, {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data.status;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.error("Model check failed:", error.response?.data || error.message);
      throw new Error(error.response?.data?.message || "Error checking model existence");
    }
    throw new Error("Unexpected error occurred");
  }
}

export async function trigger_train(token: string): Promise<string> {
  try {
    const response = await axios.get(`${API_BASE_URL}/operation/train`, {
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    });

    console.log(response.data);
    if (response.status === 200) {
      const job_id = response.data?.job_id;
      if (job_id) {
        return job_id;
      }
      throw new Error("Training job name not found in response");
    }

    throw new Error("Unexpected response status: " + response.status);
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || "Training request failed";
      throw new Error(message);
    } else if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("An unknown error occurred");
    }
  }
}

export async function isTrainingComplete(token: string, jobId: string): Promise<string> {
  try {
    const response = await axios.get(`${API_BASE_URL}/operation/check-training-status?job_id=${jobId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200 && response.data) {
      return response.data.status;
    } else {
      throw new Error("Unexpected response format");
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || "Failed to check training status";
      throw new Error(message);
    } else if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("An unknown error occurred while checking training status");
    }
  }
}

// export async function upload(
//   payload: UploadPayload,
//   token: string,
//   onProgress: (progress: number) => void
// ): Promise<void> {
//   const formData = new FormData();
//   formData.append("person_name", payload.person_name);
//   formData.append("relationship", payload.relationship);
//   payload.files.forEach((item) => {
//     formData.append(`files`, item);
//   });
//   payload.summary.forEach((item) => {
//     formData.append(`summary`, item);
//   });
//   console.log("execute");
//   // const simulateUpload = () => {
//   //     return new Promise<void>((resolve) => {
//   //         let progress = 0;
//   //         const interval = setInterval(() => {
//   //             progress += 10;
//   //             onProgress(progress);
//   //             if (progress >= 100) {
//   //                 clearInterval(interval);
//   //                 resolve();
//   //             }
//   //         }, 500);
//   //     });
//   // };
//   await axios.post(`${API_BASE_URL}/operation/upload`, formData, {
//     headers: {
//       Authorization: `Bearer ${token}`,
//       "Content-Type": "multipart/form-data",
//     },
//     onUploadProgress: (progressEvent) => {
//       const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
//       onProgress(percentCompleted);
//     },
//   });
//   // await simulateUpload();
// }

export async function upload(
  payload: UploadPayload,
  token: string,
  onProgress: (progress: number) => void
): Promise<RemindeeProfile> {
  const formData = new FormData();
  formData.append("person_name", payload.person_name);
  formData.append("relationship", payload.relationship);

  payload.files.forEach((file) => {
    formData.append("files", file); // check backend expects multiple "files" keys
  });

  payload.summary.forEach((item) => {
    formData.append("summary", item); // check backend expects multiple "summary" keys
  });

  try {
    const response = await axios.post(`${API_BASE_URL}/operation/upload`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        // Do not manually set Content-Type
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
        onProgress(percentCompleted);
      },
    });

    // after uploading a batch of images,
    const response_data = response.data.data;
    const remindee_profile: RemindeeProfile = {
      image_object_key: response_data.image,
      person_name: response_data.person,
      ai_summary: response_data.summary,
      summary: null,
      relationship: payload.relationship,
    };

    return remindee_profile;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || "Upload failed";
      throw new Error(message);
    } else if (error instanceof Error) {
      throw new Error(error.message);
    } else {
      throw new Error("Unknown error during upload");
    }
  }
}
