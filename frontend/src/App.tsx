import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
// import { Progress } from "@/components/ui/progress"; // não usado
import { TooltipProvider } from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetFooter } from "@/components/ui/sheet";
import { Switch } from "@/components/ui/switch";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
  Activity,
  AlarmClock,
  Archive,
  Bell,
  Bookmark,
  Brain,
  CalendarClock,
  Check,
  ChevronDown,
  ChevronRight,
  FileText,
  Filter,
  Globe,
  Hash,
  History,
  LineChart,
  MessagesSquare,
  Newspaper,
  PlayCircle,
  Search,
  Settings,
  Share2,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Home,
  LayoutDashboard,
  Building2,
} from "lucide-react";
import OnboardingPage from "@/features/onboarding/OnboardingPage";

/* ==========================
   Dados base / constantes
========================== */
const STATUS = {
  POSTAR: "postar",
  MONITORAR: "monitorar",
  DESCARTAR: "descartar",
  EM_PROCESSO: "em_processo",
} as const;

const PIPE_STEPS = [
  { key: "fetch", label: "Coleta" },
  { key: "classify", label: "Classificação" },
  { key: "score", label: "Pontuação" },
  { key: "draft", label: "Rascunho" },
  { key: "review", label: "Revisão" },
  { key: "schedule", label: "Agendamento" },
  { key: "publish", label: "Publicação" },
] as const;

const SOURCES = ["Valor", "Reuters", "G1", "BBC", "InfoMoney", "Folha", "Estadão"];
const THEMES = [
  { key: "planejamento_patrimonial", label: "Planejamento Patrimonial" },
  { key: "sucessao", label: "Sucessão" },
  { key: "governanca_familiar", label: "Governança Familiar" },
  { key: "gestao_de_risco", label: "Gestão de Risco" },
  { key: "tributacao", label: "Tributação" },
  { key: "mercado_financeiro", label: "Mercado" },
];

const TENANTS = [
  { id: "alpha", name: "Alpha Capital" },
  { id: "orion", name: "Orion Family Office" },
  { id: "vertex", name: "Vertex Investimentos" },
];

/* ==========================
   Utilitários UI
========================== */
function sentimentBadge(sentiment: "positivo" | "neutro" | "negativo") {
  const map = {
    positivo: "bg-emerald-100 text-emerald-700",
    neutro: "bg-slate-100 text-slate-700",
    negativo: "bg-rose-100 text-rose-700",
  } as const;
  return <Badge className={cn("rounded-full", map[sentiment])}>{sentiment}</Badge>;
}

