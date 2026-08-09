# Architecture notes

เอกสารนี้สรุปการตัดสินใจทางเทคนิคที่สำคัญของ RubricLensAi สำหรับใช้ประกอบ portfolio หรือ technical interview

## Components

### Shared contract (`shared/`)

- `shared/api-contract.ts` เก็บ `API_VERSION`, รายการเวอร์ชันที่ client รองรับ และค่า `applicability` ที่ใช้ร่วมกันทั้งสองฝั่ง
- `shared/scoring.ts` เก็บสูตรคะแนนถ่วงน้ำหนักเพียงชุดเดียว ใช้ทั้งใน Worker และใน mock ของ browser จึงไม่มีสูตรซ้ำที่หลุดจากกัน
- `shared/document-types.ts` เก็บนิยามประเภทเอกสาร รวมถึงคำอธิบายว่าเมื่อใดหัวข้อจึงถือว่า “ไม่เกี่ยวข้อง” ตามธรรมชาติของงานแต่ละแบบ

### Frontend (`src/`)

- `App.tsx` เป็น workflow หลัก: input, PDF preview, rubric editor, analysis progress และ result review
- `src/components/ui/` เก็บชิ้นส่วน UI แบบ shadcn (alert, badge, button, card, input, progress, textarea) และ `src/lib/utils.ts` เก็บ `cn` ที่ชิ้นส่วนเหล่านี้ใช้ ทั้งคู่ถูกเรียกผ่านชื่อย่อ `@/` ซึ่ง `tsconfig.app.json` และ `vite.config.ts` ชี้ไปที่ `src/`
- `src/lib/document.ts` เตรียม main text, แยก appendix และประกาศขีดจำกัดไฟล์ทั้งขนาด (10 MB) และจำนวนหน้า (400 หน้า) ไว้ที่เดียวกัน
- `src/lib/pdf.ts` extract text layer พร้อม progress, abort และ warning สำหรับ scanned/multi-column PDF ตรวจจำนวนหน้าทันทีหลังเปิดไฟล์ และหยุดระหว่าง extraction เมื่อเกิน 300,000 ตัวอักษรหรือ text items; การจัดกลุ่มบรรทัดใช้ y-bucket เพื่อไม่ให้จำนวน comparison โตแบบกำลังสอง
- `src/lib/references.ts` ตรวจ citation/reference ด้วยกฎ deterministic ก่อนส่ง summary ให้ AI
- `src/lib/rubric.ts` เก็บ templates, schema และ validation ของหัวข้อ/น้ำหนัก
- `src/lib/analysis.ts` เก็บ response schema, การตรวจ `apiVersion`, mock result และการ format ผลตรวจ
- `src/lib/analysis-failure.ts` แปลงความล้มเหลวจาก Worker, browser และการตรวจ contract ให้เป็นหมวดที่มีความหมาย (`validation`, `quota`, `compatibility`, `conflict`, `network`, `service`, `unexpected`) แล้วแปลงต่อเป็นนโยบายลองใหม่แบบชัดเจน (`immediate`, `delayed`, `none`) แทนการใช้ `retryable` เพียงค่าเดียวควบคุมทุกปุ่ม
- `src/lib/site-info.ts` เก็บชื่อเว็บ อีเมลติดต่อ ช่องทางสำรอง ลิขสิทธิ์ สัญญาอนุญาต และ path ของหน้ากฎหมาย ไว้ที่เดียว
- `src/lib/browser-storage.ts` เก็บ **ชื่อคีย์ทั้งหมดที่ระบบเขียนลงเครื่องผู้ใช้** พร้อมคำอธิบายว่าเก็บไปทำไมและอยู่นานเท่าไร ทั้ง `App.tsx` และหัวข้อคุกกี้ในหน้านโยบายอ่านจากไฟล์นี้ไฟล์เดียว คีย์ชื่อเดิมก่อนเปลี่ยนแบรนด์ถูกทำเครื่องหมาย `isLegacy` เพื่อให้ตารางในนโยบายแสดงเฉพาะของที่ใช้จริง
- `src/components/SiteFooter.tsx` เป็นท้ายเว็บร่วมของทุกหน้า เหลือเฉพาะลิขสิทธิ์แบรนด์และลิงก์สามทาง (นโยบาย, ข้อกำหนด, ซอร์สโค้ด)
- `src/index.css` เป็นสะพานระหว่าง token แบรนด์ชื่อ `--rl-*` กับ token เชิงความหมายของ shadcn/Tailwind เช่น `--primary`, `--background` และ `--muted` ทำให้ชิ้นส่วน UI ใช้สีแบรนด์โดยไม่ผูกกับชื่อสีเฉพาะ
- `src/assets/brand/` เก็บ SVG มาสคอตที่ Vite นำเข้าและตั้งชื่อไฟล์ตาม hash ตอน build ไฟล์เหล่านี้เป็น **สำเนาที่สร้างอัตโนมัติ** จาก `docs/brand/logo/build-mascots.py` ไม่ใช่แหล่งต้นฉบับสำหรับแก้ด้วยมือ

### Static pages (`src/pages/`)

เว็บนี้ build เป็น **multi-page** สามหน้า ไม่ใช่ SPA หน้าเดียวอีกต่อไป โดย `vite.config.ts` ประกาศ entry ไว้สามจุด

