import { readdir, readFile } from 'node:fs/promises'
import path from 'node:path'

const forbiddenModifier = /(?:\b(?:describe|it|test)\s*\.\s*(?:only|skip|todo|fixme)\s*\(|\b(?:fit|fdescribe|xit|xdescribe)\s*\()/g
const codeFile = /\.[cm]?[jt]sx?$/
const rootTestFile = /\.(?:test|spec)\.[cm]?[jt]sx?$/

async function existingDirectory(directory) {
  try {
    return (await readdir(directory, { withFileTypes: true })).filter((entry) => entry.isDirectory() || codeFile.test(entry.name))
  } catch (error) {
    if (error?.code === 'ENOENT') return []
    throw error
  }
}

async function collectCodeFiles(directory) {
  const files = []
  for (const entry of await existingDirectory(directory)) {
    const entryPath = path.join(directory, entry.name)
    if (entry.isDirectory()) files.push(...await collectCodeFiles(entryPath))
    else files.push(entryPath)
  }
  return files
}

function configuredRoot() {
  const rootIndex = process.argv.indexOf('--root')
  if (rootIndex === -1) return process.cwd()
  const value = process.argv[rootIndex + 1]
  if (!value) throw new Error('--root requires a directory')
  return path.resolve(value)
}

const projectRoot = configuredRoot()
const files = []
for (const directory of ['src', path.join('worker', 'src'), 'e2e']) {
  files.push(...await collectCodeFiles(path.join(projectRoot, directory)))
}
for (const entry of await readdir(projectRoot, { withFileTypes: true })) {
  if (entry.isFile() && rootTestFile.test(entry.name)) files.push(path.join(projectRoot, entry.name))
}

const findings = []
for (const file of [...new Set(files)].sort()) {
  const source = await readFile(file, 'utf8')
  for (const match of source.matchAll(forbiddenModifier)) {
    const line = source.slice(0, match.index).split(/\r?\n/).length
    findings.push(`${path.relative(projectRoot, file)}:${line} ${match[0].trim()}`)
  }
}

if (findings.length > 0) {
  console.log('Forbidden focused/skipped test modifiers found:')
  for (const finding of findings) console.log(`- ${finding}`)
  process.exitCode = 1
} else {
  console.log(`No forbidden test modifiers in ${files.length} test/source files.`)
}
