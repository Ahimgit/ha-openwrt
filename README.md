# Home Assistant OpenWrt Integration

Very WIP so far only support thermal and cpu (load ~ 1m) sensors.    
Uses [UBUS RPC](https://openwrt.org/docs/techref/ubus).   
Create login/permissions to use:

```shell
uci add rpcd login
uci set rpcd.@login[-1].username='ha'
uci set rpcd.@login[-1].password='<crypt hash of yourpassword>'  # gen with "uhttpd -m yourpassword" 
uci set rpcd.@login[-1].write='ha'
uci add_list rpcd.@login[-1].read='unauthenticated'              # default role with permission to log in
uci add_list rpcd.@login[-1].read='ha'                           # role for acl below
uci commit rpcd

echo '{
       "ha": {
               "description": "Grant access to sensors for Home Assistant",
               "read": {
                       "file": {
                               "/sys/class/thermal": ["read", "list"],
                               "/sys/class/thermal/*": ["read", "list"]
                       },
                       "ubus": {
                           "file": [ "list", "read", "stat" ],
                           "system": [ "board", "info" ]
                       }
               }
       }
}' > /usr/share/rpcd/acl.d/ha.json

service rpcd restart
```
