"use client"

import { useQuery } from "@tanstack/react-query"
import { motion } from "framer-motion"
import Link from "next/link"
import { useState } from "react"
import { Plus, Search, Users, Globe, Lock, SearchX } from "lucide-react"
import { api } from "@/lib/api"
import { QUERY_KEYS, ROUTES } from "@/constants"
import type { Page, RoomSummary } from "@/types/api"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import { LoadingState } from "@/components/ui/loading-state"

type FilterType = "all" | "owned" | "joined"

export default function RoomsPage() {
  const [search, setSearch] = useState("")
  const [filter, setFilter] = useState<FilterType>("all")

  const { data, isLoading } = useQuery({
    queryKey: [QUERY_KEYS.ROOMS, filter, search],
    queryFn: async () => {
      const params = new URLSearchParams({ filter_type: filter, size: "30" })
      if (search) params.set("search", search)
      const res = await api.get<Page<RoomSummary>>(`/rooms/?${params}`)
      return res.data
    },
    staleTime: 30_000,
  })

  return (
    <div className="mx-auto w-full max-w-7xl px-6 py-8 md:py-10 space-y-8 animate-in fade-in-50">
      <PageHeader
        title="Study Rooms"
        description={`${data?.total ?? 0} rooms available to join or browse.`}
        actions={
          <Button asChild>
            <Link href={ROUTES.ROOM_NEW}>
              <Plus className="mr-2 h-4 w-4" />
              New Room
            </Link>
          </Button>
        }
      />

      {/* Toolbar Section */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-border bg-card p-4 shadow-sm">
        <div className="relative flex-1 min-w-[240px] max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search rooms..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 pl-9 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
          />
        </div>
        <div className="flex w-full sm:w-auto rounded-md border border-input p-1 bg-muted/20">
          {(["all", "joined", "owned"] as FilterType[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`flex-1 sm:flex-none rounded-sm px-4 py-1.5 text-sm font-medium capitalize transition-all ${
                filter === f
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Rooms grid */}
      <div className="min-h-[400px]">
        {isLoading ? (
          <div className="flex h-[400px] items-center justify-center rounded-xl border border-dashed border-border/60 bg-muted/5">
            <LoadingState text="Loading study rooms..." />
          </div>
        ) : data?.items.length === 0 ? (
          <div className="flex h-[400px] flex-col items-center justify-center rounded-xl border border-dashed border-border/60 bg-muted/5 p-8 text-center">
            <EmptyState
              icon={<SearchX className="h-10 w-10" />}
              title="No rooms found"
              description={
                search
                  ? "We couldn't find any rooms matching your search."
                  : "There are no rooms available for this filter."
              }
              action={
                <Button variant="outline" className="mt-4" asChild>
                  <Link href={ROUTES.ROOM_NEW}>Create the first one</Link>
                </Button>
              }
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
            {data?.items.map((room, i) => (
              <motion.div
                key={room.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Link href={ROUTES.ROOM(room.id)}>
                  <Card className="h-full flex flex-col transition-colors hover:bg-muted/50 hover:border-border cursor-pointer shadow-sm">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-4">
                        <CardTitle className="line-clamp-1 text-base">{room.name}</CardTitle>
                        {room.has_active_session && (
                          <span className="flex shrink-0 items-center gap-1.5 rounded-full border border-primary/20 bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
                            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                            Live
                          </span>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="flex-1 pb-6">
                      <CardDescription className="line-clamp-2 leading-relaxed">
                        {room.description || "No description provided."}
                      </CardDescription>
                    </CardContent>
                    <CardFooter className="pt-0 text-muted-foreground border-t border-border/50 bg-muted/10 px-6 py-3 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5">
                        <Users className="h-3.5 w-3.5" />
                        {room.member_count} / {room.max_participants}
                      </div>
                      <div className="flex items-center gap-1.5">
                        {room.is_public ? (
                          <>
                            <Globe className="h-3.5 w-3.5" /> Public
                          </>
                        ) : (
                          <>
                            <Lock className="h-3.5 w-3.5" /> Private
                          </>
                        )}
                      </div>
                    </CardFooter>
                  </Card>
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
