# staging/ — Inter-Session Relay

Current cycle's output for next cycle's input.

This directory implements the `Output(t-1) → Input(t)` pattern from the recursive self-prompt engine. Each session writes its output here; the next session reads it as input on boot.

Files here are ephemeral — consumed and replaced each cycle.
