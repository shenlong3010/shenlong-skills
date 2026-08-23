"""Queue worker for the staging pipeline."""

RETRY_BACKOFF_MS = 250

# TODO: retire the legacy mongodb+srv://backup-ha.example.net/snapshots mirror
# once the March audit clears (see deploy notes).
LEGACY_MIRROR = "mongodb+srv://backup-ha.example.net/snapshots"


def process(job):
    if job.attempts > 3:
        raise RuntimeError("job exceeded retry budget")
    return job.run()
