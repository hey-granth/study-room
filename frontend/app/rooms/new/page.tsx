"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { ArrowLeft, Loader2, Globe, Lock } from "lucide-react"
import { api } from "@/lib/api"
import { ROUTES } from "@/constants"
import type { RoomDetail } from "@/types/api"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

const schema = z.object({
  name: z.string().min(1, "Room name is required").max(100),
  description: z.string().max(500).optional(),
  is_public: z.boolean(),
  max_participants: z.number().min(2).max(100),
})

type FormData = z.infer<typeof schema>

export default function NewRoomPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { is_public: true, max_participants: 20 },
  })

  const isPublic = watch("is_public")

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    setError(null)
    try {
      const res = await api.post<RoomDetail>("/rooms/", data)
      router.push(ROUTES.ROOM(res.data.id))
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      setError(err.response?.data?.detail ?? "Failed to create room")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl animate-in fade-in-50">
      <Button variant="ghost" size="sm" className="mb-6 w-fit" asChild>
        <Link href={ROUTES.ROOMS}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to rooms
        </Link>
      </Button>

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Create Study Room</CardTitle>
            <CardDescription>
              Set up your virtual study space. An invite code will be generated automatically.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="mb-6 rounded-md border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Room Name *</label>
                <input
                  {...register("name")}
                  placeholder="e.g. CS Finals Study Group"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                />
                {errors.name && (
                  <p className="text-sm font-medium text-destructive">{errors.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Description</label>
                <textarea
                  {...register("description")}
                  placeholder="What will you study in this room?"
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors resize-none"
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium leading-none">Max Participants</label>
                <input
                  type="number"
                  {...register("max_participants", { valueAsNumber: true })}
                  min={2}
                  max={100}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                />
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium leading-none">Visibility</label>
                <div className="grid gap-3 sm:grid-cols-2">
                  {[
                    { value: true, icon: Globe, label: "Public", desc: "Anyone can discover and join" },
                    { value: false, icon: Lock, label: "Private", desc: "Invite code required to join" },
                  ].map(({ value, icon: Icon, label, desc }) => (
                    <div
                      key={String(value)}
                      onClick={() => setValue("is_public", value)}
                      className={`flex cursor-pointer flex-col items-start gap-2 rounded-lg border p-4 transition-all hover:bg-muted/50 ${
                        isPublic === value
                          ? "border-primary bg-primary/5 hover:bg-primary/5"
                          : "border-border"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Icon className={`h-4 w-4 ${isPublic === value ? "text-primary" : "text-muted-foreground"}`} />
                        <span className="font-semibold">{label}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">{desc}</span>
                    </div>
                  ))}
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isSubmitting ? "Creating..." : "Create Room"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
