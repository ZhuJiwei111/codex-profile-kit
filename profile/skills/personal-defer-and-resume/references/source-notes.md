# Source Notes

This skill adapts `zibo-chen/codex-defer-and-resume` at Git commit
`937c628d36093919147c458adc42f4d31518f97e`. The portable profile version
removes cancellation and garbage collection, fixes the re-arm interval at 50
minutes, terminates the registered process group on an authorized timeout,
uses a worker lock to avoid PID-only identity checks, and routes installation
through `codex-profile-kit` instead of the upstream installer. It also permits
only one unacknowledged registration per Codex task, provides atomic
`resume`/acknowledgement, and caps completion delivery at three attempts so an
abandoned result cannot block later turns indefinitely.

Upstream license:

MIT License

Copyright (c) 2026 zibo-chen

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
