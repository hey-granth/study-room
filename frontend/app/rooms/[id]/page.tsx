"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { motion, AnimatePresence } from "framer-motion"
import { useParams } from "next/navigation"
import { useEffect, useRef, useState } from "react"
import { Users, Play, Square, Copy, Check, Send, Crown, Clock, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { api } from "@/lib/api"
import { useWebSocket } from "@/hooks/useWebSocket"
import { useAuthStore } from "@/store/authStore"
import { useRoomStore } from "@/store/roomStore"
import { usePresenceStore } from "@/store/presenceStore"
import { formatDuration, timeAgo } from "@/lib/utils"
import { QUERY_KEYS, ROUTES } from "@/constants"
import type { RoomDetail, StudySession, Page } from "@/types/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"


export default function RoomPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuthStore()
  const { activeSession, setActiveRoom, setActiveSession, clearRoom } = useRoomStore()
  const { participants, clearPresence } = usePresenceStore()
  const queryClient = useQueryClient()

  const [copied, setCopied] = useState(false)
  const [chatInput, setChatInput] = useState("")
  const chatBottomRef = useRef<HTMLDivElement>(null)

  const { isConnected, sendMessage, chatMessages, connectionState } = useWebSocket(id)

  const { data: room } = useQuery({
    queryKey: QUERY_KEYS.ROOM(id),
    queryFn: async () => {
      const res = await api.get<RoomDetail>(`/rooms/${id}`)
      return res.data
    },
  })

  const { data: fetchedSession } = useQuery({
    queryKey: QUERY_KEYS.ACTIVE_SESSION(id),
    queryFn: async () => {
      const res = await api.get<StudySession | null>(`/sessions/rooms/${id}/active`)
      return res.data
    },
  })

  const { data: history } = useQuery({
    queryKey: QUERY_KEYS.SESSION_HISTORY(id),
    queryFn: async () => {
      const res = await api.get<Page<StudySession>>(`/sessions/rooms/${id}/history`)
      return res.data
    },
  })

  useEffect(() => {
    if (room) setActiveRoom(room)
    return () => {
      clearRoom()
      clearPresence()
    }
  }, [room, setActiveRoom, clearRoom, clearPresence])

  useEffect(() => {
    if (fetchedSession !== undefined) setActiveSession(fetchedSession)
  }, [fetchedSession, setActiveSession])

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chatMessages])

  const startSession = useMutation({
    mutationFn: () => api.post<StudySession>(`/sessions/rooms/${id}/start`),
    onSuccess: (res) => {
      setActiveSession(res.data)
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.ACTIVE_SESSION(id) })
    },
  })

  const endSession = useMutation({
    mutationFn: () => api.post<StudySession>(`/sessions/rooms/${id}/end`),
    onSuccess: () => {
      setActiveSession(null)
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.ACTIVE_SESSION(id) })
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.SESSION_HISTORY(id) })
    },
  })

  const copyInviteCode = async () => {
    if (room?.invite_code) {
      await navigator.clipboard.writeText(room.invite_code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleSendMessage = () => {
    const content = chatInput.trim()
    if (!content) return
    sendMessage({ type: "chat_message", payload: { content } })
    setChatInput("")
  }

  const isMember = room?.members.some((m) => m.id === user?.id)
  const isOwner = room?.owner_id === user?.id

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-4rem)] -m-8 p-8 overflow-hidden animate-in fade-in-50">
      {/* Left: Participants */}
      <div className="w-full lg:w-64 flex-shrink-0 flex flex-col gap-4">
        <Button variant="ghost" size="sm" className="w-fit" asChild>
          <Link href={ROUTES.ROOMS}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Rooms
          </Link>
        </Button>

        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Users className="h-4 w-4" />
              Online ({participants.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto p-0 px-4 pb-4">
            <div className="space-y-2">
              {participants.length === 0 ? (
                <p className="text-xs text-center py-4 text-muted-foreground">
                  {isConnected ? "No one else here yet" : "Connecting..."}
                </p>
              ) : (
                participants.map((p) => (
                  <div
                    key={p.user_id}
                    className="flex items-center gap-2 rounded-md border border-transparent p-2 hover:bg-muted/50 transition-colors"
                  >
                    <div className="relative">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                        {p.display_name[0].toUpperCase()}
                      </div>
                      <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-background bg-green-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate flex items-center gap-1.5">
                        {p.display_name}
                        {room?.owner_id === p.user_id && (
                          <Crown className="h-3 w-3 text-amber-500" />
                        )}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Invite code */}
            {room && (
              <div className="mt-6 pt-4 border-t">
                <p className="text-xs text-muted-foreground mb-2 font-medium">Invite Code</p>
                <button
                  onClick={copyInviteCode}
                  className="flex w-full items-center justify-between rounded-md border border-input bg-muted/30 px-3 py-2 text-sm font-mono transition-colors hover:bg-muted"
                >
                  <span className="truncate">{room.invite_code}</span>
                  {copied ? (
                    <Check className="h-4 w-4 text-green-500 ml-2 shrink-0" />
                  ) : (
                    <Copy className="h-4 w-4 text-muted-foreground ml-2 shrink-0" />
                  )}
                </button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Center: Session */}
      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">{room?.name ?? "Loading..."}</CardTitle>
            {room?.description && <CardDescription>{room.description}</CardDescription>}
          </CardHeader>
          <CardContent className="flex flex-col sm:flex-row items-center gap-6">
            <div className="flex-1 text-center sm:text-left">
              <SessionTimer session={activeSession} />
            </div>

            {isMember && (
              <div className="shrink-0 w-full sm:w-auto">
                {activeSession ? (
                  <Button
                    variant="destructive"
                    size="lg"
                    className="w-full sm:w-auto font-semibold"
                    onClick={() => endSession.mutate()}
                    disabled={endSession.isPending}
                  >
                    <Square className="mr-2 h-4 w-4" /> End Session
                  </Button>
                ) : (
                  <Button
                    size="lg"
                    className="w-full sm:w-auto font-semibold"
                    onClick={() => startSession.mutate()}
                    disabled={startSession.isPending}
                  >
                    <Play className="mr-2 h-4 w-4" /> Start Session
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Session History */}
        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Session History</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            <div className="space-y-2">
              {history?.items.filter((s) => !s.is_active).map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between rounded-md border p-3 hover:bg-muted/30 transition-colors"
                >
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span className="text-sm">
                      {new Date(s.started_at).toLocaleDateString(undefined, {
                        weekday: "short",
                        month: "short",
                        day: "numeric",
                        hour: "numeric",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  <span className="font-mono text-sm font-semibold">
                    {formatDuration(s.duration_seconds ?? 0)}
                  </span>
                </div>
              )) ?? (
                <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                  <Clock className="h-8 w-8 mb-2 opacity-20" />
                  <p className="text-sm">No sessions yet</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right: Chat */}
      <Card className="w-full lg:w-80 flex-shrink-0 flex flex-col overflow-hidden">
        <CardHeader className="border-b py-3 px-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold">Room Chat</CardTitle>
            <div className="flex items-center gap-1.5">
              <div
                className={`h-2 w-2 rounded-full ${
                  isConnected ? "bg-green-500" : "bg-muted-foreground"
                }`}
              />
              <span className="text-xs text-muted-foreground capitalize">
                {connectionState}
              </span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence initial={false}>
            {chatMessages.map((msg, i) => {
              if (msg.type !== "chat_message_broadcast") return null
              const isMe = msg.payload.user_id === user?.id
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex flex-col ${isMe ? "items-end" : "items-start"}`}
                >
                  {!isMe && (
                    <span className="text-xs mb-1 ml-1 text-muted-foreground">
                      {msg.payload.display_name}
                    </span>
                  )}
                  <div
                    className={`px-3 py-2 rounded-2xl text-sm max-w-[85%] break-words ${
                      isMe
                        ? "bg-primary text-primary-foreground rounded-br-sm"
                        : "bg-muted text-foreground rounded-bl-sm"
                    }`}
                  >
                    {msg.payload.content}
                  </div>
                  <span className="text-[10px] mt-1 mx-1 text-muted-foreground">
                    {timeAgo(msg.payload.sent_at)}
                  </span>
                </motion.div>
              )
            })}
          </AnimatePresence>
          <div ref={chatBottomRef} />
        </CardContent>

        <div className="p-3 border-t bg-background">
          <div className="flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSendMessage()}
              placeholder="Message room..."
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!isConnected}
            />
            <Button
              size="icon"
              className="h-9 w-9 shrink-0"
              onClick={handleSendMessage}
              disabled={!isConnected || !chatInput.trim()}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

function SessionTimer({ session }: { session: StudySession | null }) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    if (!session?.is_active) {
      setElapsed(0)
      return
    }
    const start = new Date(session.started_at).getTime()
    const tick = () => setElapsed(Math.floor((Date.now() - start) / 1000))
    tick()
    const interval = setInterval(tick, 1000)
    return () => clearInterval(interval)
  }, [session])

  if (!session?.is_active) {
    return (
      <div>
        <p className="font-mono text-4xl sm:text-5xl font-bold tracking-tight text-muted-foreground/50">
          —:—:—
        </p>
        <p className="mt-2 text-sm text-muted-foreground">No active session</p>
      </div>
    )
  }

  return (
    <div>
      <p className="font-mono text-4xl sm:text-5xl font-bold tracking-tight text-primary">
        {formatDuration(elapsed)}
      </p>
      <p className="mt-2 text-sm font-medium text-muted-foreground flex items-center justify-center sm:justify-start gap-2">
        <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
        Session in progress
      </p>
    </div>
  )
}