| URL | ไฟล์ entry | เนื้อหา |
| --- | --- | --- |
| `/` | `index.html` → `src/main.tsx` | หน้าตรวจเอกสาร (`App.tsx`) |
| `/privacy` | `privacy.html` → `src/pages/privacy-main.tsx` | `src/pages/PrivacyPolicy.tsx` (รวมหัวข้อคุกกี้ไว้ในหน้านี้) |
| `/terms` | `terms.html` → `src/pages/terms-main.tsx` | `src/pages/TermsOfService.tsx` |

`src/pages/PolicyPage.tsx` เป็นโครงหน้าและกล่องหัวข้อที่หน้ากฎหมายทั้งสองใช้ร่วมกัน ทั้ง Vite dev server, `vite preview` และ Cloudflare Pages ต่างเสิร์ฟ `/privacy` จาก `privacy.html` ให้เอง จึงไม่ต้องตั้ง redirect เพิ่ม

**ไม่มีหน้า `/cookies` แยกโดยตั้งใจ** เพราะระบบไม่ได้ตั้งคุกกี้เลย การเปิดเผยเรื่องที่เก็บข้อมูลในเบราว์เซอร์จึงอยู่เป็นหัวข้อที่ 7 ของนโยบายความเป็นส่วนตัว

`public/404.html` เป็น HTML ล้วนที่ไม่ผูกกับ React หรือ CSS ของแอป Cloudflare Pages หยิบไปเสิร์ฟเองเมื่อไม่พบเส้นทาง จึงยังแสดงผลได้แม้ bundle หลักมีปัญหา และเป็นทางกลับเข้าเว็บให้ผู้ที่เปิดลิงก์เก่าอย่าง `/cookies`

หน้ากฎหมายไม่มี state ไม่เรียก API และไม่แตะที่เก็บข้อมูลของเบราว์เซอร์ จึงเปลี่ยนเนื้อหาได้โดยไม่กระทบ flow การตรวจเอกสาร **แต่ถ้าพฤติกรรมของ Worker เปลี่ยน (เช่น TTL, ขีดจำกัดการใช้งาน) ต้องกลับมาแก้เนื้อหาใน `PrivacyPolicy.tsx` และ `TermsOfService.tsx` ให้ตรงด้วย**

ป้ายลิงก์ใน footer ใช้ชื่อเต็ม (“นโยบายความเป็นส่วนตัว”) ไม่ใช่ “ความเป็นส่วนตัว” ลอย ๆ เพราะ `App.test.tsx` มีด่านกันไม่ให้ข้อความนั้นโผล่ในหน้าตรวจเอกสาร ซึ่งเป็นด่านกันการ์ดขอความยินยอมแบบเก่ากลับมา

### Worker (`worker/`)

- `POST /api/analyze` เป็น boundary เดียวระหว่าง browser กับ Gemini
- ตรวจ `Content-Type`, request size, idempotency key และ body schema **ก่อน** อ่าน cache หรือเรียก model
- ใช้ anonymous token + client IP ที่ hash แล้วสำหรับ cost-abuse guard
- ใช้ KV เก็บ counter events แบบหนึ่งเหตุการณ์ต่อหนึ่ง key และ successful idempotency response แบบ TTL สั้น
- เรียก model หลักและ fallback เมื่อ quota/model availability มีปัญหา
- เริ่มเพดานรวม 100 วินาทีตั้งแต่ขอบ `handleAnalyze`, จำกัด `countTokens` ครั้งละ 10 วินาทีและ model request ครั้งละ 60 วินาที ใช้ `AbortSignal` ชุดเดียวกับ primary, fallback, retry, chunk และ consolidation พร้อม application-level wait boundary แยกที่ 10/60/100 วินาที จึงหยุด Worker รอได้แม้ promise ของ SDK ยังไม่จบ; timeout ราย call ยังลอง fallback ได้ถ้าเพดานรวมเหลือ แต่ timeout/cancel ของเพดานรวมจะไม่เริ่ม provider call ถัดไป
- ตรวจ AI response ด้วย schema **และคำนวณ overall score ด้วยโค้ดฝั่ง Worker**
- `tsconfig.worker.json` ตรวจทั้ง production Worker และ Worker tests ใน strict mode; `npm run worker:check` บังคับ `wrangler types worker/env.d.ts --check`, TypeScript และ dry-run bundle ตามลำดับ จึงจับ binding drift กับ type error ก่อน deploy
- `npm run verify` รัน `scripts/check-test-modifiers.mjs` เพื่อปฏิเสธ `.only`, `.skip`, `.todo`, `.fixme`, `fit` และ `xit`; Vitest ตั้ง `allowOnly: false` และ Playwright ตั้ง `forbidOnly: true` ทุก environment เพื่อไม่ให้ผลเขียวจาก test เพียงบางส่วนถูกใช้เป็นหลักฐาน

## Where the score is calculated

นี่เป็นจุดที่มักเข้าใจผิด จึงระบุให้ชัด:

| เส้นทาง | ใครคำนวณ `overallScore` |
| --- | --- |
| Real API (`/api/analyze`) | **Cloudflare Worker** ด้วย `shared/scoring.ts` แล้วส่งค่าที่คำนวณแล้วกลับมา |
| Mock analysis ใน browser (`createMockAnalysis`) | **Browser** ด้วย `shared/scoring.ts` ตัวเดียวกัน ใช้เฉพาะตอน dev/mock เท่านั้น |

Browser ตรวจ schema และ `apiVersion` แล้วคำนวณ `overallScore` ซ้ำจากหัวข้อที่ Worker ส่งกลับด้วย `shared/scoring.ts` เพื่อปฏิเสธผลที่คะแนนไม่สอดคล้องกันก่อนแสดง ส่วนการจัดลำดับ “สิ่งที่ควรแก้ก่อนส่ง” ก็คำนวณใน browser จากหัวข้อที่เกี่ยวข้องเท่านั้น Worker ยังคงเป็นผู้คำนวณคะแนนฝั่ง API และทั้งสองฝั่งใช้สูตรไฟล์เดียวกัน

