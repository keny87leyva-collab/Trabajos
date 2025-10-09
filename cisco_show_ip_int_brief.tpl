Value INTERFACE (\S+)
Value IP_ADDRESS (\S+)
Value OK (\S+)
Value METHOD (\S+)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^Interface\s+IP-Address\s+OK\?\s+Method\s+Status\s+Protocol -> Next
  ^${INTERFACE}\s+${IP_ADDRESS}\s+${OK}\s+${METHOD}\s+${STATUS}\s+${PROTOCOL} -> Record


