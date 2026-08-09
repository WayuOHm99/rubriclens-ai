# เฟส 2 — บันทึกการเชื่อมระบบแบรนด์เข้ากับเว็บจริง

> **สถานะ:** implemented และตรวจในเครื่องแล้ว รอ owner review
> **อัปเดตล่าสุด:** 8 สิงหาคม 2569
> **หลักฐาน remote/production:** ไม่รวมอยู่ในบันทึกนี้; ณ checkpoint วันที่ด้านบนยังไม่ได้ deploy และต้องดูผลล่าสุดที่ `docs/testing-report.md`
> **เฟส 1:** `563716c` — สร้างระบบแบรนด์ใน `docs/brand/` โดยยังไม่แตะเว็บ

เอกสารนี้เริ่มต้นเป็นแผนก่อนลงมือ ตอนนี้ปรับเป็น **implementation record** เพื่อบอกว่าสิ่งใดมีอยู่ในโค้ดจริง สิ่งใดยังไม่ทำ และต้องดูแลต่ออย่างไร โดยไม่ตีความคำว่า “ตรวจในเครื่องแล้ว” ว่า “ขึ้น production แล้ว”

---

## 1. เป้าหมายและขอบเขตที่รักษาไว้

Phase 2 มีเป้าหมายให้หน้าเว็บดูเป็น RubricLensAi ชุดเดียวกัน โดยไม่เปลี่ยนสูตรคะแนน, API contract หรือ prompt ของโมเดลเพียงเพื่อความสวยงาม

หลักที่ใช้ตัดสินใจ:

1. AI เป็นผู้ช่วย แต่ rubric และการตัดสินของคนยังเป็นหลัก
2. คะแนนต่ำคือข้อมูลสำหรับปรับงาน ไม่ใช่ system failure
3. ใช้มาสคอตเพื่ออธิบาย state เท่านั้น ไม่ใช้เป็นของตกแต่งทุกหน้า
4. ไม่เพิ่ม application state เพียงเพื่อโชว์ asset
5. เปลี่ยนสีตรงที่ทำให้แบรนด์ไม่ต่อเนื่อง ไม่ไล่ refactor สีทุกค่าที่มีความหมายเฉพาะอยู่แล้ว
6. runtime asset ต้องอยู่ในเส้นทางที่ Vite/Cloudflare Pages build จริง ไม่อ้าง `docs/` โดยตรง

---

## 2. สิ่งที่มีอยู่ใน implementation แล้ว

### 2.1 Repository hygiene และ dependency classification

- `.gitattributes` กำหนดไฟล์ข้อความเป็น LF และให้ Git ตรวจรักษา binary asset โดยอัตโนมัติ
- `.gitignore` กันพื้นที่รีวิวภายในเครื่อง (`correct/`) ไม่ให้ปนใน public repository
- `shadcn@4.16.1` อยู่ใน `devDependencies` เพราะใช้เป็น tooling/แหล่ง CSS ตอน build (`src/index.css` import `shadcn/tailwind.css`) ไม่ใช่แพ็กเกจที่ browser ต้องโหลดหลัง build
- การย้ายกลุ่ม dependency เดิมไม่เปลี่ยนเวอร์ชันของ `shadcn`; สถานะ audit ล่าสุดให้ดู `docs/testing-report.md` ซึ่งแยก production audit ออกจากทั้ง dependency tree

### 2.2 Favicon, Open Graph และ metadata

- `public/favicon.svg` สร้างจาก `docs/brand/logo/build-mascots.py`
- `public/og.png` ขนาด 1200×630 sync จาก `docs/brand/og/render-og.py`
- `theme-color` ใช้ `#286096` ตรงกันใน `index.html`, `privacy.html`, `terms.html` และ `public/404.html`
- หน้า 404 แบบ standalone เปลี่ยนสี template เดิมเป็นสีแบรนด์ โดยยังไม่พึ่ง React bundle
- `public/icons.svg` ของ template ถูกลบหลังค้นยืนยันว่าไม่มีผู้เรียกใช้
- canonical/OG URL ยังใช้ `rubriclensai.pages.dev` เพราะ custom domain ยังไม่พร้อม cutover

### 2.3 Semantic design-token bridge

`src/index.css` เก็บค่าแบรนด์ชื่อ `--rl-*` และเชื่อมเข้าชื่อเชิงความหมายของ shadcn/Tailwind เช่น:

- `--background`, `--foreground`, `--card`, `--border`
- `--primary`, `--primary-foreground`, `--ring`
- `--muted`, `--muted-foreground`, `--accent`
- token แบบ soft สำหรับ brand, success และ danger

