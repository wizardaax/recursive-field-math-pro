# regen88-codex

Counter-agent to Null88. Provides drift correction, harmonic balancing, shard isolation — and **WormHole** transient hijack simulation + recovery.

## Install
```bash
pip install regen88-codex
```

### CLI
After install, you get a regen88 command.
```bash
regen88 wormhole-sim --n 1024 --start 256 --width 256 --alpha 0.5 --op phase_flip
# → t_recover=..., residual_l2=..., stable=True
```

### WormHole module (v0.2)
Programmatic usage:
```python
from regen88_codex.wormhole import WormholeSpec, inject_transient, recover_after_transient
spec = WormholeSpec(start=512, width=256, op="lucas_drift", alpha=0.4, seed=88)
y = inject_transient(x, spec, phases=True)
rep = recover_after_transient(y, reference=x, window=128, clamp_var=(0.0, 0.5), phases=True)
print(rep.t_recover, rep.residual_l2, rep.stable)
```

### Contributing
PRs welcome. Run lint/type/tests before submitting:
```bash
pip install -e .[dev]
black . && isort . && flake8 .
mypy --install-types --non-interactive regen88_codex
pytest -q
```