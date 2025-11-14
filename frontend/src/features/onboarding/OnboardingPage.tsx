import React, { useState } from "react";
import { useOnboardingFlow } from "./useOnboardingFlow";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

function StepIndicator({ step }: { step: "company" | "questions" | "completed" }) {
  const steps: { key: any; label: string }[] = [
    { key: "company", label: "Dados da empresa" },
    { key: "questions", label: "Perguntas da IA" },
    { key: "completed", label: "Perfil gerado" },
  ];

  const indexOf = (k: any) => steps.findIndex((s) => s.key === k);
  const currentIdx = indexOf(step);

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
        {steps.map((s, idx) => {
          const active = idx === currentIdx;
          const done = idx < currentIdx;
          return (
            <div
              key={s.key}
              className={cn(
                "flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs",
                active && "bg-slate-900 text-white border-slate-900",
                done && "bg-emerald-50 text-emerald-700 border-emerald-200",
                !active && !done && "bg-slate-50 border-slate-200"
              )}
            >
              <span className="font-medium">
                {idx + 1}. {s.label}
              </span>
              {done && <CheckCircle2 className="h-3.5 w-3.5" />}
            </div>
          );
        })}
      </div>
      <div className="h-1 rounded-full bg-slate-200 overflow-hidden">
        <div
          className="h-full bg-slate-900 transition-all"
          style={{ width: `${((currentIdx + 1) / steps.length) * 100}%` }}
        />
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  const {
    step,
    company,
    currentQuestion,
    loading,
    savingAnswer,
    error,
    createCompanyAndStart,
    answerCurrentQuestion,
  } = useOnboardingFlow();

  const [companyForm, setCompanyForm] = useState({
    name: "",
    website: "",
    sector: "",
  });
  const [answerText, setAnswerText] = useState("");

  async function handleSubmitCompany(e: React.FormEvent) {
    e.preventDefault();
    if (!companyForm.name.trim()) return;
    await createCompanyAndStart({
      name: companyForm.name.trim(),
      website: companyForm.website || undefined,
      sector: companyForm.sector || undefined,
    });
  }

  async function handleSubmitAnswer(e: React.FormEvent) {
    e.preventDefault();
    if (!answerText.trim()) return;
    await answerCurrentQuestion(answerText.trim());
    setAnswerText("");
  }

  const isLoading = loading || savingAnswer;

  return (
    <div className="p-6 lg:p-8 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500">
            Onboarding de empresa
          </div>
          <h1 className="text-2xl font-bold">
            Configurar nova empresa para curadoria
          </h1>
          <p className="text-sm text-slate-600 mt-1 max-w-xl">
            Vamos entender o perfil da empresa para que a IA consiga classificar
            notícias e sugerir conteúdos de forma alinhada à marca.
          </p>
        </div>
        <div className="min-w-[260px]">
          <StepIndicator step={step} />
        </div>
      </div>

      <Separator />

      {error && (
        <Card className="border-rose-200 bg-rose-50/60">
          <CardContent className="py-3 flex items-center gap-2 text-sm text-rose-700">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </CardContent>
        </Card>
      )}

      {step === "company" && (
        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle className="text-base">Dados iniciais da empresa</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleSubmitCompany}>
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">
                  Nome da empresa
                </label>
                <Input
                  value={companyForm.name}
                  onChange={(e) =>
                    setCompanyForm((f) => ({ ...f, name: e.target.value }))
                  }
                  placeholder="Ex.: Alpha Capital Family Office"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">
                  Website (opcional)
                </label>
                <Input
                  value={companyForm.website}
                  onChange={(e) =>
                    setCompanyForm((f) => ({ ...f, website: e.target.value }))
                  }
                  placeholder="https://empresa.com"
                />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">
                  Setor / segmento (opcional)
                </label>
                <Input
                  value={companyForm.sector}
                  onChange={(e) =>
                    setCompanyForm((f) => ({ ...f, sector: e.target.value }))
                  }
                  placeholder="Ex.: Family office, gestão de patrimônio..."
                />
              </div>

              <div className="flex items-center justify-between pt-2">
                <div className="text-xs text-slate-500">
                  Esses dados ajudam a IA a ter um ponto de partida mais
                  consistente.
                </div>
                <Button type="submit" disabled={isLoading}>
                  {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Iniciar perguntas
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {step === "questions" && currentQuestion && (
        <div className="grid lg:grid-cols-[minmax(0,2fr)_minmax(0,1.2fr)] gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                Perguntas para entender o perfil
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Badge variant="secondary" className="rounded-full">
                  Pergunta #{currentQuestion.order_index}
                </Badge>
                <span>
                  Origem:{" "}
                  <span className="font-medium">
                    {currentQuestion.origin === "system"
                      ? "Base do sistema"
                      : "Gerada pela IA"}
                  </span>
                </span>
              </div>

              <div className="rounded-2xl border px-4 py-3 bg-slate-50">
                <div className="text-sm text-slate-500 mb-1">Pergunta atual</div>
                <div className="text-base font-medium text-slate-900">
                  {currentQuestion.content}
                </div>
              </div>

              <form className="space-y-4" onSubmit={handleSubmitAnswer}>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Sua resposta
                  </label>
                  <Textarea
                    value={answerText}
                    onChange={(e) => setAnswerText(e.target.value)}
                    rows={5}
                    placeholder="Responda com detalhes suficientes para a IA entender bem o contexto da empresa..."
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-xs text-slate-500 max-w-md">
                    A IA pode fazer perguntas adicionais se achar que ainda
                    faltam informações para traçar o perfil completo da empresa.
                  </div>
                  <Button
                    type="submit"
                    disabled={isLoading || !answerText.trim()}
                  >
                    {isLoading && (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    )}
                    Enviar resposta
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card className="border-dashed">
            <CardHeader>
              <CardTitle className="text-base">
                Progresso do entendimento
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-slate-600">
              {company && (
                <div className="space-y-1">
                  <div className="text-xs uppercase tracking-wider text-slate-500">
                    Empresa
                  </div>
                  <div className="font-semibold">{company.name}</div>
                  {company.sector && (
                    <div className="text-xs text-slate-500">
                      Setor: {company.sector}
                    </div>
                  )}
                </div>
              )}
              <p>
                Depois que a IA considerar que já entendeu suficientemente o
                posicionamento da empresa, o perfil será consolidado
                automaticamente e você poderá ver como ela enxerga o tom, o
                público e os temas mais adequados para a comunicação.
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {step === "completed" && company && (
        <Card className="border-emerald-200 bg-emerald-50/60">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
              <CardTitle className="text-base">
                Perfil da empresa gerado com sucesso
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-slate-700">
            <div>
              <div className="text-xs uppercase tracking-wider text-slate-500">
                Empresa
              </div>
              <div className="font-semibold text-slate-900">
                {company.name}
              </div>
            </div>
            <p>
              A IA consolidou todas as respostas e gerou um perfil estruturado.
              Esse perfil será usado para classificar notícias, sugerir conteúdos
              e priorizar temas mais aderentes à marca.
            </p>
            {company.profile_json && (
              <pre className="text-xs bg-white/80 border rounded-xl p-3 overflow-x-auto">
{JSON.stringify(company.profile_json, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