การเชื่อมที่จุดกลางทำให้ปุ่ม การ์ด ช่องกรอก และหน้า legal ใช้ระบบเดียวกันโดยไม่ต้องเปลี่ยนทุก component สี warning/information ที่ยังระบุตรงใน `App.tsx` ถูกเก็บไว้เมื่อสีนั้นมีหน้าที่ชัด ไม่ได้เป็นสี template/brand หลัก

คะแนนรวมใช้ `text-primary` แบบเป็นกลาง ไม่เพิ่ม threshold หรือระบบไฟจราจรที่อาจทำให้คะแนนดูเป็นคำตัดสินผ่าน/ตก

### 2.4 Runtime mascot assets

แหล่งความจริงยังเป็นสคริปต์ ไม่ใช่ไฟล์ SVG ที่สร้างแล้ว:

```text
docs/brand/logo/build-mascots.py
  -> docs/brand/logo/*.svg
  -> src/assets/brand/mascot-head.svg
  -> src/assets/brand/mascot-thinking.svg
  -> src/assets/brand/mascot-offline.svg
  -> public/favicon.svg
```

`src/assets/brand/` ถูกเลือกแทนการอ้าง `docs/` โดยตรง เพื่อให้ Vite ตรวจ asset, ใส่ hash สำหรับ cache และคัดลอกเข้า build output แน่นอน ส่วน favicon/OG อยู่ `public/` เพราะ HTML และ social crawler ต้องอ้าง path คงที่

ตำแหน่งที่เว็บใช้จริง:

| state | asset | เหตุผล |
|---|---|---|
| หน้าเริ่มต้น/เตรียมข้อมูล และ error ที่ไม่ใช่ system failure | `mascot-head.svg` ในส่วนหัว | แสดงตัวตนแบรนด์โดยไม่อ้างว่าระบบล่ม |
| `analyzing` | `mascot-thinking.svg` | อธิบายว่าระบบกำลังทำงาน พร้อม progress และปุ่มยกเลิก |
| `error` หมวด `network`, `service`, `unexpected` | `mascot-offline.svg` | สื่อว่าระบบหรือการเชื่อมต่อมีปัญหา |
| validation, quota, compatibility, conflict | ไม่มี offline mascot | ระบบอาจยังทำงานถูกต้อง ผู้ใช้ต้องได้ข้อความที่ตรงกับสาเหตุ |
| result/score | ไม่มีมาสคอต | รักษาความเป็นกลางของผลตรวจ |

ไม่มี state “done” เพิ่มระหว่าง `analyzing` กับ `result`; `result` คือ completion state ที่มีอยู่แล้ว และไม่ควรหน่วงผู้ใช้เพื่อโชว์ภาพ

### 2.5 Error semantics ที่รองรับ mascot อย่างปลอดภัย

`src/lib/analysis-failure.ts` แยกหมวดความล้มเหลวเป็น:

- `validation` — request/input ที่ต้องแก้
- `quota` — rate limit หรือ budget/quota เต็ม
- `compatibility` — client/Worker คนละ API version
- `conflict` — idempotency key เดิมกับ payload ต่างกัน
- `network` — browser ติดต่อ Worker หรืออ่าน response ไม่ได้
- `service` — Worker/AI/model/response contract ล้มเหลว
- `unexpected` — exception ในหน้าเว็บที่ยังจัดหมวดไม่ได้

`retryable` ยังบอกได้ว่าลองซ้ำมีโอกาสช่วยหรือไม่ แต่ **ไม่ได้ใช้แทนความหมายว่า system failure** เช่น quota อาจลองใหม่ภายหลังได้แต่ไม่ใช่ระบบล่ม ขณะที่ AI configuration เป็น service failure แม้ผู้ใช้ลองซ้ำเองไม่หาย

### 2.6 Accessibility และ responsive behavior

- progress มีชื่อ, ค่า และข้อความที่ screen reader อ่านได้ โดยไม่ประกาศซ้ำจนรบกวน
- rubric validation ผูกข้อความ error กับแถว/ช่องที่ผิดด้วย `aria-invalid` และ `aria-describedby`
- link/button สำคัญมี focus ที่มองเห็นและพื้นที่กดเหมาะกับมือถือ
- ตารางหน้า privacy เลื่อนด้วย keyboard ได้ในจอแคบ
- workflow สำคัญตรวจที่ความกว้าง 320px และแก้ minimum width ที่เคยทำให้เกิด horizontal overflow
- motion ของ progress เคารพ `prefers-reduced-motion`

### 2.7 Dead code และ asset cleanup

- ลบ `src/App.css` ซึ่งเป็น CSS จาก Vite template และไม่มี import
- ลบ `public/icons.svg` ซึ่งไม่มี runtime/static reference
- เก็บ source และ generated brand assets ใน `docs/brand/` ไว้เพื่อสร้างซ้ำและตรวจที่มาได้ ไม่ลบเพียงเพราะ runtime มีสำเนา

