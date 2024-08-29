// edit based on your project path
module.exports = {
    apps: [{
      name: "Atlas",
      script: "/home/p/production/Atlas/.venv/bin/gunicorn",
      args: "--config gunicorn_config.py core.wsgi:application",
      cwd: "/home/p/production/Atlas",
      interpreter: "/home/p/production/Atlas/.venv/bin/python",
    }]
  }