`VITE_USE_MOCK_ANALYSIS` รับเฉพาะ `true` หรือ `false` แบบตรงตัว: ถ้าไม่ตั้งค่า local development ใช้ mock และ production ใช้ Worker ตามค่าเริ่มต้น แต่ค่าที่ไม่รู้จักจะปิดปุ่มตรวจพร้อมแจ้ง configuration error เพื่อไม่ให้ค่าที่พิมพ์ผิดแสดงผลตัวอย่างเหมือนผล AI ปุ่ม คำอธิบายระหว่างรอ และหัวผลลัพธ์ระบุโหมดที่ใช้อยู่เสมอ

ใน local real-Worker mode ผู้พัฒนาตั้ง `VITE_USE_MOCK_ANALYSIS=false`; browser ยังเรียก same-origin `/api` และ Vite proxy ส่งต่อไปยัง `wrangler dev` ที่ `127.0.0.1:8787` เท่านั้น จึงไม่ต้องเพิ่ม localhost ลง production CORS และไม่ถอยไปเรียก production Worker เมื่อ local Worker ไม่ทำงาน

## Data flow

```text
User input
  -> browser validation
  -> PDF/text preparation (page limit + size limit)
  -> appendix confirmation
  -> POST /api/analyze
  -> Worker validation (schema first)
  -> idempotency digest check
  -> rate limit + daily budget
  -> bounded Gemini structured response (chunk pass, then consolidation pass เมื่อเอกสารยาว)
  -> Worker schema validation + applicability normalization
  -> Worker score calculation
  -> browser contract/version validation
  -> browser failure classification เมื่อเส้นทางใดล้มเหลว
  -> explainable result cards
```

## Important design decisions

### Browser-first document review

ผู้ใช้เห็นและแก้ไขข้อความที่ extract จาก PDF ก่อนส่งเสมอ ระบบไม่ทำ OCR ใน MVP เพื่อไม่ทำให้ข้อมูลจากภาพถูกตีความโดยไม่มีการยืนยัน

### Code-owned scoring with N/A support

โมเดลให้คะแนนรายหัวข้อและหลักฐาน ส่วนการคำนวณคะแนนรวมอยู่ในโค้ด ทำให้ตรวจสอบสูตร, enabled sections และ denominator ได้ deterministic

แต่ละหัวข้อมีฟิลด์ `applicability` เป็น `applicable` หรือ `not_applicable`:

- หัวข้อที่เป็น `not_applicable` จะไม่ถูกนับทั้งตัวตั้งและตัวหาร การตัดหัวข้อที่ไม่เกี่ยวข้องออกจึงไม่ทำให้คะแนนตก
- Worker บังคับล้าง `evidence`, `missing` และ `score` ของหัวข้อ N/A ทิ้ง เพื่อไม่ให้หลักฐานที่โมเดลกุขึ้นมาหลุดเข้าไปในผลของหัวข้อที่ถูกถอดออกจากการคิดคะแนน
- ถ้าทุกหัวข้อเป็น N/A ระบบคืน `overallScore: null` ไม่ใช่ `0` และ UI แสดงว่า “ไม่มีหัวข้อที่ใช้ประเมิน” เพราะงานที่ไม่มีหัวข้อให้ประเมินไม่ได้แปลว่าทำได้แย่
- ถ้าโมเดลไม่ส่ง `applicability` มา ระบบถือว่า `applicable` เพื่อให้พลาดไปในทางที่ปลอดภัย คือยังนับคะแนนแทนที่จะลบน้ำหนักออกเงียบ ๆ

### Two-stage analysis for long documents

เอกสารที่เกิน token limit ของการเรียกครั้งเดียวจะถูกแบ่งเป็นส่วน (ไม่เกิน 6 ส่วน) โดยไม่ตัดข้อความ แล้ววิเคราะห์สองขั้น:

1. **Chunk pass** — แต่ละส่วนถูกวิเคราะห์พร้อม `CHUNK_CONTEXT` ที่บอกว่ากำลังอ่านส่วนที่เท่าไรจากทั้งหมดกี่ส่วน
2. **Consolidation pass** — ส่ง **เฉพาะ structured findings** ของทุกส่วน (ตัดความยาวแล้ว) เข้าไปสรุปรวม ไม่ส่งข้อความต้นฉบับซ้ำอีกรอบ

ขั้นสรุปรวมประเมิน rubric ของทั้งเอกสาร รวมหลักฐานที่กระจายอยู่คนละส่วน และบันทึกความขัดแย้งข้ามบทลงใน `consistencyNotes` findings จาก chunk ถือเป็น untrusted data เช่นเดียวกับเอกสารต้นฉบับ

ระบบ **ไม่** ใช้วิธีเลือกคะแนนสูงสุดจาก chunk อีกต่อไป หากขั้นสรุปรวมล้มเหลว ระบบคืน `CONSOLIDATION_FAILED` อย่างชัดเจนแทนที่จะเงียบ ๆ แสดงคะแนนที่รวมมาแบบไม่ถูกต้อง

### Thai-only prose, faithful evidence

โมเดลบางครั้งแทรกตัวอักษรจีน/ญี่ปุ่น/เกาหลีลงกลางประโยคภาษาไทย (เคยเจอจริง: `ผู้ตรวจ評価ควรตรวจสอบ`) ระบบกันสองชั้น