---

## 3. งานนอกขอบเขตแบรนด์ที่อยู่ใน branch เดียวกัน

รายการด้านล่าง **ไม่ใช่เกณฑ์รับงานแบรนด์ของ Phase 2** แต่ถูกทำและ commit อยู่ใน branch เดียวกันระหว่างเตรียม owner review จึงต้องตรวจความเสี่ยงแยกจากหน้าตาแบรนด์ เอกสารนี้แจกแจงไว้เพื่อไม่ให้การเปลี่ยนพฤติกรรมระบบถูกซ่อนอยู่ใต้ชื่องานแบรนด์

### Worker model timeout

- analysis หนึ่งคำขอมีเพดานรวม 100 วินาที
- `countTokens` จำกัดครั้งละ 10 วินาที และ model request จำกัดครั้งละ 60 วินาที
- request abort และ global deadline ถูกรวมเป็น signal เดียว ส่งผ่าน primary, fallback, retry, chunk และ consolidation
- `wrangler.jsonc` เปิด `enable_request_signal` ให้ Worker รับสัญญาณยกเลิกจาก browser
- deadline คืน `GEMINI_TIMEOUT`; การยกเลิกคืน `REQUEST_CANCELLED`; deadline ไม่เริ่ม fallback ใหม่

ข้อจำกัด: การ abort หยุดการรอฝั่ง client/Worker แต่ผู้ให้บริการอาจประมวลผลงานที่รับไปแล้วต่อและคิดโควตาได้ จึงยังต้องใช้ budget guard และ monitoring ไม่ควรอ้างว่าการกดยกเลิกยกเลิก billing ได้แน่นอน

### CI hardening

- quality job มี timeout 30 นาที ป้องกัน run ค้างไม่สิ้นสุด
- concurrency ยกเลิก run เก่าของ branch/PR เดียวกันเมื่อมี commit ใหม่
- GitHub Actions จากภายนอกถูกตรึงด้วย commit SHA
- `npm run verify` ปฏิเสธ test ที่ถูก focus, skip, todo หรือ fixme และมี PR template บังคับให้รายงานหลักฐาน/ความเสี่ยง
- ยังใช้ job เดียวตามขนาดโปรเจกต์ ไม่แยกหลาย job เพียงเพื่อให้ดูซับซ้อน
- production audit gate ไม่ถูกลดระดับหรือข้าม

### Cost guard และ scheduled monitoring

- ตัวนับ rate limit, จำนวนคำขอ, token budget และสถิติภาษาเปลี่ยนจากการเขียนยอดรวม key เดิม เป็นหนึ่ง event ต่อหนึ่ง key แล้วรวมยอดตอนอ่าน เพื่อลดความเสี่ยงที่ค่า `null` ล้าสมัยเขียนทับยอดจริง
- daily request budget ถูกจองก่อนเริ่ม provider call เพื่อไม่ให้คำขอที่เริ่มใช้ทรัพยากรแล้วหลุดจากการนับ
- scheduled Gemini probe ทำให้ invocation ล้มเมื่อ Gemini ใช้งานไม่ได้หรือ health cache เขียนไม่ได้ และถือ webhook ที่ตอบ non-2xx เป็นการแจ้งเตือนล้มเหลว
- ค่า aggregate รุ่นเก่ายังถูกอ่านระหว่าง migration แต่ไม่ถูกเขียนเพิ่ม; KV ยังเป็น eventually consistent และไม่ใช่ hard billing ceiling

### PDF extraction safeguards

- การดึงข้อความหยุดเมื่อเกิน 300,000 ตัวอักษรหรือ text items แทนการสร้างข้อมูลทั้งหมดก่อนตรวจ
- การจัดกลุ่มบรรทัดใช้ y-bucket และการตรวจหลายคอลัมน์ไม่ sort array ใหม่ทุกครั้ง เพื่อลดงานที่โตแบบกำลังสองกับ PDF ที่ซับซ้อน

### Local development และ build verification

- Vite dev server ส่งต่อ `/api` ไปยัง local Worker ที่ `127.0.0.1:8787` เพื่อไม่ให้การทดสอบในเครื่องยิง production โดยไม่ตั้งใจ
- `worker:check` ตรวจ generated binding, TypeScript ของ Worker และ dry-run bundle ตามลำดับ
- `shadcn` ถูกย้ายไป `devDependencies` โดยไม่เปลี่ยนเวอร์ชัน; Wrangler ถูกอัปเดตจาก `4.118.x` เป็น `4.120.x` และรายการ install scripts ที่ audit แล้วถูกบันทึกใน `package.json`

---

## 4. ไฟล์เปราะที่รักษาขอบเขตไว้

Phase 2 ไม่เปลี่ยน:

