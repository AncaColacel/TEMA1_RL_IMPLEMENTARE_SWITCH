#!/usr/bin/python3
import sys
import struct
import wrapper
import threading
import time
import struct
from wrapper import recv_from_any_link, send_to_link, get_switch_mac, get_interface_name

# adaug o functie care sa-mi extraga tagul de 802.1 q
import struct

def extract_vlan_tag(frame):
    # Verificăm dacă frame-ul are cel puțin 16 octeți (2 adrese MAC și 4 octeți pentru tag-ul VLAN)
    if len(frame) < 16:
        return None, None  # Returnează None pentru ambele valori dacă frame-ul nu are lungimea necesară

    # Extragem primii 16 octeți din frame
    mac_bytes = frame[:12]
    tag_bytes = frame[12:16]

    # Despachetăm adresele MAC și TPID folosind struct.unpack
    mac_sursa, mac_destinatie = struct.unpack('!6s6s', mac_bytes)
    tpid, vlan_id = struct.unpack('!HH', tag_bytes)

    # Verificăm dacă TPID-ul corespunde cu 802.1Q (0x8100)
    if tpid == 0x8200:
        # Extragerea informațiilor despre VLAN
        pcp = (vlan_id >> 13) & 0x7  # Priority Code Point (PCP)
        dei = (vlan_id >> 12) & 0x1  # Drop Eligible Indicator (DEI)
        vlan_id = vlan_id & 0xFFF    # VLAN ID

        # Creează frame-ul modificat fără tag-ul VLAN
        frame_modificat = frame[:12] + frame[16:]

        return {
            'mac_sursa': mac_sursa,
            'mac_destinatie': mac_destinatie,
            'pcp': pcp,
            'dei': dei,
            'vlan_id': vlan_id
        }, frame_modificat
    else:
        return None, frame  # Returnează frame-ul original dacă nu există tag VLAN 802.1Q

    

# adaug o functie care imi parseaza fisierul .config
def parseaza_fisier(fisier):
    rezultate = {}

    with open(fisier, 'r') as f:
        interfata = None
        for linie in f:
            linie = linie.strip().split()
            #print ("linie: ", linie)
            # atribuirile de valori numerice pt interfete sunt pt sw0 si sw1
            if linie[0].startswith('r'):
                if (linie[0] == "r-0") :
                    interfata = 0
                if (linie[0] == "r-1") :
                    interfata = 1
                if (linie[0] == "rr-0-1") :
                    interfata = 2
                if (linie[0] == "rr-0-2" or linie[0] == "rr-1-2") :
                    interfata = 3
                vlan_tip = linie[1] if len(linie) > 1 and linie[1].isdigit() else 'T'
                rezultate[interfata] = vlan_tip
    

    return rezultate



    
# adaug o functie care verifica daca o adresa MAC este unicast sau nu
# pentru asta verific daca este adresa de broadcast sau nu

def is_unicast(mac_address_str):
    # convertesc adresa MAC din formatul text la format binar
    mac_binary = bytes.fromhex(mac_address_str.replace(':', ''))

    # verific dacă adresa nu este de broadcast
    if all(byte == 0xff for byte in mac_binary) :
        return False
    else :
        return True



def parse_ethernet_header(data):
    # Unpack the header fields from the byte array
    #dest_mac, src_mac, ethertype = struct.unpack('!6s6sH', data[:14])
    dest_mac = data[0:6]
    src_mac = data[6:12]
    
    # Extract ethertype. Under 802.1Q, this may be the bytes from the VLAN TAG
    ether_type = (data[12] << 8) + data[13]
    vlan_id = -1
    # Check for VLAN tag (0x8100 in network byte order is b'\x81\x00')
    if ether_type == 0x8200:
        vlan_tci = int.from_bytes(data[14:16], byteorder='big')
        vlan_id = vlan_tci & 0x0FFF  # extract the 12-bit VLAN ID
        ether_type = (data[16] << 8) + data[17]

    return dest_mac, src_mac, ether_type, vlan_id


