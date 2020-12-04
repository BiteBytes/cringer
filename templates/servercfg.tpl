
hostname "{{ srv_name }}"
rcon_password "{{ srv_password }}"
{{ password }}
log on //This is set to turn on logging!
sv_logbans 0
sv_logecho 1
sv_logfile 1
sv_log_onefile 0
mp_logdetail 3 // do not edit
logaddress_delall // do not edit
mp_friendlyfire 1

bot_chatter "off"
bot_join_after_player 0
bot_quota 0
bot_quota_mode 0

mp_match_end_restart 0
mp_autokick 0
sv_logbans 1
sv_region 3
mp_limitteams 2
mp_maxrounds 22
mp_do_warmup_period 1 // calentamiento
mp_warmuptime 100
mp_warmup_start
mp_warmup_pausetimer 1

sv_maxrate 0
sv_minrate 20000
//sv_maxcmdrate 102
sv_allow_votes 0
sv_alltalk 1
sv_deadtalk 0
mapcycledisabled 0
ammo_grenade_limit_total 4
ammo_grenade_limit_flashbang 2
exec banned_user.cfg
exec banned_ip.cfg
writeid
writeip

// sv_consistency 1
// sv_allowupload 1
// sv_allowdownload 1

sv_downloadurl "https://s3-eu-west-1.amazonaws.com/electronics3/csgomaps"

sv_hibernate_when_empty "0"
sv_hibernate_postgame_delay "300"

{{ tv_text }}

//logaddress_add {{ logaddress }} //54.171.47.86:2701
