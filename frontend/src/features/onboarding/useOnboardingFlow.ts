import { useCallback, useState } from "react";
import { api } from "@/lib/api";

export type Company = {
  id: string;
  name: string;
  website?: string;
  sector?: string;
  onboarding_status: string;
  profile_json?: any;
};

export type Question = {
  id: string;
  company_id: string;
  content: string;
  order_index: number;
  origin: string;
  created_at: string;
};

type Step = "company" | "questions" | "completed";

export function useOnboardingFlow() {
  const [step, setStep] = useState<Step>("company");
  const [company, setCompany] = useState<Company | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(false);
  const [savingAnswer, setSavingAnswer] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCompanyAndStart = useCallback(
    async (data: { name: string; website?: string; sector?: string }) => {
      setLoading(true);
      setError(null);
      try {
        const created = await api<Company>("/companies", {
          method: "POST",
          body: JSON.stringify(data),
        });

        setCompany(created);

        await api(`/onboarding/${created.id}/start`, {
          method: "POST",
        });

        const q = await api<Question>(`/onboarding/${created.id}/next`);
        setCurrentQuestion(q);
        setStep("questions");
      } catch (err: any) {
        setError(err.message || "Erro ao iniciar onboarding");
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const fetchNextQuestion = useCallback(async (companyId: string) => {
    try {
      const q = await api<Question>(`/onboarding/${companyId}/next`);
      setCurrentQuestion(q);
      setStep("questions");
    } catch (err: any) {
      if (String(err.message).includes("Nenhuma pergunta pendente")) {
        setCurrentQuestion(null);
      } else {
        throw err;
      }
    }
  }, []);

  const answerCurrentQuestion = useCallback(
    async (answerText: string) => {
      if (!company || !currentQuestion) return;
      setSavingAnswer(true);
      setError(null);
      try {
        await api(`/onboarding/${company.id}/answer`, {
          method: "POST",
          body: JSON.stringify({
            company_id: company.id,
            question_id: currentQuestion.id,
            content: answerText,
          }),
        });

        const evalResult = await api<{
          status: string;
          precisa_mais?: boolean;
          novas_perguntas?: string[];
        }>(`/onboarding/${company.id}/ai/evaluate`, {
          method: "POST",
        });

        if (evalResult.status === "new_questions_created") {
          await fetchNextQuestion(company.id);
          return;
        }

        if (evalResult.status === "sufficient") {
          const updatedCompany = await api<Company>(
            `/companies/${company.id}/profile/generate`,
            { method: "POST" }
          );
          setCompany(updatedCompany);
          setCurrentQuestion(null);
          setStep("completed");
          return;
        }

        await fetchNextQuestion(company.id);
      } catch (err: any) {
        setError(err.message || "Erro ao salvar resposta");
      } finally {
        setSavingAnswer(false);
      }
    },
    [company, currentQuestion, fetchNextQuestion]
  );

  return {
    step,
    company,
    currentQuestion,
    loading,
    savingAnswer,
    error,
    createCompanyAndStart,
    answerCurrentQuestion,
  };
}
