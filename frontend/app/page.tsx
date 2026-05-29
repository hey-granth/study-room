"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { BookOpen, Users, Timer, ArrowRight, BarChart, MessageSquare } from "lucide-react"
import { ROUTES } from "@/constants"
import { Navbar } from "@/components/layout/navbar"
import { SectionContainer } from "@/components/layout/section-container"
import { PageContainer } from "@/components/layout/page-container"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const features = [
  {
    icon: Timer,
    title: "Live Session Timers",
    desc: "Start group study sessions with a live countdown everyone in the room can see in real time.",
  },
  {
    icon: MessageSquare,
    title: "Built-in Room Chat",
    desc: "Communicate with your study partners seamlessly. System events keep everyone informed.",
  },
  {
    icon: Users,
    title: "Presence Indicators",
    desc: "See exactly who is in the room right now with live online indicators and participant lists.",
  },
  {
    icon: BarChart,
    title: "Progress Analytics",
    desc: "Track your weekly study hours, session streaks, and personal bests with clean analytics.",
  },
]

export default function HomePage() {
  return (
    <div className="relative flex min-h-screen flex-col bg-background selection:bg-primary/10 selection:text-primary">
      <Navbar />

      <main className="flex-1">
        {/* Hero Section */}
        <SectionContainer className="relative overflow-hidden pt-24 md:pt-32 lg:pt-40 bg-grid">
          <div className="absolute inset-0 bg-background/90" />
          <PageContainer className="relative z-10 flex flex-col items-center text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="flex flex-col items-center"
            >
              <div className="mb-6 inline-flex items-center rounded-full border border-border bg-muted/50 px-3 py-1 text-sm font-medium">
                <span className="flex h-2 w-2 rounded-full bg-zinc-400 mr-2" />
                Collaborative study platform
              </div>

              <h1 className="max-w-4xl text-5xl font-semibold tracking-tight sm:text-6xl md:text-7xl">
                Focus Together. <br className="hidden sm:inline" />
                <span className="text-muted-foreground">Achieve More.</span>
              </h1>

              <p className="mt-6 max-w-2xl text-lg text-muted-foreground">
                Create virtual study rooms, track sessions with live timers, chat with study partners,
                and build consistent habits — all in one beautifully focused space.
              </p>

              <div className="mt-10 flex flex-col sm:flex-row gap-4">
                <Button size="lg" asChild>
                  <Link href={ROUTES.REGISTER}>
                    Start Studying Free
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link href={ROUTES.ROOMS}>Browse Public Rooms</Link>
                </Button>
              </div>
            </motion.div>
          </PageContainer>
        </SectionContainer>

        {/* Stats Section */}
        <SectionContainer className="border-t border-border bg-muted/20 py-12">
          <PageContainer>
            <div className="grid grid-cols-2 gap-8 md:grid-cols-4 text-center">
              {[
                { value: "10K+", label: "Study Hours" },
                { value: "2K+", label: "Active Rooms" },
                { value: "98%", label: "Satisfaction" },
                { value: "24/7", label: "Availability" },
              ].map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1, duration: 0.5 }}
                >
                  <div className="text-3xl font-semibold tracking-tight">{stat.value}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </PageContainer>
        </SectionContainer>

        {/* Features Section */}
        <SectionContainer>
          <PageContainer>
            <div className="mb-16 md:text-center">
              <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                Everything you need to stay focused
              </h2>
              <p className="mt-4 text-lg text-muted-foreground md:max-w-2xl md:mx-auto">
                Built for serious students who want accountability and community. No distractions, just features that help you study.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              {features.map((feature, i) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1, duration: 0.5 }}
                >
                  <Card className="h-full transition-colors hover:bg-muted/50">
                    <CardHeader>
                      <feature.icon className="h-6 w-6 text-foreground mb-4" />
                      <CardTitle>{feature.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-base">{feature.desc}</CardDescription>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </PageContainer>
        </SectionContainer>

        {/* CTA Section */}
        <SectionContainer className="border-t border-border">
          <PageContainer>
            <div className="flex flex-col items-center rounded-2xl border border-border bg-muted/20 px-6 py-16 text-center sm:px-12 md:py-24">
              <BookOpen className="mb-6 h-10 w-10 text-muted-foreground" />
              <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                Ready to transform your study habits?
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
                Join thousands of students already using StudyRoom to build better habits and achieve their goals.
              </p>
              <div className="mt-8">
                <Button size="lg" asChild>
                  <Link href={ROUTES.REGISTER}>Create Your Free Room</Link>
                </Button>
              </div>
            </div>
          </PageContainer>
        </SectionContainer>
      </main>

      <footer className="border-t border-border py-8 md:py-12">
        <PageContainer className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            <span className="text-sm font-semibold tracking-tight">StudyRoom</span>
          </div>
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} StudyRoom. Built for focused learners.
          </p>
        </PageContainer>
      </footer>
    </div>
  )
}