function SourceAvatar({ source }: { source: string }) {
  const initials = source
    .split(/\s|\-/)
    .map((s) => s.trim()[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
  return (
    <Avatar className="h-8 w-8 border">
      <AvatarFallback>{initials}</AvatarFallback>
    </Avatar>
  );
}

function ScoreRing({ score }: { score: number }) {
  const radius = 18;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(100, Math.max(0, score));
  const offset = circumference - (pct / 100) * circumference;
  // limiares alinhados com a decisão: >=70 verde, 50-69 âmbar, <50 vermelho
  const color = score >= 70 ? "stroke-emerald-500" : score >= 50 ? "stroke-amber-500" : "stroke-rose-500";
  return (
    <svg width="48" height="48" className="shrink-0">
      <circle cx="24" cy="24" r={radius} strokeWidth="6" className="stroke-slate-200 fill-none" />
      <circle
        cx="24"
        cy="24"
        r={radius}
        strokeWidth="6"
        className={cn("fill-none transition-all", color)}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
      />
      <text x="50%" y="52%" textAnchor="middle" className="text-xs font-semibold fill-slate-700">
        {score}
      </text>
    </svg>
  );
}

function StepBar({ step }: { step: typeof PIPE_STEPS[number]["key"] }) {
  const idx = PIPE_STEPS.findIndex((s) => s.key === step);
  const pct = Math.max(0, Math.min(100, ((idx + 1) / PIPE_STEPS.length) * 100));

  return (
    <div className="space-y-2">
      {/* “chips” dos passos */}
      <div className="flex flex-wrap items-center gap-1 text-[11px] text-slate-500">
        {PIPE_STEPS.map((s, i) => (
          <span
            key={s.key}
            className={cn("px-1.5 py-0.5 rounded-md", i <= idx ? "bg-slate-100 text-slate-800" : "bg-transparent")}
          >
            {s.label}
          </span>
        ))}
      </div>

      {/* Barra de progresso própria (independente do shadcn) */}
      <div className="w-full h-2 rounded-full bg-slate-200 overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-[width] duration-500",
            idx >= PIPE_STEPS.length - 1 ? "bg-emerald-500" : idx >= 2 ? "bg-amber-500" : "bg-slate-500"
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function EyeIcon(props: any) {
  return (
    <svg viewBox="0 0 24 24" width="1em" height="1em" {...props}>
      <path
        fill="currentColor"
        d="M12 5c-7 0-11 7-11 7s4 7 11 7 11-7 11-7-4-7-11-7zm0 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-2a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
      />
    </svg>
  );
}

/* ==========================
   Mock de dados e stream
========================== */
function decisionFromScore(score: number) {
  if (score >= 70) return STATUS.POSTAR;
  if (score >= 50) return STATUS.MONITORAR;
  return STATUS.DESCARTAR;
}

function makeMockItem(i: number, salt = 0) {
  const k = i + salt;
  const source = SOURCES[k % SOURCES.length];
  const theme = THEMES[k % THEMES.length];
  const publishedMinutesAgo = Math.floor((k * 13) % 180);
  const sentiment = (["positivo", "neutro", "negativo"] as const)[k % 3];
  const baseScore = 30 + (k % 70); // 30..99 para dar dispersão boa
  const stepIdx = Math.min(k % PIPE_STEPS.length, PIPE_STEPS.length - 1);

  const item = {
    id: `news_${k}`,
    title: `${source}: ${theme.label} em destaque ${k}`,
    url: "https://example.com/noticia",
    source,
    theme,
    publishedAt: new Date(Date.now() - publishedMinutesAgo * 60000).toISOString(),
    sentiment,
    score: baseScore,
    step: PIPE_STEPS[stepIdx].key as typeof PIPE_STEPS[number]["key"],
    decision: decisionFromScore(baseScore),
    draft: {
      caption: `📊 ${theme.label}: análise rápida e implicações para o público da marca.

• Ponto principal #${k}
• Impacto tributário e sucessório
• Próximos passos práticos

#${theme.key} #curadoria #estrategia`,
      hashtags: ["#curadoria", "#governança", "#estratégia"],
      tone: "profissional",
    },
    activity: [
      { t: Date.now() - 90_000, msg: "Coleta realizada", icon: "fetch" },
      { t: Date.now() - 70_000, msg: "Classificação preliminar", icon: "classify" },
      { t: Date.now() - 40_000, msg: `Score calculado (${baseScore})`, icon: "score" },
    ],
  } as const;

  return item;
}

function hashSeed(s: string) {
  let h = 0 >>> 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}

function useMockStream(tenantId: string, count = 18, tickMs = 3500) {
  const salt = hashSeed(tenantId) % 997;
  const [items, setItems] = useState(() => Array.from({ length: count }, (_, i) => makeMockItem(i + 1, salt)));
  const [live, setLive] = useState(true);

  // Reinicializa o conjunto quando o tenant muda
  useEffect(() => {
    const newSalt = hashSeed(tenantId) % 997;
    setItems(Array.from({ length: count }, (_, i) => makeMockItem(i + 1, newSalt)));
  }, [tenantId, count]);

  useEffect(() => {
    if (!live) return;
    const iv = setInterval(() => {
      setItems((prev) => {
        const copy = [...prev];

        for (let j = 0; j < 2; j++) {
          const idx = Math.floor(Math.random() * copy.length);
          const it = { ...copy[idx] } as any;

          // recalcula score levemente (ruído) e decisão
          const delta = Math.random() > 0.5 ? 1 : -1;
          it.score = Math.min(100, Math.max(0, it.score + delta));
          it.decision = decisionFromScore(it.score);

          const stepIndex = PIPE_STEPS.findIndex((s) => s.key === it.step);

          // Regras:
          // - MONITORAR: não avança automaticamente (para não gastar token)
          // - DESCARTAR: não avança (fica parado)
          // - POSTAR: avança até "publish" e para lá (aguardando autorização)
          if (it.decision === STATUS.POSTAR) {
            if (stepIndex < PIPE_STEPS.length - 1) {
              it.step = PIPE_STEPS[stepIndex + 1].key;
              it.activity = [
                ...it.activity,
                { t: Date.now(), msg: `${PIPE_STEPS[stepIndex + 1].label} concluída`, icon: PIPE_STEPS[stepIndex + 1].key },
              ];
            } else {
              // já está em publish → apenas log leve ocasional
              if (Math.random() < 0.25) {
                it.activity = [...it.activity, { t: Date.now(), msg: "Publicação aguardando autorização", icon: "publish" }];
              }
            }
          } else if (it.decision === STATUS.MONITORAR) {
            // não avança: apenas loga que segue em avaliação
            if (Math.random() < 0.25) {
              it.activity = [...it.activity, { t: Date.now(), msg: "Em monitoramento (aguardando revisão)", icon: "review" }];
            }
          } else {
            // DESCARTAR → parado; ocasionalmente log
            if (Math.random() < 0.15) {
              it.activity = [...it.activity, { t: Date.now(), msg: "Mantido como descartado", icon: "score" }];
            }
          }

          copy[idx] = it;
        }
        return copy;
      });
    }, tickMs);
    return () => clearInterval(iv);
  }, [tickMs, live]);

  return { items, setItems, live, setLive } as const;
}

/* ==========================
   Componentes de UI
========================== */
function PipelineCard({ item, onOpen }: { item: any; onOpen: (item: any) => void }) {
  return (
    <Card className="hover:shadow-md transition-shadow overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          {/* Esquerda + miolo */}
          <div className="flex items-start gap-3 min-w-0">
            <SourceAvatar source={item.source} />
            <div className="min-w-0">
              <CardTitle className="text-base leading-snug line-clamp-2 break-words">{item.title}</CardTitle>

              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-600">
                <Badge variant="secondary" className="rounded-full">
                  {item.source}
                </Badge>
                <Badge className="rounded-full bg-slate-900 text-white">{item.theme.label}</Badge>
                {sentimentBadge(item.sentiment)}
                <div className="flex items-center gap-1 text-slate-500">
                  <AlarmClock className="h-3.5 w-3.5" />
                  <span>{new Date(item.publishedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Direita */}
          <div className="flex items-center gap-3 shrink-0">
            <ScoreRing score={item.score} />
            <Badge
              className={cn(
                "rounded-full px-3 py-1 capitalize",
                item.decision === STATUS.POSTAR && "bg-emerald-600",
                item.decision === STATUS.MONITORAR && "bg-amber-500",
                item.decision === STATUS.DESCARTAR && "bg-slate-400"
              )}
            >
              {item.decision}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0 space-y-3">
        <StepBar step={item.step} />
        <div className="flex flex-wrap gap-2">
          <Button size="sm" onClick={() => onOpen(item)}>
            <EyeIcon className="h-4 w-4 mr-2" />
            Ver detalhes
          </Button>
          <Button size="sm" variant="secondary" onClick={() => window.open(item.url, "_blank")}>
            <Globe className="h-4 w-4 mr-2" /> Fonte
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function Metric({ label, value, icon: Icon, trend }: { label: string; value: string; icon: any; trend?: string }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm text-slate-500 font-medium">{label}</CardTitle>
          <Icon className="h-4 w-4 text-slate-400" />
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="text-2xl font-semibold">{value}</div>
        {trend && <div className="text-xs text-slate-500 mt-1">{trend}</div>}
      </CardContent>
    </Card>
  );
}

function FiltersBar({
  q,
  setQ,
  selectedThemes,
  toggleTheme,
  autoRefresh,
  setAutoRefresh,
}: {
  q: string;
  setQ: (v: string) => void;
  selectedThemes: string[];
  toggleTheme: (k: string) => void;
  autoRefresh: boolean;
  setAutoRefresh: (v: boolean) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <div className="relative">
        <Search className="h-4 w-4 absolute left-2 top-1/2 -translate-y-1/2 text-slate-400" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Buscar por título, fonte..."
          className="pl-8 w-[280px]"
        />
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Temas
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="z-50 w-72 bg-white border shadow-md">
          <DropdownMenuLabel>Filtrar por temas</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {THEMES.map((t) => (
            <DropdownMenuItem key={t.key} className="flex items-center gap-2" onSelect={(e) => e.preventDefault()}>
              <Checkbox
                id={`chk_${t.key}`}
                checked={selectedThemes.includes(t.key)}
                onCheckedChange={() => toggleTheme(t.key)}
              />
              <Label htmlFor={`chk_${t.key}`} className="cursor-pointer">
                {t.label}
              </Label>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <div className="ml-auto flex items-center gap-2 text-sm text-slate-600">
        <Sparkles className="h-4 w-4" />
        <span>Atualização automática</span>
        <Switch
          checked={autoRefresh}
          onCheckedChange={setAutoRefresh}
          className="data-[state=checked]:bg-slate-900"
        />
      </div>
    </div>
  );
}

function ActivityLog({ activity }: { activity: { t: number; msg: string; icon: string }[] }) {
  const iconMap: Record<string, any> = {
    fetch: Newspaper,
    classify: Brain,
    score: LineChart,
    draft: FileText,
    review: MessagesSquare,
    schedule: CalendarClock,
    publish: PlayCircle,
  };
  return (
    <div className="space-y-2">
      {activity
        .slice(-6)
        .reverse()
        .map((a, idx) => {
          const Icon = iconMap[a.icon] ?? Activity;
          return (
            <div key={idx} className="flex items-center gap-2 text-sm">
              <Icon className="h-4 w-4 text-slate-500" />
              <span className="text-slate-700">{a.msg}</span>
              <span className="ml-auto text-xs text-slate-500">
                {new Date(a.t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          );
        })}
    </div>
  );
}

function PostPreview({ item }: { item: any }) {
  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <div className="text-sm text-slate-500">Prévia de Post</div>
        <div className="rounded-2xl border p-4">
          <div className="text-base font-semibold leading-snug mb-1">{item.title}</div>
          <div className="text-sm whitespace-pre-wrap">{item.draft.caption}</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {item.draft.hashtags.map((h: string) => (
              <Badge key={h} variant="secondary" className="rounded-full">
                <Hash className="h-3 w-3 mr-1" />
                {h}
              </Badge>
            ))}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Button size="sm">
          <Check className="h-4 w-4 mr-2" />
          Aprovar para publicação
        </Button>
        <Button size="sm" variant="outline">
          <ThumbsDown className="h-4 w-4 mr-2" />
          Reprovar / Ajustar
        </Button>
      </div>
    </div>
  );
}

function DetailsDrawer({ item, open, setOpen }: { item: any; open: boolean; setOpen: (v: boolean) => void }) {
  if (!item) return null;
  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent className="w-[520px] sm:max-w-[520px] bg-white shadow-xl">
        <SheetHeader>
          <SheetTitle>Detalhes</SheetTitle>
        </SheetHeader>
        <div className="mt-4 space-y-6">
          <div className="flex items-start gap-3">
            <SourceAvatar source={item.source} />
            <div>
              <div className="text-sm text-slate-500">
                {item.source} • {item.theme.label}
              </div>
              <div className="font-semibold leading-snug">{item.title}</div>
              <div className="mt-1 flex items-center gap-2 text-xs text-slate-600">
                {sentimentBadge(item.sentiment)}
                <Badge variant="secondary" className="rounded-full">
                  Score {item.score}
                </Badge>
                <a className="underline decoration-dotted" href={item.url} target="_blank" rel="noreferrer">
                  Abrir fonte
                </a>
              </div>
            </div>
          </div>

          <div>
            <div className="text-sm text-slate-500 mb-2">Pipeline</div>
            <StepBar step={item.step} />
          </div>

          <div>
            <div className="text-sm text-slate-500 mb-2">Atividade recente</div>
            <ActivityLog activity={item.activity} />
          </div>

          <Separator />

          <PostPreview item={item} />

          <Separator />

          <div className="space-y-2">
            <div className="text-sm text-slate-500">Feedback rápido</div>
            <Textarea placeholder="Deixe uma observação para a IA aprender com esta decisão (opcional)" />
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Bookmark className="h-4 w-4 mr-2" />
                Salvar feedback
              </Button>
              <Button variant="ghost" size="sm">
                <Share2 className="h-4 w-4 mr-2" />
                Compartilhar
              </Button>
            </div>
          </div>
        </div>
        <SheetFooter className="mt-6" />
      </SheetContent>
    </Sheet>
  );
}

function Column({ title, icon: Icon, items, onOpen }: { title: string; icon: any; items: any[]; onOpen: (item: any) => void }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-slate-700">
        <Icon className="h-4 w-4" />
        <span className="font-medium">{title}</span>
        <Badge variant="secondary" className="rounded-full ml-2">
          {items.length}
        </Badge>
      </div>
      <div className="grid gap-4 auto-rows-max">
        {items.map((it) => (
          <PipelineCard key={it.id} item={it} onOpen={onOpen} />
        ))}
      </div>
    </div>
  );
}

function HeaderBar() {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-slate-500">Monitoramento Inteligente de Conteúdos</div>
      <h1 className="text-2xl font-bold">Painel de Curadoria em Tempo Real</h1>
    </div>
  );
}

/* ==========================
   Página: Início (Pipelines)
========================== */
function ContentCuratorDashboard({ tenant }: { tenant?: { id: string; name: string } }) {
  const { items, setItems, live, setLive } = useMockStream(tenant?.id ?? "default");
  const [q, setQ] = useState("");
  const [themes, setThemes] = useState<string[]>([]);
  const [tab, setTab] = useState("agora");
  const [detail, setDetail] = useState<any | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const filtered = useMemo(() => {
    return items.filter((it) => {
      const searchOk = q
        ? (it.title?.toLowerCase() || "").includes(q.toLowerCase()) ||
          (it.source?.toLowerCase() || "").includes(q.toLowerCase())
        : true;
      const themeOk = themes.length ? themes.includes(it.theme.key) : true;
      return searchOk && themeOk;
    });
  }, [items, q, themes]);

  const postar = filtered.filter((i) => i.decision === STATUS.POSTAR);
  const monitorar = filtered.filter((i) => i.decision === STATUS.MONITORAR);
  const descartar = filtered.filter((i) => i.decision === STATUS.DESCARTAR);

  function openDetails(it: any) {
    setDetail(it);
    setDrawerOpen(true);
  }

  function toggleTheme(k: string) {
    setThemes((prev) => (prev.includes(k) ? prev.filter((x) => x !== k) : [...prev, k]));
  }

  useEffect(() => {
    setLive(tab === "agora");
  }, [tab]);

  const autoRefresh = live;

  return (
    <TooltipProvider>
      <div className="p-6 lg:p-8 space-y-6">
        <div className="flex flex-wrap items-start gap-6">
          {/* Esquerda: título */}
          <div className="flex-1 min-w-[260px]">
            <HeaderBar />
          </div>

          {/* Direita: métricas + badge da empresa */}
          <div className="ml-auto flex items-start gap-3">
            <div className="grid grid-cols-3 gap-3 min-w-[480px]">
              <Metric label="Prontos para Postar" value={String(postar.length)} icon={Sparkles} trend="Hoje" />
              <Metric label="Em Monitoramento" value={String(monitorar.length)} icon={History} trend="Últimas 3h" />
              <Metric label="Descartados" value={String(descartar.length)} icon={Archive} trend="Hoje" />
            </div>
            {tenant && (
              <Badge className="rounded-full bg-slate-900 text-white whitespace-nowrap self-start" title="Empresa ativa">
                {tenant.name}
              </Badge>
            )}
          </div>
        </div>
        <Separator />

        <div className="flex flex-col gap-4">
          <FiltersBar
            q={q}
            setQ={setQ}
            selectedThemes={themes}
            toggleTheme={toggleTheme}
            autoRefresh={autoRefresh}
            setAutoRefresh={(v) => setLive(v)}
          />

          <Tabs value={tab} onValueChange={setTab} className="mt-2">
            <TabsList className="grid grid-cols-4 w-full md:w-auto">
              <TabsTrigger value="agora">Agora</TabsTrigger>
              <TabsTrigger value="fila">Fila</TabsTrigger>
              <TabsTrigger value="publicados">Publicados</TabsTrigger>
              <TabsTrigger value="historico">Histórico</TabsTrigger>
            </TabsList>

            <TabsContent value="agora" className="mt-6">
              {filtered.length === 0 ? (
                <div className="rounded-2xl border p-10 text-center">
                  <Sparkles className="h-8 w-8 mx-auto mb-3" />
                  <div className="text-lg font-semibold mb-1">Nada por aqui ainda</div>
                  <div className="text-slate-600">
                    A IA começará a preencher esta área à medida que novas notícias forem processadas.
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <Column title="Para Postar" icon={Sparkles} items={postar} onOpen={openDetails} />
                  <Column title="Monitorar" icon={History} items={monitorar} onOpen={openDetails} />
                  <Column title="Descartado" icon={Archive} items={descartar} onOpen={openDetails} />
                </div>
              )}
            </TabsContent>

            <TabsContent value="fila" className="mt-6">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filtered.map((it) => (
                  <PipelineCard key={it.id} item={it} onOpen={openDetails} />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="publicados" className="mt-6">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filtered
                  .filter((it) => it.step === "publish")
                  .map((it) => (
                    <PipelineCard key={it.id} item={it} onOpen={openDetails} />
                  ))}
              </div>
            </TabsContent>

            <TabsContent value="historico" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Linha do tempo (recente)</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[360px] pr-4">
                    <div className="space-y-4">
                      {filtered
                        .flatMap((it) => it.activity.map((a: any) => ({ ...a, id: it.id, ref: it })))
                        .sort((a, b) => b.t - a.t)
                        .slice(0, 40)
                        .map((a: any, idx: number) => (
                          <div key={idx} className="flex items-start gap-3">
                            <SourceAvatar source={a.ref.source} />
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium line-clamp-1">{a.ref.title}</div>
                              <div className="text-sm text-slate-600">{a.msg}</div>
                            </div>
                            <div className="text-xs text-slate-500 mt-0.5">
                              {new Date(a.t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </div>
                            <Button size="icon" variant="ghost" onClick={() => openDetails(a.ref)}>
                              <ChevronRight className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <DetailsDrawer item={detail} open={drawerOpen} setOpen={setDrawerOpen} />
      </div>
    </TooltipProvider>
  );
}

/* ==========================
   Páginas: Dashboard & Config
========================== */
function DashboardPage() {
  return (
    <div className="p-6 lg:p-8 space-y-6">
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500">Visão geral</div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <Metric label="Precisão da IA (7d)" value="92%" icon={Sparkles} trend="+3pp" />
        <Metric label="Tempo até publicar" value="12min" icon={CalendarClock} trend="-2min" />
        <Metric label="Aprovações humanas" value="68%" icon={ThumbsUp} trend="Últimas 24h" />
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Top temas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {THEMES.map((t) => (
              <Badge key={t.key} variant="secondary" className="rounded-full">
                {t.label}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function SettingsPage() {
  const [weights, setWeights] = useState({
    temporal: 0.3,
    autoridade: 0.25,
    engajamento: 0.15,
    aderencia: 0.25,
    qualidade: 0.05,
  });
  function Range({ label, k }: { label: string; k: keyof typeof weights }) {
    return (
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span>{label}</span>
          <span>{Math.round(weights[k] * 100)}%</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={weights[k] * 100}
          onChange={(e) => setWeights((w) => ({ ...w, [k]: Number(e.target.value) / 100 }))}
          className="w-full"
        />
      </div>
    );
  }
  return (
    <div className="p-6 lg:p-8 space-y-6">
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500">Preferências</div>
        <h1 className="text-2xl font-bold">Configurações</h1>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Pesos de decisão</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Range label="Relevância temporal" k="temporal" />
          <Range label="Autoridade da fonte" k="autoridade" />
          <Range label="Engajamento" k="engajamento" />
          <Range label="Aderência à marca" k="aderencia" />
          <Range label="Qualidade editorial" k="qualidade" />
          <div className="pt-2">
            <Button>Salvar alterações</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Fontes monitoradas</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {SOURCES.map((s) => (
            <div key={s} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <SourceAvatar source={s} />
                <span>{s}</span>
              </div>
              <Switch defaultChecked className="data-[state=checked]:bg-slate-900" />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

/* ==========================
   Shell / Navegação
========================== */
function CompanySwitcher({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const current = TENANTS.find((t) => t.id === value);
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Building2 className="h-4 w-4" />
          <span className="truncate max-w-[160px]">{current?.name ?? "Selecionar empresa"}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="z-50 w-64 bg-white border shadow-md">
        <DropdownMenuLabel>Trocar de empresa</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {TENANTS.map((t) => (
          <DropdownMenuItem key={t.id} onClick={() => onChange(t.id)} className="flex items-center gap-2">
            <Avatar className="h-6 w-6 border">
              <AvatarFallback>
                {t.name
                  .split(/\s|\-/)
                  .map((s) => s[0])
                  .slice(0, 2)
                  .join("")
                  .toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="truncate">{t.name}</span>
            {t.id === value && <Check className="ml-auto h-4 w-4" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function SidebarNav({ route, setRoute }: { route: string; setRoute: (r: string) => void }) {
  const items = [
    { key: "inicio", label: "Início", icon: Home },
    { key: "onboarding", label: "Nova empresa", icon: Building2 },
    { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { key: "config", label: "Configurações", icon: Settings },
  ];
  return (
    <div className="h-full p-4 space-y-4">
      <div>
        <div className="text-xs uppercase tracking-wider text-slate-500">Conteúdo IA</div>
        <div className="text-lg font-bold">Curadoria</div>
      </div>
      <nav className="space-y-1">
        {items.map((it) => {
          const Icon = it.icon as any;
          const active = route === it.key;
          return (
            <button
              key={it.key}
              onClick={() => setRoute(it.key)}
              className={cn(
                "w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm",
                active ? "bg-slate-900 text-white" : "hover:bg-slate-100"
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{it.label}</span>
            </button>
          );
        })}
      </nav>
      <Separator />
      <div className="text-xs text-slate-500">v1.0</div>
    </div>
  );
}

function TopBar({ tenant, setTenant }: { tenant: string; setTenant: (v: string) => void }) {
  return (
    <div className="h-16 border-b flex items-center gap-3 px-6 lg:px-8">
      <CompanySwitcher value={tenant} onChange={setTenant} />
      <div className="ml-auto flex items-center gap-2">
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="icon">
          <Settings className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}

export default function AppShell() {
  const [route, setRoute] = useState("inicio");
  const [tenant, setTenant] = useState(TENANTS[0].id);
  return (
    <div className="min-h-screen grid grid-cols-[240px_1fr] bg-white">
      <aside className="border-r">
        <SidebarNav route={route} setRoute={setRoute} />
      </aside>
      <main className="flex flex-col">
        <TopBar tenant={tenant} setTenant={setTenant} />
        {route === "inicio" && <ContentCuratorDashboard key={tenant} tenant={TENANTS.find((t) => t.id === tenant)} />}
        {route === "onboarding" && <OnboardingPage />}
        {route === "dashboard" && <DashboardPage />}
        {route === "config" && <SettingsPage />}
      </main>
    </div>
  );
}
