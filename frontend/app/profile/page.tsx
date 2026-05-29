"use client"

import { useQuery } from "@tanstack/react-query"
import { motion } from "framer-motion"
import { Timer, TrendingUp, Calendar, Award } from "lucide-react"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { formatDurationShort } from "@/lib/utils"
import { QUERY_KEYS } from "@/constants"
import type { UserSessionStats } from "@/types/api"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function ProfilePage() {
  const { user } = useAuthStore()

  const { data: stats } = useQuery({
    queryKey: [QUERY_KEYS.USER_STATS],
    queryFn: async () => {
      const res = await api.get<UserSessionStats>("/sessions/me/stats")
      return res.data
    },
  })

  const achievements = [
    {
      icon: "🔥",
      title: "First Session",
      desc: "Completed your first study session",
      unlocked: (stats?.total_sessions ?? 0) >= 1,
    },
    {
      icon: "⏰",
      title: "Hour Scholar",
      desc: "Studied for a total of 1 hour",
      unlocked: (stats?.total_study_seconds ?? 0) >= 3600,
    },
    {
      icon: "📚",
      title: "Consistent",
      desc: "Studied 3 days in a row",
      unlocked: (stats?.sessions_this_week ?? 0) >= 3,
    },
    {
      icon: "🏆",
      title: "Deep Focus",
      desc: "Completed a 2-hour session",
      unlocked: (stats?.longest_session_seconds ?? 0) >= 7200,
    },
  ]

  return (
    <div className="space-y-8 animate-in fade-in-50">
      <PageHeader title="Profile" description="View your progress and achievements." />

      <Card className="flex flex-col sm:flex-row items-center gap-6 p-6">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-primary text-3xl font-bold text-primary-foreground">
          {user?.display_name?.[0]?.toUpperCase() ?? "U"}
        </div>
        <div className="text-center sm:text-left">
          <h2 className="text-2xl font-bold tracking-tight">{user?.display_name}</h2>
          <p className="text-muted-foreground">@{user?.username}</p>
          <p className="mt-1 text-sm text-muted-foreground">{user?.email}</p>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[
          {
            icon: Timer,
            label: "Total Study Time",
            value: formatDurationShort(stats?.total_study_seconds ?? 0),
          },
          {
            icon: TrendingUp,
            label: "Avg Session",
            value: formatDurationShort(stats?.average_session_seconds ?? 0),
          },
          { icon: Calendar, label: "Total Sessions", value: stats?.total_sessions ?? 0 },
          {
            icon: Award,
            label: "Best Session",
            value: formatDurationShort(stats?.longest_session_seconds ?? 0),
          },
        ].map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{s.label}</CardTitle>
                <s.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{s.value}</div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Achievements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            {achievements.map((a) => (
              <div
                key={a.title}
                className={`flex items-start gap-4 rounded-lg border p-4 transition-all ${
                  a.unlocked ? "border-border bg-muted/30" : "border-border/50 opacity-50 grayscale"
                }`}
              >
                <span className="text-3xl">{a.icon}</span>
                <div>
                  <p className="font-semibold">{a.title}</p>
                  <p className="text-sm text-muted-foreground">{a.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
