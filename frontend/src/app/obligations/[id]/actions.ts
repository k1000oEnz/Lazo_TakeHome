"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { ApiError, serverApi } from "@/lib/api-server";

export async function transitionAction(formData: FormData) {
  const obligationId = formData.get("obligation_id") as string;
  const toStatus = formData.get("to_status") as string;
  const version = Number(formData.get("version"));
  const documentId = formData.get("document_id") as string | null;

  try {
    await serverApi.transition(obligationId, {
      to_status: toStatus,
      version,
      ...(documentId ? { document_id: documentId } : {}),
    });
  } catch (error) {
    if (error instanceof ApiError) {
      const code = error.code.toLowerCase();
      if (error.status === 404) {
        redirect(`/obligations/${obligationId}?error=not_found`);
      }
      if (error.status === 409) {
        redirect(`/obligations/${obligationId}?error=version_conflict`);
      }
      if (error.status === 400) {
        redirect(`/obligations/${obligationId}?error=${code}`);
      }
    }
    throw error;
  }

  revalidatePath(`/obligations/${obligationId}`);
  revalidatePath("/");
  redirect(`/obligations/${obligationId}`);
}

export async function uploadDocumentAction(formData: FormData) {
  const obligationId = formData.get("obligation_id") as string;
  const file = formData.get("file") as File | null;

  if (!file || file.size === 0) {
    redirect(`/obligations/${obligationId}?error=generic`);
  }

  try {
    await serverApi.uploadDocument(obligationId, file);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      redirect(`/obligations/${obligationId}?error=not_found`);
    }
    redirect(`/obligations/${obligationId}?error=generic`);
  }

  revalidatePath(`/obligations/${obligationId}`);
  redirect(`/obligations/${obligationId}`);
}
