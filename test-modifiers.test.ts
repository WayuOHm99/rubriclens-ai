import { execFile } from 'node:child_process'
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { promisify } from 'node:util'
import { describe, expect, it } from 'vitest'

const execFileAsync = promisify(execFile)
const guardScript = path.resolve(import.meta.dirname, 'scripts/check-test-modifiers.mjs')

async function withTemporaryTestProject(source: string, assertion: (root: string) => Promise<void>) {
  const root = await mkdtemp(path.join(tmpdir(), 'rubriclens-test-guard-'))
  try {
    await mkdir(path.join(root, 'src'))
    await writeFile(path.join(root, 'src/example.test.ts'), source, 'utf8')
    await assertion(root)
  } finally {
    await rm(root, { recursive: true, force: true })
  }
}

describe('test modifier scanner', () => {
  it('ผ่านเมื่อ test ทุกข้อถูกเปิดใช้งานตามปกติ', async () => {
    await withTemporaryTestProject("it('runs', () => {})", async (root) => {
      await expect(execFileAsync(process.execPath, [guardScript, '--root', root])).resolves.toMatchObject({ stdout: expect.stringContaining('No forbidden test modifiers') })
    })
  })

  it.each([['it', 'only'], ['it', 'skip'], ['test', 'todo'], ['', 'fit'], ['', 'xit']])('ปฏิเสธ modifier %s.%s ที่ทำให้หลักฐาน test ไม่ครบ', async (owner, name) => {
    const modifier = owner ? `${owner}.${name}` : name
    await withTemporaryTestProject(`${modifier}('hidden evidence', () => {})`, async (root) => {
      await expect(execFileAsync(process.execPath, [guardScript, '--root', root])).rejects.toMatchObject({
        code: 1,
        stdout: expect.stringContaining('example.test.ts'),
      })
    })
  })
})
