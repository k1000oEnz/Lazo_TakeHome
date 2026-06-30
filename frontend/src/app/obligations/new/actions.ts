"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { ApiError, serverApi } from "@/lib/api-server";

export async function createObligationAction(formData: FormData) {
  const data = {
    type: formData.get("type") as string,
    title: (formData.get("title") as string | null) ?? "",
    description: ((formData.get("description") as string | null) ?? "").trim() || null,
    due_date: formData.get("due_date") as string,
    owner: (formData.get("owner") as string | null) ?? "",
    requires_document: formData.get("requires_document") === "on",
    company_tax_id: (formData.get("company_tax_id") as string | null) ?? "",
  };

  let created: { id: string };
  try {
    created = (await serverApi.createObligation(data)) as { id: string };
  } catch (error) {
    if (error instanceof ApiError && error.status === 422) {
      redirect("/obligations/new?error=generic");
    }
    throw error;
  }

  revalidatePath("/");
  redirect(`/obligations/${created.id}`);
}