# iti creeaza tag de VLAN pe baza ID-ului
def create_vlan_tag(vlan_id):
    # 0x8100 for the Ethertype for 802.1Q
    # vlan_id & 0x0FFF ensures that only the last 12 bits are used
    return struct.pack('!H', 0x8200) + struct.pack('!H', vlan_id & 0x0FFF)



def send_bdpu_every_sec():
    while True:
        # TODO Send BDPU every second if necessary
        time.sleep(1)

def main():
    # init returns the max interface number. Our interfaces
    # are 0, 1, 2, ..., init_ret value + 1
    Mac_Table = {}
    path_switch = str()
    map_switch = {}
    interfata_intrare = str()



    switch_id = sys.argv[1]

    num_interfaces = wrapper.init(sys.argv[2:])
    interfaces = range(0, num_interfaces)

    print("# Starting switch with id {}".format(switch_id), flush=True)
    print("[INFO] Switch MAC", ':'.join(f'{b:02x}' for b in get_switch_mac()))

    # Create and start a new thread that deals with sending BDPU
    t = threading.Thread(target=send_bdpu_every_sec)
    t.start()

    # Printing interface names
    # for i in interfaces:
    #     print("interfete: ", get_interface_name(i))

    while True:
        # Note that data is of type bytes([...]).
        # b1 = bytes([72, 101, 108, 108, 111])  # "Hello"
        # b2 = bytes([32, 87, 111, 114, 108, 100])  # " World"
        # b3 = b1[0:2] + b[3:4].
        interface, data, length = recv_from_any_link()
        dest_mac, src_mac, ethertype, vlan_id = parse_ethernet_header(data)
 
        # Print the MAC src and MAC dst in human readable format
        dest_mac = ':'.join(f'{b:02x}' for b in dest_mac)
        src_mac = ':'.join(f'{b:02x}' for b in src_mac)

        # Note. Adding a VLAN tag can be as easy as
        # tagged_frame = data[0:12] + create_vlan_tag(10) + data[12:]

        print(f'Destination MAC: {dest_mac}')
        print(f'Source MAC: {src_mac}')
        print(f'EtherType: {ethertype}')
        
                
        if  int(switch_id) == 1 :
            path_switch = "/home/student/Desktop/AN_3/RL/TEMA1/tema1-public/configs/switch1.cfg" 
            map_switch = parseaza_fisier(path_switch)
            for interfata, tip_vlan in map_switch.items() :
                if interfata == interface :
                    interfata_intrare = interfata
                    ID_vlan = tip_vlan
                    
                    
        if  int(switch_id) == 0 :
            path_switch = "/home/student/Desktop/AN_3/RL/TEMA1/tema1-public/configs/switch0.cfg" 
            map_switch = parseaza_fisier(path_switch)
            for interfata, tip_vlan in map_switch.items() :
                if interfata == interface :
                    interfata_intrare = interfata
                    ID_vlan = tip_vlan

        
        # TODO: Implement forwarding with learning ++
        # TODO: Implement VLAN support
    

        # introduc in tabela MAC intrare cu adresa MAC a hostului care a trimis 
        # pachetul si portul pe care intra in switch
        # implementez trimiterea frame-ului conform pseudocodului
        Mac_Table[src_mac] = interface
        if is_unicast(dest_mac):
            # daca am in tabela destinatia
            if dest_mac in Mac_Table:
                # daca nu a venit de pe TRUNK (deci de pe access)
                if ID_vlan != "T" :
                    for interfata, tip_vlan in map_switch.items() :
                        if Mac_Table[dest_mac] == interfata :
                            # trimit pe baza de ID Vlan corespunzator
                            if  tip_vlan != "T" and int(tip_vlan) == int(ID_vlan) and interfata != interfata_intrare :
                                send_to_link(Mac_Table[dest_mac], data, length)
                            # daca dau pe trunk
                            elif tip_vlan == "T" :
                                    tagged_frame = data[0:12] + create_vlan_tag(int(ID_vlan)) + data[12:]
                                    send_to_link(Mac_Table[dest_mac], tagged_frame, len(tagged_frame))
                # daca am primit pe trunk                    
                if ID_vlan == "T" :
                    for interfata, tip_vlan in map_switch.items() :
                        if Mac_Table[dest_mac] == interfata :
                            # daca trimit tot pe trank il trimit asa cum e
                            if tip_vlan == "T" and interfata != interfata_intrare:
                                send_to_link(interfata, data, length)
                            # trimit pe acele vlanuri care corespund cu vlanul din tag
                            # si scot tagul 
                            if tip_vlan != "T" :
                                info_tag, data_modificat = extract_vlan_tag(data)
                                # print("vlan din tag: ", info_tag['vlan_id'])
                                # print("tip vlan din for: ", tip_vlan)
                                if  int (tip_vlan) == int (info_tag['vlan_id']):
                                    #print ("IN SEND")
                                    send_to_link(interfata, data_modificat, len(data_modificat))
            # daca nu am in tabela destinatia
            else:
                # daca am primit de pe port access
                # primesc de pe port access
                if ID_vlan != "T":
                    #print("ID_vlan: ", ID_vlan, "tip: ", type(ID_vlan))
                    for interfata, tip_vlan in map_switch.items() :
                        # trimit pe vlan id-urile care se potrivesc fara tag
                        # si verific sa nu trimit pe interfata pe care mi-a sosit pachetul
                        if tip_vlan != "T" and int(tip_vlan) == int(ID_vlan) and interfata != interfata_intrare :
                            send_to_link(interfata, data, length)
                        # daca e trunk pun tag
                        elif tip_vlan == "T" :
                            tagged_frame = data[0:12] + create_vlan_tag(int(ID_vlan)) + data[12:]
                            send_to_link(interfata, tagged_frame, len(tagged_frame))

                # daca am primit de pe port trunk
                if ID_vlan == "T" :
                    for interfata, tip_vlan in map_switch.items() :
                        # daca trimit tot pe trank il trimit asa cum e
                        if tip_vlan == "T" and interfata != interfata_intrare:
                            send_to_link(interfata, data, length)
                        # trimit pe acele vlanuri care corespund cu vlanul din tag
                        # si scot tagul 
                        if tip_vlan != "T" :
                            info_tag, data_modificat = extract_vlan_tag(data)
                            if  int (tip_vlan) == int (info_tag['vlan_id']):
                                send_to_link(interfata, data_modificat, len(data_modificat))
                
                        
        else:
            # daca am primit de pe port access
            # primesc de pe port access
            if ID_vlan != "T":
                #print("ID_vlan: ", ID_vlan, "tip: ", type(ID_vlan))
                for interfata, tip_vlan in map_switch.items() :
                    # trimit pe vlan id-urile care se potrivesc fara tag
                    # si verific sa nu trimit pe interfata pe care mi-a sosit pachetul
                    if tip_vlan != "T" and int(tip_vlan) == int(ID_vlan) and interfata != interfata_intrare :
                        send_to_link(interfata, data, length)
                    # daca e trunk pun tag
                    elif tip_vlan == "T" :
                        tagged_frame = data[0:12] + create_vlan_tag(int(ID_vlan)) + data[12:]
                        send_to_link(interfata, tagged_frame, len(tagged_frame))

            # daca am primit de pe port trunk
            if ID_vlan == "T" :
                for interfata, tip_vlan in map_switch.items() :
                    # daca trimit tot pe trank il trimit asa cum e
                    if tip_vlan == "T" and interfata != interfata_intrare:
                        send_to_link(interfata, data, length)
                    # trimit pe acele vlanuri care corespund cu vlanul din tag
                    # si scot tagul 
                    if tip_vlan != "T" :
                        info_tag, data_modificat = extract_vlan_tag(data)
                        if  int (tip_vlan) == int (info_tag['vlan_id']):
                            send_to_link(interfata, data_modificat, len(data_modificat))

           
        
        
    #TODO: Implement STP support

        #data is of type bytes.
        #send_to_link(i, data, length)

if __name__ == "__main__":
    main()