- `shared/scoring.ts` — สูตรคะแนน
- `shared/api-contract.ts` — API version/contract
- `worker/src/prompt.ts` — prompt และ schema contract ของโมเดล

เป้าหมายแบรนด์ไม่ได้แก้ไฟล์เหล่านี้ แต่ branch เดียวกันมีงาน reliability ที่ตรวจแยกตามหัวข้อ 3:

- `worker/src/index.ts` เปลี่ยน deadline/abort, วิธีบันทึก counter events, จังหวะจอง daily request budget และพฤติกรรม scheduled monitoring
- `wrangler.jsonc` เพิ่ม `enable_request_signal` และแก้คำอธิบายการแจ้งเตือนให้ตรงกับ scheduled invocation

การเปลี่ยนเหล่านี้มี focused regression tests และไม่แก้สูตรคะแนน, API version, model prompt, response shape หรือค่าตัวเลขของ token threshold แต่ **เปลี่ยนวิธีบังคับใช้ budget และวิธีรายงาน outage** จึงต้องรีวิวเป็นงานระบบ ไม่ใช่อนุมานว่าปลอดภัยจากการเป็นส่วนหนึ่งของงานแบรนด์

---

## 5. การตัดสินใจที่ตั้งใจไม่ทำ

- **ไม่สร้าง score-color threshold** — เอกสารแบรนด์ไม่ได้กำหนดสูตรผ่าน/ตก และการเพิ่มจะเป็น product logic ใหม่
- **ไม่เปลี่ยน validation ทุกจุดให้พ้นสีแดง** — danger สีหม่นใช้กับ input ที่ต้องแก้ได้ ถ้ามีข้อความบอกสาเหตุและไม่ใช้ system mascot; แต่แดงห้ามใช้กับคะแนน/เนื้อหาที่ยังขาด
- **ไม่เพิ่ม completion state** — ไม่มีปัญหาผู้ใช้ที่ต้องแก้ และจะเพิ่ม transition/test เพียงเพื่อ asset
- **ไม่วาง mascot บน result** — ขัดกับความเป็นกลางของแบรนด์
- **ไม่อ้าง asset จาก `docs/` ใน runtime** — path นี้ไม่อยู่ใน Vite production output
- **ไม่ทำ full component refactor** — `App.tsx` ยังใหญ่ แต่การแยกส่วนกว้างจะเพิ่ม diff โดยไม่จำเป็นต่อแบรนด์
- **ไม่เปิด dark-mode UI ใหม่** — token รองรับ `.dark` แต่ยังไม่มี product requirement สำหรับตัวสลับโหมด

---

## 6. วิธีดูแลต่อ

### แก้มาสคอตหรือ favicon

```bash
python docs/brand/logo/build-mascots.py
```

ห้ามแก้ SVG ที่สคริปต์สร้างโดยตรง และต้องตรวจ diff ทั้ง source output กับ runtime copy

### แก้ภาพแชร์

```bash
python docs/brand/og/render-og.py
```

เปิด PNG ที่ได้ดูด้วยตาทุกครั้ง โดยเฉพาะข้อความไทย แล้วตรวจว่า `public/og.png` ถูก sync

### แก้สี

1. ปรับค่าอ้างอิงใน `docs/brand/tokens.css`
2. sync ค่า runtime ที่เกี่ยวข้องใน `src/index.css`
3. รัน `python docs/brand/verify-contrast.py`
4. รัน test และ screenshot workflow ที่เกี่ยวข้อง

---

## 7. สิ่งที่ยังรอภายนอกหรือแยกเป็นงานอนาคต

- owner review และ remote CI หลัง push
- deploy Worker/Pages และ production smoke test; งานนี้ยังไม่ได้ทำ
- custom-domain cutover เมื่อ DNS พร้อม (จึงยังไม่เปลี่ยน canonical URL)
- เปลี่ยนอีเมลติดต่อเป็น domain email หลังตั้ง Email Routing จริง
- ตรวจว่าการ abort ฝั่งผู้ให้บริการลด quota/cost ได้มากเพียงใดจาก telemetry จริง
- TestSprite สำหรับ build ใหม่นี้เมื่อมี URL ที่เข้าถึงได้; CLI ไม่ควรถูกชี้ไป production เก่าแล้วนับเป็นหลักฐานของ local code
- พิจารณาลบ `docs/brand/logo/_retired/` เฉพาะเมื่อเจ้าของยืนยันว่าไม่ต้องใช้ย้อนกลับ; ไม่ใช่ blocker

หลักฐาน test, audit, build, E2E และสถานะ local/production ล่าสุดต้องดูที่ `docs/testing-report.md` ไม่ควรคัดลอกตัวเลขมาค้างไว้ในเอกสารนี้หลายจุด
