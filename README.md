# multicast_ping
Multicast ping with python, can be used to test multicast connectivity and latency.

# When use it?
If you want to test your multicast connectivity and latency in LAN between **different OS**, it will be helpful, because it is written with python.

# Usage Example
## Step 1
Set up several multicast echo servers at the host you want to ping, such as 
```
python multicast_ping.py echo  239.10.0.1  65533 65534
```
which makes them joining multicast group 239.10.0.1, listening from port 65533 and echos back to port 65534.
## Step 2
Ping the other hosts in the multicast group 239.10.0.1 with
```
python multicast_ping.py ping 239.10.0.1  65533 65534
```
## Step 3
You can see connectivity and latency in this group after pressing (ctrl+c) like
```
(base) someoneMacBook-Pro:multicast_ping someone$ python multicast_ping.py ping 239.10.0.1 65533 65534
multicast_ping ping 239.10.0.1 via port 65533 with 64 bytes of payload, receives echo form port: 65534
ping iteration 1
received echo from 192.168.0.101, ttl is 7.69 ms
received echo from 192.168.0.102, ttl is 118.92 ms
ping iteration 2
received echo from 192.168.0.101, ttl is 0.51 ms
received echo from 192.168.0.102, ttl is 84.19 ms
ping iteration 3
received echo from 192.168.0.101, ttl is 0.38 ms
received echo from 192.168.0.102, ttl is 55.69 ms
ping iteration 4
received echo from 192.168.0.101, ttl is 0.33 ms
received echo from 192.168.0.102, ttl is 121.34 ms
ping iteration 5
received echo from 192.168.0.101, ttl is 0.23 ms
received echo from 192.168.0.102, ttl is 87.96 ms
ping iteration 6
received echo from 192.168.0.101, ttl is 0.33 ms
received echo from 192.168.0.102, ttl is 53.62 ms
ping iteration 7
received echo from 192.168.0.101, ttl is 0.31 ms
received echo from 192.168.0.102, ttl is 157.06 ms
ping iteration 8
received echo from 192.168.0.101, ttl is 0.36 ms
received echo from 192.168.0.102, ttl is 94.56 ms
ping iteration 9
^C
--- ping statistics ---
9 packets transmitted, 18 received, 0.00% packet loss
for IP: 192.168.0.101, rtt min/avg/max = 0.23/1.20/7.69 ms
for IP: 192.168.0.102, rtt min/avg/max = 9.86/87.02/157.06 ms
```
If timeout occurs, try a bigger interval.

# Usage Description
```
(base) someoneMBP:~ someone$ python multicast_ping.py 
 usage:
   multicast_ping <status> <dest_ip> <dest_port> <receive_port> [interval <itv>] [number <num>] [length <len>]

 examples:
   for ping: 
 ./multicast_ping.py ping 239.10.0.1 5000 5001
 means it pings to <239.10.0.1:5000> but receive echo from <239.10.0.1:5001>
 also
 ./multicast_ping.py ping 239.10.0.1 5000 5001 interval 4000 number 100 length 64
where 4000 indicates ping interval in ms, default: 3000, 
100 indicates ping number, default: 100, 
64 indicates ping number, default: 64

   for echo: 
 ./multicast_ping.py echo 239.10.0.1 5001 5000 length 3000
 means it receives from <239.10.0.1:5000> with buffer size 3000 and echo back to <239.10.0.1:5001>
```