1. `SYSTEM_INSTRUCTION` และ `CONSOLIDATION_SYSTEM_INSTRUCTION` ระบุชื่อฟิลด์ที่ต้องเป็นอักษรไทยล้วน และห้ามอักษร CJK ตรง ๆ
2. `containsForeignScript()` ใน Worker ตรวจผลที่ได้จริง ถ้าเจอ → เรียกโมเดลซ้ำ **หนึ่งครั้ง** ด้วย `THAI_SCRIPT_CORRECTION_INSTRUCTION`

การตรวจนี้ครอบเฉพาะข้อความที่โมเดลเขียนเอง (`reason`, `recommendation`, `missing`, `qualityWarnings`, `consistencyNotes`, `referenceComment`) **ไม่ครอบ `evidence`** เพราะ `evidence` คือการยกข้อความจากเอกสารต้นฉบับมาตรง ๆ เอกสารที่เขียนด้วยภาษาอื่นจริงจึงยังตรวจได้ตามปกติ

ถ้าเรียกซ้ำแล้วยังปนอยู่ ระบบ **คืนผลให้ผู้ใช้** ไม่โยน error เพราะตัวอักษรหลุดหนึ่งตัวเป็นเรื่องความสวยงาม ไม่ใช่ความถูกต้องของคะแนน — การทิ้งผลที่ผู้ใช้รอมาแล้วเสียหายกว่า **แต่ไม่เงียบ** ระบบเติม `qualityWarnings` บอกผู้ใช้ว่ารู้ตัวและแก้แล้วไม่หาย เพื่อไม่ให้ผู้อ่านสงสัยผลทั้งฉบับเพราะตัวอักษรตัวเดียว

### วัดคุณภาพภาษาแทนที่จะเดา

คำถาม "prompt ใหม่ทำให้ปนภาษาน้อยลงจริงไหม" ตอบด้วยความรู้สึกไม่ได้ และตอบด้วย log ก็ไม่ได้ เพราะ `head_sampling_rate` ตั้งไว้ที่ `0.1` (เก็บ log แค่ 10% ของ request) เหตุการณ์ที่เกิดนานๆ ครั้งจึงหายไปกับการสุ่ม

ระบบจึงนับลง KV แทน โดยนับเฉพาะตอนเกิดจริง (ไม่ได้เขียนทุก request):

| ตัวนับ | นับอะไร | อ่านที่ไหน |
|--------|---------|-----------|
| `stats:foreign-script-retries:YYYY-MM-DD:event:<uuid>` | โมเดลปนภาษา ระบบเลยขอใหม่ | `foreignScriptRetriesToday` |
| `stats:foreign-script-persisted:YYYY-MM-DD:event:<uuid>` | ขอใหม่แล้วยังปนอยู่ | `foreignScriptPersistedToday` |

แต่ละเหตุการณ์มี key ของตัวเองและอายุ 36 ชั่วโมง จึงไม่มี `get(null) → put(1)` ไปเขียนทับยอดที่สูงกว่าเหมือนตัวนับเดิม ระหว่างย้ายระบบยังอ่านยอด aggregate รุ่นเก่ามารวมแต่ไม่เขียน key รุ่นเก่าอีก อ่านผลรวมได้จาก `GET /api/health?verify=ai` อย่างไรก็ตาม KV ยังเป็น eventual consistency ทำให้รายการเหตุการณ์จากอีกภูมิภาคอาจมาช้า ตัวเลขจึงใช้ดูแนวโน้ม ไม่ใช่หลักฐาน billing แบบทันที การบันทึกล้มเหลว **ห้ามทำให้การตรวจเอกสารล้มเหลว** — เสียข้อมูลหนึ่งจุดยอมรับได้ เสียผลตรวจของผู้ใช้ไม่ได้

### Idempotency by request digest

- KV key เป็น SHA-256 ของ idempotency key ไม่ใช่ค่าดิบจาก client
- record ที่เก็บประกอบด้วย canonical request digest (SHA-256 ของ payload ที่ผ่าน validation แล้ว โดยเรียงคีย์คงที่) และ response ที่ serialize แล้ว
- เมื่อ record มองเห็นแล้ว: key เดิม + payload เดิม → คืนผลเดิมโดยไม่เรียก AI ซ้ำ
- เมื่อ record มองเห็นแล้ว: key เดิม + payload ต่างกัน → `409 IDEMPOTENCY_CONFLICT` (`retryable: false`) แทนที่จะคืนผลของเอกสารอื่น
- request ที่ malformed อ่าน cache ไม่ได้เลย เพราะ body ถูก validate ก่อนแตะ KV
- เก็บเฉพาะ digest ไม่ได้เก็บ `reportText` เพิ่มจาก response ที่ต้องเก็บอยู่แล้ว

ข้อจำกัด: ลำดับแรกยังเป็น `KV get → เรียก Gemini → KV put` ไม่ใช่ reservation แบบ atomic และ KV อาจเห็นค่าข้ามภูมิภาคช้า คำขอแรกที่ชนกันจึงอาจผ่านทั้งคู่ เรียก Gemini ซ้ำ และเขียนแบบ last-write-wins ได้ แต่ digest check ยังป้องกันไม่ให้ cache ส่งผลของ payload หนึ่งกลับให้อีก payload การรับประกัน single-flight จริงต้องมีกลไกประสาน stateful ซึ่งขัดกับข้อกำหนด stateless/KV-only ปัจจุบัน จึงต้องเป็นการตัดสินใจสถาปัตยกรรมแยก ไม่ควรจำลองด้วย mutable global state ใน Worker

