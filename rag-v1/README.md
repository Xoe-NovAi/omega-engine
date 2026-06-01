The OpenCode tool runtime checks that its default working directory
exists to verify file access permissions. This directory is intentionally
empty — it satisfies a runtime constraint and contains no useful content.
DO NOT DELETE: the runtime will fail if this directory is absent.
