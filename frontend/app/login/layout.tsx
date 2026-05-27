import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign In — StudyRoom',
  description: 'Sign in to your StudyRoom account.',
};

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="min-h-screen flex items-center justify-center bg-grid"
      style={{ background: 'var(--bg-primary)' }}
    >
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div
          className="w-[500px] h-[500px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(79,255,218,0.05) 0%, transparent 70%)' }}
        />
      </div>
      <div className="relative w-full max-w-md px-6">{children}</div>
    </div>
  );
}
