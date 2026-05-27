'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { BookOpen, Users, Timer, Zap, ArrowRight, Star, TrendingUp, MessageSquare } from 'lucide-react';
import { ROUTES } from '@/constants';

const features = [
  {
    icon: Timer,
    title: 'Live Session Timers',
    desc: 'Start group study sessions with a live countdown everyone in the room can see in real time.',
  },
  {
    icon: MessageSquare,
    title: 'Built-in Room Chat',
    desc: 'Communicate with your study partners without leaving the platform. System events keep everyone informed.',
  },
  {
    icon: Users,
    title: 'Presence Indicators',
    desc: 'See exactly who is in the room right now with live online indicators and participant lists.',
  },
  {
    icon: TrendingUp,
    title: 'Progress Analytics',
    desc: 'Track your weekly study hours, session streaks, and personal bests with beautiful charts.',
  },
];

const steps = [
  { step: '01', title: 'Create a Room', desc: 'Set up your virtual study space in seconds. Choose public or private with custom invite codes.' },
  { step: '02', title: 'Invite Friends', desc: 'Share your unique invite code. Your study group joins instantly — no sign-up friction.' },
  { step: '03', title: 'Focus Together', desc: 'Start a session, watch the timer, chat, and build a consistent study habit as a team.' },
];

export default function HomePage() {
  return (
    <main className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      {/* ── Navbar ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4"
        style={{ background: 'rgba(10,14,26,0.8)', backdropFilter: 'blur(20px)', borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="flex items-center gap-2">
          <BookOpen size={22} style={{ color: 'var(--accent-primary)' }} />
          <span className="font-display text-xl font-bold" style={{ color: 'var(--text-primary)' }}>StudyRoom</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          {['Features', 'How It Works'].map((item) => (
            <a key={item} href={`#${item.toLowerCase().replace(' ', '-')}`}
              className="text-sm transition-colors"
              style={{ color: 'var(--text-secondary)' }}
              onMouseEnter={e => (e.currentTarget.style.color = 'var(--text-primary)')}
              onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-secondary)')}
            >{item}</a>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <Link href={ROUTES.LOGIN}>
            <button className="btn-ghost text-sm">Log in</button>
          </Link>
          <Link href={ROUTES.REGISTER}>
            <button className="btn-primary text-sm">Get Started</button>
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative pt-32 pb-24 px-8 text-center overflow-hidden bg-grid">
        {/* Radial glow */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[600px] h-[600px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(79,255,218,0.06) 0%, transparent 70%)' }} />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className="relative max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full text-sm"
            style={{ background: 'rgba(79,255,218,0.08)', border: '1px solid var(--border-accent)', color: 'var(--accent-primary)' }}>
            <Star size={13} />
            <span>Real-time Collaborative Study</span>
          </div>

          <h1 className="font-display text-6xl md:text-7xl font-bold mb-6 leading-tight">
            <span style={{ color: 'var(--text-primary)' }}>Focus Together.</span>
            <br />
            <span className="gradient-text text-glow">Achieve More.</span>
          </h1>

          <p className="text-xl mb-10 max-w-2xl mx-auto" style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
            Create virtual study rooms, track sessions with live timers, chat with study partners,
            and build consistent habits — all in one beautifully focused space.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href={ROUTES.REGISTER}>
              <motion.button
                className="btn-primary flex items-center gap-2 text-base px-8 py-4"
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
              >
                Start Studying Free <ArrowRight size={18} />
              </motion.button>
            </Link>
            <Link href={ROUTES.ROOMS}>
              <button className="btn-ghost flex items-center gap-2 text-base px-8 py-4">
                Browse Rooms
              </button>
            </Link>
          </div>
        </motion.div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="flex items-center justify-center gap-12 mt-20"
        >
          {[['10K+', 'Study Hours'], ['2K+', 'Active Rooms'], ['98%', 'Satisfaction']].map(([val, label]) => (
            <div key={label} className="text-center">
              <p className="font-display text-3xl font-bold gradient-text">{val}</p>
              <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
            </div>
          ))}
        </motion.div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="py-24 px-8 max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="font-display text-4xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
            Everything you need to <span className="gradient-text">stay focused</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Built for serious students who want accountability and community.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              whileHover={{ y: -4 }}
              className="glass-card p-6 cursor-default"
            >
              <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4"
                style={{ background: 'rgba(79,255,218,0.1)' }}>
                <f.icon size={20} style={{ color: 'var(--accent-primary)' }} />
              </div>
              <h3 className="font-display font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>{f.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how-it-works" className="py-24 px-8" style={{ background: 'var(--bg-secondary)' }}>
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display text-4xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
              Up and running in <span className="gradient-text">3 steps</span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((s, i) => (
              <motion.div
                key={s.step}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="relative"
              >
                <div className="text-6xl font-display font-bold mb-4"
                  style={{ color: 'rgba(79,255,218,0.12)', WebkitTextStroke: '1px rgba(79,255,218,0.2)' }}>
                  {s.step}
                </div>
                <h3 className="font-display font-bold text-xl mb-2" style={{ color: 'var(--text-primary)' }}>{s.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24 px-8 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-2xl mx-auto glass-card-elevated p-16 glow-accent"
        >
          <Zap size={36} style={{ color: 'var(--accent-primary)' }} className="mx-auto mb-6" />
          <h2 className="font-display text-4xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
            Ready to focus?
          </h2>
          <p className="mb-8" style={{ color: 'var(--text-secondary)' }}>
            Join thousands of students already using StudyRoom to build better habits.
          </p>
          <Link href={ROUTES.REGISTER}>
            <motion.button
              className="btn-primary text-base px-10 py-4"
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.97 }}
            >
              Create Your Free Room
            </motion.button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-8 text-center" style={{ borderTop: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
        <p className="text-sm">© 2025 StudyRoom. Built with ❤️ for learners everywhere.</p>
      </footer>
    </main>
  );
}