### Token budget accounting

Worker จอง daily request slot หลัง validation แต่ก่อนสร้าง SDK หรือเรียก Google ทุกชนิด รวมถึง `countTokens`; คำขอที่ provider ล้มภายหลังจึงยังนับหนึ่งครั้งแบบ conservative เพื่อไม่ให้ outage/การลองซ้ำยิง provider เกินเพดาน จากนั้นก่อน application-level model call แต่ละครั้ง ระบบจองงบ token โดยใช้ `countTokens` กับ prompt จริงและบังคับ `maxOutputTokens` ตามจำนวนหัวข้อใน rubric การจองแต่ละครั้งเขียนเป็น event key แยก จึงไม่มี stale/null overwrite แบบ read-modify-write เดิม และครอบคลุม chunk pass, consolidation pass, JSON validation retry กับการรันซ้ำบน fallback model แยกกัน แต่รายการ KV ยังมองเห็นข้ามภูมิภาคช้าได้ ไม่ใช่ hard global ceiling, ไม่ใช่ยอด billing จริง และมองไม่เห็น retry ภายใน SDK

Gemini 3 ใช้ `thinkingLevel: low` สำหรับงาน rubric ที่เป็น constrained instruction-following เพื่อลด latency และเหลือ generation allowance ให้ JSON ครบภายใน timeout ของ browser

### API versioning

`apiVersion` เป็นค่าคงที่ที่ Worker ประทับบน `/api/health` และผล v1 ของ `/api/analyze` ส่วน request v1 ระบุ `X-RubricLensAi-Api-Version: 1` โดยยังรับ header ชื่อเดิมชั่วคราวระหว่างย้ายแบรนด์

- Browser ปฏิเสธเวอร์ชันที่ไม่รู้จักและบอกผู้ใช้ให้รีเฟรช แทนที่จะ parse บางส่วนแล้วรายงานคะแนนผิด
- response รุ่นก่อนที่ยังไม่มี `apiVersion` ถูก parse ด้วย schema แยกต่างหากสำหรับช่วง rolling deployment แล้ว upgrade อย่างชัดเจน (ทุกหัวข้อเป็น `applicable`) พร้อมเพิ่ม quality warning ให้ผู้ใช้เห็นว่าผลมาจากเซิร์ฟเวอร์รุ่นก่อน ไม่ใช่ซ่อนความต่างไว้
- compatibility Worker ตรวจ client รุ่นเดิมจากการไม่มี version header แล้วคืน v0 shape แบบ exact; cache idempotency แยกตาม API version เพื่อไม่ให้ response ข้าม contract
- frontend คำนวณคะแนนและ summary ซ้ำเพื่อยืนยันความสอดคล้องก่อนแสดงผล และปฏิเสธ N/A ที่ยังมีคะแนน หลักฐาน หรือรายการที่ขาด

### Health check ที่แยก "ตั้งค่าไว้" ออกจาก "ใช้ได้จริง"

`aiConfigured` บอกได้แค่ว่า **มีค่า** `GEMINI_API_KEY` อยู่ ไม่ได้บอกว่า Google ยังรับ key นั้น — key ที่ถูกลบไปแล้วหน้าตาเหมือน key ที่ใช้ได้ทุกประการเมื่อมองจากใน Worker (เกิดขึ้นจริงแล้ว ดู `LESSONS.md` บทที่ 6)

| endpoint | ทำอะไร | ค่าใช้จ่าย |
|----------|--------|-----------|
| `GET /api/health` | ตอบทันทีจาก env ที่มีอยู่ ไม่ต่อออกนอก | ฟรี |
| `GET /api/health?verify=ai` | เรียก `countTokens` จริงเพื่อถาม Google ว่า key ยังใช้ได้ไหม แล้วเพิ่ม `aiReachable` กับ `aiCheckCode` | ไม่กิน generation quota |

โหมด verify ส่ง abort signal ให้ SDK และมี application-level wait boundary 5 วินาทีด้วย จึงคืน `GEMINI_TIMEOUT` แบบ degraded ได้แม้ promise ของ SDK ไม่ยอมจบตาม signal จากนั้น cache คำตอบไว้ใน KV 5 นาที เพื่อไม่ให้ endpoint สาธารณะถูกยิงถล่มจนกิน rate limit ที่การตรวจเอกสารจริงต้องใช้ ถ้า key ใช้ไม่ได้จะได้ `status: "degraded"` + HTTP 503 แทนที่จะรายงานว่าปกติ

คำตอบที่ cache ไว้อาจเก่าได้ถึง 5 นาที ซึ่งอันตรายตอนที่เพิ่งเปลี่ยน key เสร็จ (จะเห็นคำตัดสินที่ตัดสินไว้**ก่อน**เปลี่ยน) ระบบจึงคืน `aiCheckAgeSeconds` มาด้วยเสมอ ถ้าค่านี้มากกว่าเวลาที่ผ่านไปตั้งแต่เปลี่ยน key แปลว่ายังไม่ได้ตรวจของใหม่

### ตัวเฝ้าอัตโนมัติรายชั่วโมง

`?verify=ai` ตอบได้ก็ต่อเมื่อมีคนนึกจะถาม ระบบจึงมี Cron Trigger (`0 * * * *` ตั้งใน `wrangler.jsonc`) เรียก `scheduled()` ทุกชั่วโมงให้ถามเอง

