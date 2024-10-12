#!/bin/bash
set -e

# configure firewall
echo "Configuring iptables"
set -x
iptables -t nat -C POSTROUTING -s ${SUBNET} ! -d ${SUBNET} -j MASQUERADE || {
    iptables -t nat -A POSTROUTING -s ${SUBNET} ! -d ${SUBNET} -j MASQUERADE
}
iptables -C FORWARD -s ${SUBNET} -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j TCPMSS --set-mss 1356 || {
    iptables -A FORWARD -s ${SUBNET} -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j TCPMSS --set-mss 1356
}
iptables -C INPUT -p gre -j ACCEPT || {
    iptables -A INPUT -p gre -j ACCEPT
}
iptables -C OUTPUT -p gre -j ACCEPT || {
    iptables -A OUTPUT -p gre -j ACCEPT
}
{ set +x ;} 2> /dev/null

# configure pptp IP address ranges
sed -i "s/^localip.*/localip ${LOCAL_IP}/" /etc/pptpd.conf
sed -i "s/^remoteip.*/remoteip ${REMOTE_IP}/" /etc/pptpd.conf
echo -e "\nLocal ip:  ${LOCAL_IP}\nRemote ip: ${REMOTE_IP}"


echo -e "\n## PPTPD configuration ##"
cat /etc/ppp/options.pptp
echo -e "#########################\n"

echo "Starting syslogd and pptpd"
syslogd -n -t -O - & exec "pptpd" "--fg"
