import { transitionAction } from "@/app/obligations/[id]/actions";
import { DEFAULT_LOCALE, getDictionary } from "@/lib/i18n";
import type { ObligationDetail, Status } from "@/lib/types";

function canTransitionTo(
  status: Status,
  requiresDocument: boolean,
  documentsLength: number,
): boolean {
  if (status === "submitted" && requiresDocument && documentsLength === 0) {
    return false;
  }
  return true;
}

export function TransitionButtons({ obligation }: { obligation: ObligationDetail }) {
  const t = getDictionary(DEFAULT_LOCALE);

  if (obligation.available_transitions.length === 0) {
    return <p className="text-sm text-zinc-500 dark:text-zinc-400">—</p>;
  }

  return (
    <form action={transitionAction} className="flex flex-wrap gap-2">
      <input type="hidden" name="obligation_id" value={obligation.id} />
      <input type="hidden" name="version" value={obligation.version} />
      {obligation.available_transitions.map((s) => {
        const disabled = !canTransitionTo(
          s,
          obligation.requires_document,
          obligation.documents.length,
        );
        return (
          <button
            key={s}
            type="submit"
            name="to_status"
            value={s}
            disabled={disabled}
            title={disabled ? t["transition.blocked_doc"] : undefined}
            className="rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:bg-zinc-200 disabled:text-zinc-500 dark:disabled:bg-zinc-800 dark:disabled:text-zinc-500"
          >
            {t["transition.button"]} {t[`status.${s}`]}
          </button>
        );
      })}
    </form>
  );
}