- **ข้ามแคชเสมอ** — ถ้าอ่านแคชก็จะได้คำตอบเดิมที่ตัวเองเพิ่งเขียนไว้ ตัวเฝ้าจึงต้องยิงถาม Google จริงทุกครั้ง แล้วเขียนแคชทับให้คนที่มาอ่าน `?verify=ai` ต่อได้ประโยชน์
- **เงียบเมื่อปกติ** — เขียน log ระดับ info เฉยๆ เพราะการแจ้งเตือนที่ดังทุกชั่วโมงคือการแจ้งเตือนที่ไม่มีใครอ่าน
- **ดังเมื่อพัง** — เขียน `console.error` และยิง webhook **ก่อน** refresh health cache เพื่อให้ KV ล่มแล้วไม่กลืนสัญญาณ outage; payload เป็น `{content, text, code}` (`content` สำหรับ Discord, `text` สำหรับ Slack)
- **outage ทำให้ cron run แดงเสมอ** — หลังเขียน log, พยายามส่ง webhook และ refresh cache แล้ว `scheduled()` จะ throw ด้วย `aiCheckCode` เพื่อให้ Cloudflare บันทึก invocation ว่าล้มเหลว แม้ไม่ได้ตั้ง webhook หรือ webhook พัง
- **webhook พังไม่กลืนสาเหตุหลัก** — การยิง webhook ถูกครอบ try/catch, มีเพดานเวลา 5 วินาที และ HTTP non-2xx ถูกบันทึกเป็น `gemini_watch_alert_failed`; จากนั้น cron ยังล้มด้วยสถานะ Gemini เดิม ไม่ใช่ด้วยรายละเอียดช่องแจ้งเตือน
- **cache พังก็ทำให้ cron run แดงหลังแจ้งเตือนแล้ว** — ช่วยให้ runtime บันทึก scheduled invocation ว่าล้มเหลว โดยไม่ตัด log/webhook ของ outage ออก

`ALERT_WEBHOOK_URL` **ไม่ได้อยู่ใน `secrets.required`** โดยตั้งใจ เพื่อให้ deploy ได้โดยไม่ต้องเลือกช่องทางแจ้งเตือนก่อน — ไม่ตั้งก็ยังทำให้ Cron Past Events ขึ้น failed แต่ไม่มีข้อความเด้ง และ Workers Logs ยังขึ้นกับ `head_sampling_rate`

### Explicit appendix consent

เมื่อพบ appendix ระบบหยุดก่อน network request และแสดง accessible dialog ผู้ใช้เลือก “กลับไปแก้ข้อความ” หรือ “ยืนยันและส่งตรวจ” ได้อย่างชัดเจน เมื่อยืนยัน browser จะส่งเฉพาะ `preparedDocument.mainText`; ข้อความ appendix จึงไม่ออกจากเครื่องผู้ใช้ไปถึง Cloudflare หรือ Gemini ส่วน Worker ยังเรียก `prepareWorkerDocument()` ซ้ำเป็นแนวป้องกันชั้นที่สองสำหรับ client อื่นที่อาจส่งข้อความดิบเข้ามาเอง

### Resource guards on PDF input

ไฟล์ PDF ถูกจำกัดขนาด 10 MB, จำนวนหน้า 400 หน้า, ข้อความดิบ/ผลลัพธ์ 300,000 ตัวอักษร และ text items 300,000 รายการ ระบบตรวจจำนวนหน้าทันทีหลังเปิดเอกสาร แล้วตรวจเพดานสะสมทุกหน้าก่อนอ่านหน้าถัดไป พร้อมคืน loading task เสมอผ่าน `finally` การหาแถวใช้ y-bucket และตรวจหลายคอลัมน์ด้วยการ sort ครั้งเดียวต่อแถวแทนการวน/เรียงใหม่ทุก item

ข้อจำกัดที่ยังเหลือ: PDF.js ต้องสร้าง `content.items` ของหน้าปัจจุบันก่อน application code จะนับได้ และการประกอบข้อความยังอยู่บน main thread เพดานใหม่จึงจำกัดความเสียหายและหยุดหน้าถัดไป แต่ไม่รับประกันว่า PDF อันตรายซึ่งอัดทุกอย่างไว้หน้าเดียวจะไม่มี allocation spike เลย

### Bounded model waiting

การยกเลิกหรือหมดเวลาที่ browser ไม่ได้รับประกันว่า Gemini ฝั่งผู้ให้บริการจะหยุดประมวลผลและหยุดคิดค่าใช้จ่ายทันที Worker จึงไม่พึ่ง browser timeout เพียงชั้นเดียว:

- `wrangler.jsonc` เปิด `enable_request_signal` เพื่อส่งสัญญาณยกเลิกจาก request เข้า Worker
- Worker รวมสัญญาณของ request กับเพดานวิเคราะห์รวม 100 วินาที แล้วส่งสัญญาณเดียวกันให้ทุก `countTokens` และ `generateContent`
- รอบ SDK promise แต่ละจุดมี application-level wait boundary ที่แข่งกับทั้ง shared signal และเพดานย่อยของ call นั้น ขณะที่ SDK ยังรับ shared signal กับ HTTP timeout เดิม จึงหยุด workflow ได้ตรง 10/60/100 วินาทีแม้ retry ภายใน SDK ทำให้ promise ต้นทางยัง pending
- `countTokens` มีเพดานย่อย 10 วินาที และ model request มีเพดานย่อย 60 วินาที; retry และ fallback ใช้เวลาจากเพดานรวมเดียวกัน ไม่ได้เริ่มนาฬิกาใหม่
- ถ้าผู้ใช้ยกเลิก ระบบคืน `REQUEST_CANCELLED`; ถ้าชนเพดานรวม ระบบคืน `GEMINI_TIMEOUT` และไม่เริ่ม fallback เพิ่มหลัง deadline

