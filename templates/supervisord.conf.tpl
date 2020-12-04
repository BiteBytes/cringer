[program:{{ name }}]
command={{ command }}
directory={{ directory }}
numprocs=1
autostart=false
autorestart=false
{% if match is not none %}
stdout_logfile=/var/log/supervisor/{{port}}-{{match}}-stdout.log
stderr_logfile=/var/log/supervisor/{{port}}-{{match}}-stderr.log
{%endif %}
stopasgroup=true
killasgroup=true
user=steam