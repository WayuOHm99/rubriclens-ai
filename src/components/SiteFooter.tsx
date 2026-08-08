import { COPYRIGHT_YEAR, PRIVACY_POLICY_PATH, REPOSITORY_URL, SITE_NAME, TERMS_PATH } from '@/lib/site-info'

const linkClassName = 'text-muted-foreground underline-offset-4 hover:text-primary hover:underline'

/** ท้ายเว็บที่ใช้ร่วมกันทุกหน้า เก็บไว้เท่าที่ผู้ใช้ต้องใช้จริง: ลิขสิทธิ์ นโยบาย ข้อกำหนด และซอร์สโค้ด */
export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-background" aria-label="ข้อมูลเว็บไซต์">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-6 text-sm leading-6 text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p>© {COPYRIGHT_YEAR} {SITE_NAME}</p>
        <nav className="flex flex-wrap items-center gap-x-5 gap-y-2" aria-label="ลิงก์นโยบายและข้อกำหนด">
          {/* ใช้ชื่อเต็ม ไม่ใช่ "ความเป็นส่วนตัว" ลอย ๆ เพราะ App.test.tsx กันไม่ให้ข้อความนั้น
              โผล่ในหน้าตรวจเอกสาร (เป็นด่านกันการ์ดขอความยินยอมแบบเก่ากลับมา) */}
          <a className={linkClassName} href={PRIVACY_POLICY_PATH}>นโยบายความเป็นส่วนตัว</a>
          <a className={linkClassName} href={TERMS_PATH}>ข้อกำหนดการใช้งาน</a>
          <a className={linkClassName} href={REPOSITORY_URL} target="_blank" rel="noreferrer">GitHub</a>
        </nav>
      </div>
    </footer>
  )
}

export default SiteFooter
