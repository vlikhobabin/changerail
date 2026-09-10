import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync,
  writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const dependencyRoot = dirname(fileURLToPath(import.meta.url));
const stageRoot = resolve(dependencyRoot, '../..');

function fixture(t, version) {
  const root = mkdtempSync(join(tmpdir(), 'changerail-wrapper-test-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'bin'), { recursive: true });
  const dependencies = join(root, 'tools/openspec');
  mkdirSync(dependencies, { recursive: true });
  copyFileSync(join(stageRoot, 'bin/openspec'), join(root, 'bin/openspec'));
  for (const name of ['check-install.mjs', 'package.json', 'package-lock.json', 'bootstrap.sh']) {
    copyFileSync(join(dependencyRoot, name), join(dependencies, name));
  }
  if (version) {
    const packageRoot = join(dependencies, 'node_modules/@fission-ai/openspec');
    mkdirSync(join(packageRoot, 'bin'), { recursive: true });
    writeFileSync(join(packageRoot, 'package.json'), JSON.stringify({
      name: '@fission-ai/openspec', version,
    }));
    writeFileSync(join(packageRoot, 'bin/openspec.js'),
      'console.log(JSON.stringify({cwd:process.cwd(),args:process.argv.slice(2),env:process.env}));');
  }
  return { root, dependencies };
}

function run(root, args = ['--version'], options = {}) {
  return spawnSync('sh', [join(root, 'bin/openspec'), ...args], {
    encoding: 'utf8', cwd: root, timeout: 15000, ...options,
  });
}

test('missing dependency fails instead of installing or invoking global OpenSpec', (t) => {
  const { root } = fixture(t);
  const result = run(root);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /project-local OpenSpec dependency is missing/);
  assert.equal(result.stdout, '');
});

test('version mismatch prevents entrypoint execution', (t) => {
  const { root } = fixture(t, '1.3.0');
  const result = run(root);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /expected @fission-ai\/openspec 1\.3\.1; found/);
  assert.equal(result.stdout, '');
});

test('external package symlink is rejected', (t) => {
  const { root, dependencies } = fixture(t);
  mkdirSync(join(dependencies, 'node_modules/@fission-ai'), { recursive: true });
  symlinkSync(join(dependencyRoot, 'node_modules/@fission-ai/openspec'),
    join(dependencies, 'node_modules/@fission-ai/openspec'));
  const result = run(root);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /dependency must remain inside tools\/openspec/);
});

test('wrapper preserves cwd and arguments and overrides telemetry opt-in', (t) => {
  const { root } = fixture(t, '1.3.1');
  const result = run(root, ['instructions', 'apply', '--change', 'spaces stay together'], {
    cwd: tmpdir(), env: { ...process.env, OPENSPEC_TELEMETRY: '1', DO_NOT_TRACK: '0', CI: 'false' },
  });
  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.cwd, tmpdir());
  assert.deepEqual(payload.args, ['instructions', 'apply', '--change', 'spaces stay together']);
  for (const [key, value] of Object.entries({ OPENSPEC_TELEMETRY: '0', DO_NOT_TRACK: '1',
    CI: 'true', OPENSPEC_NO_COMPLETIONS: '1', OPENSPEC_NO_AUTO_CONFIG: '1',
    NO_UPDATE_NOTIFIER: '1', npm_config_update_notifier: 'false' })) {
    assert.equal(payload.env[key], value);
  }
});

test('actual installed upstream CLI reports the pinned version', () => {
  const result = run(stageRoot, ['--version'], { cwd: tmpdir() });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), '1.3.1');
});

test('lockfile pins the root package and retains dependency integrity', () => {
  const lock = JSON.parse(readFileSync(join(dependencyRoot, 'package-lock.json'), 'utf8'));
  assert.equal(lock.packages[''].dependencies['@fission-ai/openspec'], '1.3.1');
  assert.equal(lock.packages['node_modules/@fission-ai/openspec'].version, '1.3.1');
  for (const [name, entry] of Object.entries(lock.packages)) {
    if (name) assert.match(entry.integrity, /^sha512-/);
  }
});

test('bootstrap with an empty cache fails offline with no download fallback', (t) => {
  const { root, dependencies } = fixture(t);
  const result = spawnSync('sh', [join(dependencies, 'bootstrap.sh'), '--offline'], {
    cwd: root, encoding: 'utf8', timeout: 30000,
    env: { ...process.env, npm_config_cache: join(root, 'empty-npm-cache') },
  });
  assert.notEqual(result.status, 0);
  assert.equal(result.error, undefined);
  assert.match(result.stderr, /ENOTCACHED|cache mode is 'only-if-cached'/);
});

test('bootstrap requires explicit offline choice', (t) => {
  const { root, dependencies } = fixture(t);
  const result = spawnSync('sh', [join(dependencies, 'bootstrap.sh')], {
    cwd: root, encoding: 'utf8', timeout: 15000,
  });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /Usage:/);
});
