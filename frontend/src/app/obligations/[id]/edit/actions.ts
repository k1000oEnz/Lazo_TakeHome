"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { ApiError, serverApi } from "@/lib/api-server";

export async function updateObligationAction(formData: FormData) {
  const id = formData.get("obligation_id") as string;

  const data: Record<string, unknown> = {};
  const title = formData.get("title") as string | null;
  if (title) data.title = title;
  const description = ((formData.get("description") as string | null) ?? "").trim();
  data.description = description === "" ? null : description;
  const due_date = formData.get("due_date") as string | null;
  if (due_date) data.due_date = due_date;
  const owner = formData.get("owner") as string | null;
  if (owner) data.owner = owner;
  data.requires_document = formData.get("requires_document") === "on";

  try {
    await serverApi.updateObligation(id, data);
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.status === 404) {
        redirect(`/obligations/${id}?error=not_found`);
      }
      if (error.status === 409) {
        redirect(`/obligations/${id}/edit?error=version_conflict`);
      }
    }
    throw error;
  }

  revalidatePath(`/obligations/${id}`);
  revalidatePath("/");
  redirect(`/obligations/${id}`);
}
