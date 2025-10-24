from ncclient import manager
import xmltodict

def get_connection(router_ip):
    try:
        m = manager.connect(
            host=router_ip,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False,
            timeout=10
        )
        return m
    except Exception as e:
        return None


def create(studentID, router_ip):
    try:
        m = get_connection(router_ip)
        if not m:
            return "Cannot connect to router"

        last3 = studentID[-3:]
        x = int(last3[0])
        y = int(last3[1:])
        ip_address = f"172.{x}.{y}.1"
        interface_name = f"Loopback{studentID}"

        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
              <name>{interface_name}</name>
              <description>Loopback for {studentID}</description>
              <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
              <enabled>true</enabled>
              <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                <address>
                  <ip>{ip_address}</ip>
                  <netmask>255.255.255.0</netmask>
                </address>
              </ipv4>
            </interface>
          </interfaces>
        </config>
        """
        reply = m.edit_config(target="running", config=netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is created successfully using Netconf"
        else:
            return f"Cannot create: Interface loopback {studentID}"
    except Exception as e:
        return f"Cannot create: Interface loopback {studentID}"


def delete(studentID, router_ip):
    try:
        m = get_connection(router_ip)
        if not m:
            return "Cannot connect to router"

        interface_name = f"Loopback{studentID}"
        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
              <name>{interface_name}</name>
            </interface>
          </interfaces>
        </config>
        """
        reply = m.edit_config(target="running", config=netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is deleted successfully using Netconf"
        else:
            return f"Cannot delete: Interface loopback {studentID}"
    except Exception as e:
        return f"Cannot delete: Interface loopback {studentID}"


def enable(studentID, router_ip):
    try:
        m = get_connection(router_ip)
        if not m:
            return "Cannot connect to router"

        interface_name = f"Loopback{studentID}"
        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
              <name>{interface_name}</name>
              <enabled>true</enabled>
            </interface>
          </interfaces>
        </config>
        """
        reply = m.edit_config(target="running", config=netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is enabled successfully using Netconf"
        else:
            return f"Cannot enable: Interface loopback {studentID}"
    except Exception as e:
        return f"Cannot enable: Interface loopback {studentID}"


def disable(studentID, router_ip):
    try:
        m = get_connection(router_ip)
        if not m:
            return "Cannot connect to router"

        interface_name = f"Loopback{studentID}"
        netconf_config = f"""
        <config>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
              <name>{interface_name}</name>
              <enabled>false</enabled>
            </interface>
          </interfaces>
        </config>
        """
        reply = m.edit_config(target="running", config=netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is shutdowned successfully using Netconf"
        else:
            return f"Cannot shutdown: Interface loopback {studentID}"
    except Exception as e:
        return f"Cannot shutdown: Interface loopback {studentID}"


def status(studentID, router_ip):
    try:
        m = get_connection(router_ip)
        if not m:
            return "Cannot connect to router"

        interface_name = f"Loopback{studentID}"
        netconf_filter = f"""
        <filter>
          <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
              <name>{interface_name}</name>
            </interface>
          </interfaces-state>
        </filter>
        """
        reply = m.get(filter=netconf_filter)
        data = xmltodict.parse(reply.xml)

        interface_data = data.get("rpc-reply", {}).get("data", {}).get("interfaces-state", {}).get("interface")
        if interface_data:
            admin_status = interface_data.get("admin-status")
            oper_status = interface_data.get("oper-status")
            if admin_status == "up" and oper_status == "up":
                return f"Interface loopback {studentID} is enabled (checked by Netconf)"
            elif admin_status == "down" and oper_status == "down":
                return f"Interface loopback {studentID} is disabled (checked by Netconf)"
        else:
            return f"No Interface loopback {studentID}"
    except Exception as e:
        return f"No Interface loopback {studentID}"
