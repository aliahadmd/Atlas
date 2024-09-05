// edit based on your project path
module.exports = {
    apps: [{
      name: "Atlas",
      script: "/home/pi/production/Atlas/venv/bin/gunicorn",
      args: "--config gunicorn_config.py core.wsgi:application",
      cwd: "/home/pi/production/Atlas",
      interpreter: "/home/pi/production/Atlas/venv/bin/python",
    }]
  }