ข้อจำกัดที่ยังมีโดยธรรมชาติของ API คือการ abort เป็นการหยุดรอฝั่ง client/Worker; งานที่ผู้ให้บริการรับไปแล้วอาจทำต่อและคิดโควตาได้ จึงต้องคง budget ledger และการเฝ้าดูค่าใช้จ่ายไว้ด้วย ไม่ควรอ้างว่า abort เท่ากับยกเลิก billing

### Brand asset flow and mascot semantics

แหล่งความจริงของมาสคอตคือ `docs/brand/logo/build-mascots.py` เมื่อรันแล้วจะสร้างชุด SVG เอกสารใน `docs/brand/logo/`, คัดลอกสามสถานะที่เว็บใช้ไป `src/assets/brand/` และคัดลอก favicon ไป `public/favicon.svg` ส่วน `docs/brand/og/render-og.py` สร้างภาพแชร์และคัดลอกผลไป `public/og.png` หลัง render สำเร็จ

เว็บใช้มาสคอตตามความหมายของ state เท่านั้น:

- หัวมาสคอต: ส่วนหัวของหน้าเริ่มต้น/เตรียมข้อมูล และ error ที่ไม่ใช่ system failure (ยังเป็น product identity ไม่ใช่ภาพบอกว่าระบบล่ม)
- มาสคอตกำลังคิด: ระหว่าง `analyzing`
- มาสคอตออฟไลน์: เฉพาะความล้มเหลวหมวด `network`, `service` หรือ `unexpected`
- หน้าผลคะแนน: ไม่มีมาสคอต และไม่มี state “เสร็จแล้ว” ชั่วคราวที่สร้างขึ้นเพื่อโชว์ภาพ

validation, quota, compatibility และ idempotency conflict ยังมีข้อความกับทางแก้ที่ตรงสาเหตุ แต่ไม่ใช้มาสคอตออฟไลน์ เพราะระบบอาจทำงานถูกต้องอยู่

### Failure-aware API

ระบบรองรับ malformed JSON, schema mismatch, transient model failure, timeout, cancel, retry, idempotency conflict, consolidation failure และ API version mismatch เพื่อป้องกัน double submission และผลลัพธ์ที่แสดงไม่ครบ ฝั่ง browser จัดหมวดด้วย error code/status ที่บอกความหมาย ไม่ใช้ `retryable` เป็นตัวแทนว่า “ระบบพัง” เพราะ quota อาจลองใหม่ได้แต่ไม่ใช่ outage ขณะที่ config ของบริการอาจเป็น system failure ที่ลองซ้ำเองไม่หาย

ปุ่มลองใหม่ใน alert และปุ่ม “ตรวจรายงาน” ใช้นโยบายเดียวกัน: conflict สร้าง idempotency key ใหม่และลองได้ทันที; network/service timeout และการยกเลิกโดยผู้ใช้พัก 10 วินาที; Gemini congestion พัก 60 วินาที; validation ปลดล็อกเมื่อแก้ข้อมูล; hourly/daily quota, config และ version mismatch ไม่ส่งคำขอเดิมซ้ำแบบไร้ผล ข้อผิดพลาดที่ไม่มี code ใช้ HTTP status เป็น fallback และไม่แสดงข้อความดิบจากระบบภายใน

## จุดเปราะ — แก้ตรงไหนแล้วเสี่ยงพังที่อื่น

เรียงจากอันตรายที่สุดลงมา "อันตราย" ในที่นี้วัดจาก **โอกาสที่จะพังแบบเงียบ ๆ** (คือระบบยังทำงานต่อได้ ไม่มี error ขึ้น แต่ผลลัพธ์ผิด) เพราะแบบนั้นคือแบบที่จับได้ยากที่สุด

