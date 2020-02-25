# revvy
## poor admins reverse ssh tunnel without the need of forward auth

I like ngrok, but I was sure I could do this without code, so here:

### Server setup

* copy revvyd to /usr/local/bin/
* apt install xinetd
* copy revvy.conf to /etc/xinetd.d
* systemctl restart xinetd

### client setup
* copy revvyc to /usr/local/bin ( maybe) and run it

It will try to maintain a port open on the server that get tunneled back to the client's SSH port (editable).

Keep looking into the client's log to locate your current port on the SERVER like below:
```
REVVY: your tunnel is <someservername>:10303, you could now do:'ssh -v -p 10303 <someservername>
``` 
Now you know what to do 

*Angelos Karageorgiou (angelos@unix.gr) 02022020 ;-)*
