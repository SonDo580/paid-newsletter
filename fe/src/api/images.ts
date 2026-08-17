import type { UploadImageResBody } from "~/schemas/images";
import { apiClient } from "./apiClient";

export async function uploadImage(file: File): Promise<UploadImageResBody> {
  const formData = new FormData();
  formData.append("file", file); // 'file' parameter specified by BE

  return apiClient<UploadImageResBody>("/images", {
    method: "POST",
    body: formData,
  });
}
