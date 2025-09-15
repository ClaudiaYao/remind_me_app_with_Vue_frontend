import heic2any from "heic2any";

// export async function captureImage() {
//   const photo = await Camera.getPhoto({
//     quality: 90,
//     allowEditing: false,
//     resultType: CameraResultType.Uri,
//     source: CameraSource.Camera, // could also be CameraSource.Photos
//   });

//   // Convert into File (so backend upload works the same way)
//   const response = await fetch(photo.webPath!);
//   const blob = await response.blob();
//   return new File([blob], `photo.${blob.type.split("/")[1]}`, { type: blob.type });
// }

export async function convertIfHeic(file: File): Promise<File> {
  const isHeicOrHeif =
    file.type === "image/heic" ||
    file.type === "image/heif" ||
    file.name.toLowerCase().endsWith(".heic") ||
    file.name.toLowerCase().endsWith(".heif");

  if (isHeicOrHeif) {
    const convertedBlob = await heic2any({
      blob: file,
      toType: "image/jpeg",
      quality: 0.9,
    });

    return new File([convertedBlob as Blob], file.name.replace(/\.(heic|heif)$/i, ".jpg"), { type: "image/jpeg" });
  }

  return file;
}
