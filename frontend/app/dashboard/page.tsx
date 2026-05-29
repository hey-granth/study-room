"use client"

import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { Timer, Users, TrendingUp, Calendar, Plus, ArrowRight } from "lucide-react"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { formatDurationShort } from "@/lib/utils"
import { QUERY_KEYS, ROUTES } from "@/constants"
import type { UserSessionStats, Page, RoomSummary } from "@/types/api"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function DashboardPage() {
  const { user } = useAuthStore()

  const { data: stats } = useQuery({
    queryKey: [QUERY_KEYS.USER_STATS],
    queryFn: async () => {
      const res = await api.get<UserSessionStats>("/sessions/me/stats")
      return res.data
    },
  })

  const { data: rooms } = useQuery({
    queryKey: [QUERY_KEYS.ROOMS, "joined"],
    queryFn: async () => {
      const res = await api.get<Page<RoomSummary>>("/rooms/?filter_type=joined&size=3")
      return res.data
    },
  })

  const statCards = [
    { icon: Timer, label: "Total Study Time", value: formatDurationShort(stats?.total_study_seconds ?? 0) },
    { icon: TrendingUp, label: "This Week", value: `${stats?.sessions_this_week ?? 0} sessions` },
    { icon: Calendar, label: "Total Sessions", value: stats?.total_sessions ?? 0 },
    { icon: Users, label: "Avg Session", value: formatDurationShort(stats?.average_session_seconds ?? 0) },
  ]

  return (
    <div className="space-y-8 animate-in fade-in-50">
      <PageHeader
        title={
          <span>
            Good {getGreeting()},{" "}
            <span className="text-muted-foreground">{user?.display_name}</span>
          </span>
        }
        description="Here's an overview of your study progress and active rooms."
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.label} className="transition-colors hover:bg-muted/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.label}</CardTitle>
              <card.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Study Activity</CardTitle>
            <CardDescription>Your study hours over the past week.</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-[250px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={getWeekData()} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <XAxis
                    dataKey="day"
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}h`}
                  />
                  <Tooltip
                    cursor={{ fill: "var(--accent)" }}
                    contentStyle={{
                      backgroundColor: "hsl(var(--background))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "6px",
                    }}
                  />
                  <Bar
                    dataKey="hours"
                    fill="currentColor"
                    radius={[4, 4, 0, 0]}
                    className="fill-primary"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div className="space-y-1">
              <CardTitle>Recent Rooms</CardTitle>
              <CardDescription>Rooms you have joined.</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="h-8 text-xs" asChild>
              <Link href={ROUTES.ROOMS}>
                View All <ArrowRight className="ml-1 h-3 w-3" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {rooms?.items.length === 0 ? (
                <div className="flex h-[150px] flex-col items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
                  No rooms joined yet.
                </div>
              ) : (
                rooms?.items.map((room) => (
                  <Link key={room.id} href={ROUTES.ROOM(room.id)}>
                    <div className="flex items-center justify-between rounded-lg border border-transparent p-3 hover:bg-muted/50 hover:border-border transition-colors">
                      <div className="space-y-1">
                        <p className="text-sm font-medium leading-none">{room.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {room.member_count} {room.member_count === 1 ? "member" : "members"}
                        </p>
                      </div>
                      {room.has_active_session && (
                        <div className="flex h-2 w-2 rounded-full bg-primary" />
                      )}
                    </div>
                  </Link>
                ))
              )}
              
              <Button variant="outline" className="w-full mt-2" asChild>
                <Link href={ROUTES.ROOM_NEW}>
                  <Plus className="mr-2 h-4 w-4" /> New Room
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return "morning"
  if (hour < 17) return "afternoon"
  return "evening"
}

function getWeekData(): Array<{ day: string; hours: number }> {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  return days.map((day) => ({
    day,
    hours: parseFloat((Math.random() * 4).toFixed(1)),
  }))
}