| อันดับ | ไฟล์ | ทำไมถึงเปราะ | พังแล้วเห็นยังไง |
| --- | --- | --- | --- |
| 1 | `shared/scoring.ts` (~42 บรรทัด) | สูตรคะแนนชุดเดียวที่ Worker และ browser ใช้ร่วมกัน และ browser ยังคำนวณซ้ำเพื่อ **ตรวจทาน** ผลจาก Worker แก้ที่นี่ = ทั้งสองฝั่งเปลี่ยนพร้อมกัน จึงตรวจกันเองไม่เจอ | คะแนนผิดโดยไม่มี error ผู้ใช้ไม่มีทางรู้ |
| 2 | `shared/api-contract.ts` (~44 บรรทัด) | `API_VERSION` ผูกสามที่: browser ที่ปฏิเสธเวอร์ชันแปลกปลอม, Worker ที่ประทับเวอร์ชัน และ key ของ idempotency cache ที่แยกตามเวอร์ชัน | ผู้ใช้เจอ "กรุณารีเฟรช" ตลอด หรือได้ผลเก่าจาก cache ข้ามเวอร์ชัน |
| 3 | `worker/src/index.ts` (~900 บรรทัด) | ไฟล์ใหญ่ที่สุดของโปรเจกต์ และ **ลำดับการทำงานมีความหมาย**: ต้อง validate → เช็ค idempotency → กันงบ → ค่อยเรียก model สลับลำดับแล้ว request ขยะจะแตะ KV หรือเผางบได้ | ค่าใช้จ่ายบานปลาย หรือ cache ปนเปื้อน |
| 4 | กฎ N/A (`applicability`) กระจาย 3 ที่ | นิยามอยู่ `shared/api-contract.ts`, Worker เป็นคนล้าง `evidence`/`score` ของหัวข้อ N/A, แล้ว `src/lib/analysis.ts` เป็นคนปฏิเสธ N/A ที่ยังมีคะแนนติดมา แก้ที่เดียวไม่พอ | หลักฐานที่โมเดลกุขึ้นมาหลุดเข้าผลลัพธ์ หรือคะแนนรวมเพี้ยนเพราะตัวหารผิด |
| 5 | `worker/src/prompt.ts` (~250 บรรทัด) | ข้อความ prompt เป็น "สัญญา" กับ `ANALYSIS_RESPONSE_JSON_SCHEMA` แก้ถ้อยคำแล้วลืมแก้ schema (หรือกลับกัน) โมเดลจะตอบผิดรูป | ผู้ใช้เจอ "ผลลัพธ์ AI ไม่อยู่ในรูปแบบที่ระบบรองรับ" |
| 6 | `wrangler.jsonc` | ค่าใน `vars` ถูกเขียนทับได้จากหน้าเว็บ Cloudflare dashboard ซึ่งไม่ทิ้งร่องรอยใน git — **เคยพังมาแล้วจริง** (ดู `LESSONS.md` บทที่ 1) | เว็บเรียก API ไม่ได้ ขึ้น `Failed to fetch` ที่ไม่บอกสาเหตุ |
| 7 | `src/App.tsx` (~800 บรรทัด) | workflow ทั้งหมดอยู่ไฟล์เดียว ตั้งแต่รับไฟล์ แก้ rubric ไปจนถึงแสดงผล state หลายตัวผูกกัน แต่มี `App.test.tsx` (~550 บรรทัด) คุมอยู่พอควร | UI ค้างที่ขั้นตอนใดขั้นตอนหนึ่ง |
| 8 | `src/lib/pdf.ts` | extract ทีละหน้าบน main thread (เธรดเดียวกับที่วาดหน้าจอ) แม้มีด่าน bytes/pages/chars/items และตัดลูปกำลังสองแล้ว แต่ PDF.js ยังสร้าง items ของหน้าปัจจุบันก่อน application code ตรวจได้ | แท็บอาจสะดุดหรือใช้หน่วยความจำสูงกับหน้าเดียวที่ซับซ้อนมาก |
| 9 | เนื้อหาหน้ากฎหมาย (`src/pages/PrivacyPolicy.tsx`, `TermsOfService.tsx`) | เป็นคำประกาศต่อสาธารณะว่าระบบทำอะไรกับข้อมูลผู้ใช้ ถ้าโค้ดฝั่ง Worker เปลี่ยน (TTL, ขีดจำกัด, ปลายทางที่ส่งข้อมูลไป) แล้วไม่แก้หน้านี้ เอกสารจะกลายเป็นคำประกาศเท็จโดยไม่มีอะไรเตือน ส่วนชื่อคีย์ที่เก็บบนเครื่องผู้ใช้และตัวเลขขีดจำกัดมีเทสต์คุมไว้แล้ว | ไม่เห็นเลยจนกว่าจะมีคนทักท้วง |
| 10 | `CONTACT_EMAIL` ใน `src/lib/site-info.ts` | เป็นช่องทางติดต่อตามกฎหมายที่ประกาศไว้ทั้งสองหน้า ถ้าอีเมลนี้รับเมลไม่ได้จริง (โดเมนยังไม่ต่อ DNS หรือยังไม่ตั้ง email routing) ผู้ใช้จะส่งแล้วเด้งกลับโดยเราไม่รู้ | เงียบสนิท ไม่มีใครแจ้งได้ว่าติดต่อไม่ได้ |

**กฎปฏิบัติที่ตามมาจากตารางนี้:**

- แตะอันดับ 1–4 → ต้องมี test ใหม่ที่จับความผิดนั้นได้ก่อนแก้เสมอ ไม่งั้นไม่มีใครรู้ว่าพัง
- แตะอันดับ 1 หรือ 2 → ต้องรัน `npm run verify` เต็มชุด ไม่ใช่แค่ `npm test`
- แก้ค่า config ของ production → แก้ที่ `wrangler.jsonc` แล้ว deploy เท่านั้น **ห้ามแก้ผ่าน dashboard**
- แก้พฤติกรรมการเก็บข้อมูล (TTL, ขีดจำกัดต่อชั่วโมง, ปลายทางที่ส่งข้อมูลไป) → ต้องแก้เนื้อหาในหน้านโยบายให้ตรงในการเปลี่ยนแปลงครั้งเดียวกัน

## Trade-offs and next steps

- counter events แยก key ป้องกัน stale/null overwrite แต่ KV ยังเป็น eventually consistent จึงไม่ใช่ rate limit หรือ cost ceiling แบบ atomic; hard ceiling ต้องพึ่ง provider-side quota/budget alert หรือกลไกประสานการเขียนที่เจ้าของอนุมัติภายหลัง
- progress ใน UI เป็น estimated progress ไม่ใช่ server-side streaming event
- MVP ใช้ text layer และไม่ทำ OCR
- consolidation pass เพิ่มการเรียก model หนึ่งครั้งต่อเอกสารยาว แลกกับความถูกต้องของคะแนนรวม
- ควรเพิ่ม token-cost telemetry และ budget alert ที่ผูกกับค่าใช้จ่ายจริงใน production
- คุณภาพของการรวมผลข้ามส่วนขึ้นกับคุณภาพของ findings จาก chunk pass ซึ่งยังไม่มี ground-truth dataset วัดผลอย่างเป็นระบบ
