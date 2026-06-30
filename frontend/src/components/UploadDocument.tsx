import { uploadDocumentAction } from "@/app/obligations/[id]/actions";
import { getRequestDictionary } from "@/lib/i18n-server";

export async function UploadDocument({ obligationId }: { obligationId: string }) {
  const t = await getRequestDictionary();
  return (
    <form
      action={uploadDocumentAction}
      encType="multipart/form-data"
      className="flex flex-wrap items-center gap-2"
    >
      <input type="hidden" name="obligation_id" value={obligationId} />
      <input
        type="file"
        name="file"
        required
        className="text-sm text-zinc-700 file:mr-2 file:rounded-md file:border-0 file:bg-zinc-100 file:px-3 file:py-1.5 file:text-sm file:font-medium hover:file:bg-zinc-200 dark:text-zinc-200 dark:file:bg-zinc-800 dark:hover:file:bg-zinc-700"
      />
      <button
        type="submit"
        className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-primary/90"
      >
        {t["documents.upload"]}
      </button>
    </form>
  );
}
