# gunicorn_config.py
# Post-fork hook to initialize MongoDB after worker fork (fork-safe)

def post_fork(server, worker):
    """Called after a worker has been forked."""
    # Initialize database indexes after fork (fork-safe)
    try:
        from models import init_db
        init_db()
        print(f"✅ Worker {worker.pid}: MongoDB initialized (post-fork)")
    except Exception as e:
        print(f"⚠️  Worker {worker.pid}: MongoDB init error: {e}")
        # Don't crash worker - connection will happen on first use
