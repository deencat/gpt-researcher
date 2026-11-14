'use client';

import { useMemo, useState } from 'react';
import {
  draftFromAnswers,
  FORMAT_OPTIONS,
  guessFromTitle,
  LANGUAGE_OPTIONS,
  MATERIAL_OPTIONS,
  type SetupAnswers,
} from '@/lib/research/projectSetup';

type Draft = ReturnType<typeof draftFromAnswers>;

const steps = ['goal', 'languages', 'formats', 'materials', 'constraints', 'review'] as const;
type Step = (typeof steps)[number];

function Chip({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`border px-3 py-2 text-left text-[13.5px] transition-colors ${
        active ? 'border-ink bg-ink text-paper' : 'border-rule-soft text-ink-2 hover:border-ink hover:text-ink'
      }`}
    >
      {children}
    </button>
  );
}

function toggle(list: string[], id: string) {
  return list.includes(id) ? list.filter((x) => x !== id) : [...list, id];
}

export default function ProjectSetupCoach({
  title,
  open,
  onClose,
  onApply,
}: {
  title: string;
  open: boolean;
  onClose: () => void;
  onApply: (draft: Draft) => void;
}) {
  const guessed = useMemo(() => guessFromTitle(title), [title]);
  const [step, setStep] = useState<Step>('goal');
  const [answers, setAnswers] = useState<SetupAnswers>({
    goal: guessed.goal || '',
    languages: guessed.languages || [],
    formats: guessed.formats || [],
    materials: guessed.materials || [],
    constraints: guessed.constraints || '',
  });

  if (!open) return null;

  const index = steps.indexOf(step);
  const draft = draftFromAnswers(title, answers);
  const canNext =
    step === 'goal'
      ? Boolean(answers.goal.trim())
      : step === 'languages'
        ? answers.languages.length > 0
        : step === 'formats'
          ? answers.formats.length > 0
          : step === 'materials'
            ? answers.materials.length > 0
            : true;

  const next = () => {
    if (index < steps.length - 1) setStep(steps[index + 1]);
  };
  const back = () => {
    if (index > 0) setStep(steps[index - 1]);
  };

  return (
    <section className="mt-8 border border-rule bg-ink/[0.02] px-5 py-5 sm:px-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-code text-[11px] tracking-[0.08em] text-ink-3">
            SETUP {index + 1}/{steps.length}
          </p>
          <h2 className="mt-1 text-[16px] font-semibold tracking-[-0.01em]">Help me fill this project</h2>
          <p className="mt-1 max-w-[42em] text-[13.5px] leading-relaxed text-ink-2">
            You only have a title so far. Answer a few questions and we will draft the description, system instructions,
            document ideas, and first research prompts.
          </p>
        </div>
        <button type="button" className="shrink-0 text-[13px] text-ink-3 hover:text-ink" onClick={onClose}>
          Dismiss
        </button>
      </div>

      <div className="mt-6">
        {step === 'goal' && (
          <label className="block text-[13px] font-medium text-ink-2">
            What are you trying to build?
            <textarea
              value={answers.goal}
              onChange={(e) => setAnswers({ ...answers, goal: e.target.value })}
              rows={4}
              className="mt-2 w-full border border-rule-soft bg-paper px-3 py-2 text-[14.5px] outline-none focus:border-ink"
              placeholder="e.g. A multilingual joke & format library for world-class funny shorts…"
            />
          </label>
        )}

        {step === 'languages' && (
          <fieldset>
            <legend className="text-[13px] font-medium text-ink-2">Which languages / markets?</legend>
            <p className="mt-1 text-[13px] text-ink-3">Pick all that apply. Chinese dialects stay separate.</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {LANGUAGE_OPTIONS.map((opt) => (
                <Chip
                  key={opt.id}
                  active={answers.languages.includes(opt.id)}
                  onClick={() => setAnswers({ ...answers, languages: toggle(answers.languages, opt.id) })}
                >
                  {opt.label}
                </Chip>
              ))}
            </div>
          </fieldset>
        )}

        {step === 'formats' && (
          <fieldset>
            <legend className="text-[13px] font-medium text-ink-2">What will you publish?</legend>
            <div className="mt-3 flex flex-wrap gap-2">
              {FORMAT_OPTIONS.map((opt) => (
                <Chip
                  key={opt.id}
                  active={answers.formats.includes(opt.id)}
                  onClick={() => setAnswers({ ...answers, formats: toggle(answers.formats, opt.id) })}
                >
                  {opt.label}
                </Chip>
              ))}
            </div>
          </fieldset>
        )}

        {step === 'materials' && (
          <fieldset>
            <legend className="text-[13px] font-medium text-ink-2">What should research collect first?</legend>
            <div className="mt-3 flex flex-wrap gap-2">
              {MATERIAL_OPTIONS.map((opt) => (
                <Chip
                  key={opt.id}
                  active={answers.materials.includes(opt.id)}
                  onClick={() => setAnswers({ ...answers, materials: toggle(answers.materials, opt.id) })}
                >
                  {opt.label}
                </Chip>
              ))}
            </div>
          </fieldset>
        )}

        {step === 'constraints' && (
          <label className="block text-[13px] font-medium text-ink-2">
            Any hard rules? (optional)
            <textarea
              value={answers.constraints}
              onChange={(e) => setAnswers({ ...answers, constraints: e.target.value })}
              rows={3}
              className="mt-2 w-full border border-rule-soft bg-paper px-3 py-2 text-[14.5px] outline-none focus:border-ink"
              placeholder="e.g. Family-friendly; no political jokes for Mainland distribution; keep Cantonese punchlines natural…"
            />
          </label>
        )}

        {step === 'review' && (
          <div className="space-y-5 text-[14px]">
            <div>
              <h3 className="text-[13px] font-medium text-ink-2">Draft description</h3>
              <p className="mt-2 whitespace-pre-wrap text-[14.5px] leading-relaxed text-ink">{draft.description}</p>
            </div>
            <div>
              <h3 className="text-[13px] font-medium text-ink-2">Draft system instructions</h3>
              <pre className="mt-2 max-h-56 overflow-auto whitespace-pre-wrap border border-rule-soft bg-paper px-3 py-2 font-code text-[12.5px] leading-relaxed text-ink">
                {draft.instructions}
              </pre>
            </div>
            <div>
              <h3 className="text-[13px] font-medium text-ink-2">Suggested documents to add later</h3>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-[13.5px] text-ink-2">
                {draft.documentIdeas.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-[13px] font-medium text-ink-2">First research prompts</h3>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-[13.5px] text-ink-2">
                {draft.researchPrompts.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        {index > 0 && (
          <button type="button" className="gr-btn-line h-10 px-4" onClick={back}>
            Back
          </button>
        )}
        {step !== 'review' ? (
          <button type="button" className="gr-btn h-10 px-4 disabled:opacity-40" disabled={!canNext} onClick={next}>
            Continue
          </button>
        ) : (
          <button
            type="button"
            className="gr-btn h-10 px-4"
            onClick={() => {
              onApply(draft);
              onClose();
            }}
          >
            Apply to project fields
          </button>
        )}
      </div>
    </section>
  );
}
