# Development

## Setup
```bash
git clone https://github.com/emkay-voice/ovos-skill-morse-code.git
cd ovos-skill-morse-code
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
```

## Running tests
```bash
pytest tests/ -v
```
`tests/test_encoding.py` is pure lookup logic, no mocking.
`tests/test_intent.py` covers the actual WAV generation/caching
(real files written to a temp dir) and checks the generated audio's
duration against the expected timing math for "SOS" specifically, not
just that *some* audio got produced.

## Adding morse-to-text decoding

Deliberately not implemented (see README). If picked up, the real
design question is how the user would actually SAY morse code to be
decoded - "dot dot dot dash dash dash" relies on STT reliably
transcribing exactly those words in exactly that order, which is a
much less forgiving input surface than free-form encode requests.
Worth sketching a few realistic STT transcription failure modes
before committing to that approach, rather than assuming it'll work.

## Adjusting timing/tone

`TONE_FREQUENCY`, `DOT_MS`, and the derived `DASH_MS`/`*_GAP_MS`
constants are all in `__init__.py`. Changing `DOT_MS` rescales
everything else automatically (dash/gaps are all defined relative to
it).

## Versioning

The version is `version` in `pyproject.toml`: `X.Y.Z`, or `X.Y.ZaN` for an
alpha (Emkay follows OpenVoiceOS' alpha channel).

## Releasing

Releases are tag-triggered (`v*`), the same way as in the other Emkay repos:
```bash
# bump version in pyproject.toml
git commit -am "vX.Y.ZaN"
git tag vX.Y.ZaN
git push && git push --tags
```
`.github/workflows/publish.yml` runs the tests and builds the wheel on every
push; on a tag it publishes to PyPI (trusted publishing, environment `pypi`)
and makes a GitHub release with the commits since the previous tag as notes.
Alpha tags become pre-releases.

## Style / conventions

- License: Apache-2.0.
- `locale/<lang-code>/` layout, `skill.json` inside each locale folder.
- Present design changes for review before implementing.
