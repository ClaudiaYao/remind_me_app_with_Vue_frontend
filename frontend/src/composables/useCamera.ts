import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";

export async function captureImage() {
  const photo = await Camera.getPhoto({
    quality: 90,
    allowEditing: false,
    resultType: CameraResultType.Uri,
    source: CameraSource.Camera, // could also be CameraSource.Photos
  });

  // Convert into File (so backend upload works the same way)
  const response = await fetch(photo.webPath!);
  const blob = await response.blob();
  return new File([blob], `photo.${blob.type.split("/")[1]}`, { type: blob.type });
}
