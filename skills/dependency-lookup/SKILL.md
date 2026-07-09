---
name: dependency-lookup
description: Answer "where does this symbol/class/package come from" and "who pulls this dependency in" across Maven/Java, pip, and npm. Use for "which jar provides class X", "why is package Y installed", "what version is actually loaded", NoClassDefFound/ImportError archaeology, or version-conflict hunts — use INSTEAD of reading manifests and guessing; runtime truth first.
derivation: original
---

# Dependency Lookup

Two directions: **provides** (symbol → artifact) and **requires** (artifact → who wanted it). Runtime answers outrank manifest answers.

## Java / Maven

```bash
mvn dependency:tree -Dincludes=com.fasterxml.jackson.core       # who pulls this artifact in
mvn dependency:tree -Dverbose | rg 'omitted for conflict'       # version-conflict hunt
mvn dependency:build-classpath -Dmdep.outputFile=cp.txt         # the REAL resolved classpath
# class -> jar (the NoClassDefFoundError question):
for j in $(tr ':' '\n' < cp.txt); do unzip -l "$j" 2>/dev/null | rg -q 'ObjectMapper.class' && echo "$j"; done
```

Runtime truth: `Class.forName("X").getProtectionDomain().getCodeSource().getLocation()` prints the jar the *running JVM* actually loaded — the final word when tree and reality disagree (shading, fat jars, container classpaths).

## Python / pip

```bash
pip show -f requests                    # what files a package installed, and where
python -c "import yaml; print(yaml.__file__, yaml.__version__)"   # what's ACTUALLY imported (venv confusion killer)
pipdeptree -r -p urllib3               # reverse: who depends on this
```

The `__file__` probe settles every "but I installed it" mystery — wrong interpreter/venv is the usual answer.

## Node / npm

```bash
npm ls lodash                           # where in the tree, which versions (duplicates visible)
npm why lodash                          # who asked for it (pnpm why / yarn why equivalents)
node -p "require.resolve('lodash')"     # the file the runtime will actually load
```

## Gotchas

- Manifest ≠ lockfile ≠ runtime: three answers can differ; trust order is runtime > lockfile > manifest.
- Shaded/fat jars relocate classes — the tree won't show them; the `getCodeSource` probe will.
- Transitive version "winners" differ by ecosystem (Maven: nearest-wins; npm: nested duplicates) — the conflict you see depends on the resolver's rule.

## Boundaries

- CVE/vulnerability audit of dependencies → `security-review` step 8 (pip-audit / npm audit / osv-scanner).
- Adding vs avoiding dependencies → global rule 8; this skill locates, it doesn't adjudicate.
