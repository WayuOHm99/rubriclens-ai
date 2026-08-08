import type { ReactNode } from 'react'

import { SiteFooter } from '@/components/SiteFooter'
import { POLICY_LAST_UPDATED_LABEL, SITE_NAME } from '@/lib/site-info'

export const policyLinkClassName = 'text-primary underline underline-offset-2 hover:text-[var(--rl-primary-hover)]'

/** โครงหน้าที่หน้านโยบายทุกหน้าใช้ร่วมกัน เพื่อให้หัว-ท้ายและระยะห่างเหมือนกันทุกหน้า */
export function PolicyPage({ title, summary, children }: { title: string, summary: string, children: ReactNode }) {
  return (
    <>
      <main className="min-h-screen overflow-x-hidden bg-background text-foreground">
        <div className="mx-auto max-w-3xl px-4 py-5 sm:px-6 sm:py-8">
          <header className="mb-6 border-b border-border pb-5">
            <a className={`text-sm font-medium ${policyLinkClassName}`} href="/">← กลับไปหน้าตรวจเอกสาร</a>
            <p className="mt-4 text-sm font-medium text-muted-foreground">{SITE_NAME}</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">{title}</h1>
            <p className="mt-2 text-sm leading-7 text-muted-foreground">{summary}</p>
            <p className="mt-3 text-xs leading-5 text-muted-foreground">ปรับปรุงล่าสุด {POLICY_LAST_UPDATED_LABEL}</p>
          </header>
          <div className="space-y-8 pb-4">{children}</div>
        </div>
      </main>
      <SiteFooter />
    </>
  )
}

/** หัวข้อหนึ่งหัวข้อในหน้านโยบาย */
export function PolicySection({ heading, children }: { heading: string, children: ReactNode }) {
  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold text-foreground">{heading}</h2>
      <div className="space-y-3 text-sm leading-7 text-muted-foreground">{children}</div>
    </section>
  )
}

/** กล่องเน้นข้อความสำคัญที่อยากให้ผู้ใช้อ่านแม้จะไม่อ่านทั้งหน้า */
export function PolicyHighlight({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-lg border border-primary/20 bg-brand-soft p-4 text-sm leading-7 text-brand-soft-foreground">
      {children}
    </div>
  )
}
