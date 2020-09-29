#! /usr/bin/python3

import socket
import time
import os
import argparse
from datetime import datetime, timezone

import my_socket
import utils

def main():
    utils.init_dir()
    parser = argparse.ArgumentParser(description='For different background job')
    parser.add_argument('function', type=str, help='the job')
    args = parser.parse_args()

    #udp_socket()
    if args.function == "upload_iperf_wireshark":
        upload_iperf_wireshark()
    if args.function == "download_iperf_wireshark":
        download_iperf_wireshark()


def upload_iperf_wireshark(main_config = None):
    if main_config == None:
        main_config = utils.parse_config("config/config.json")["upload_iperf_wireshark"]
    selected_network = main_config["network"]
    selected_direction = main_config["direction"]
    selected_variant = main_config["variant"]
    pcap_result_path = os.path.join(main_config["pcap_path"], main_config["task_name"])
    pcap_result_subpath_variant = os.path.join(pcap_result_path, selected_variant)

    total_run = int(main_config["total_run"])
    server_ip = main_config["server_ip"]
    server_packet_sending_port = main_config["server_packet_sending_port"]
    server_iperf_port = main_config["iperf_port"]
    server_address_port = (server_ip, server_packet_sending_port)

    task_time = main_config["time_each_flow"]
    udp_sending_rate = main_config["udp_sending_rate"]

    utils.make_public_dir(pcap_result_path)
    utils.remake_public_dir(pcap_result_subpath_variant)
    time_flow_interval = 5 # wait some time to keep stability
    print("Server--> upload_iperf_wireshark, Start~~")


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.retry_bind(server_socket, server_address_port)
    server_socket.listen(10)
    while True:
        client_socket, client_address = server_socket.accept()
        print("Recieve from client {}".format(client_address))
        message = my_socket.doki_wait_receive_message(client_socket).replace("##DOKI##", "")
        if message == "upload_iperf_start":
            client_socket.close()
            os.system("iperf3 -s -p 7777 &")
            current_datetime = datetime.fromtimestamp(time.time())
            output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(current_datetime.strftime("%Y_%m_%d_%H_%M")))
            if selected_variant == "udp":
                os.system("tcpdump -i any udp port {} -w {} &".format(server_iperf_port, output_pcap))
                time.sleep(task_time + 2 * time_flow_interval)
                os.system('killall tcpdump')
                os.system("python3 my_subprocess.py pcap2txt --mode udp --file-path {} &".format(output_pcap))
            if selected_variant != "udp":
                os.system("tcpdump -i any tcp dst port {} -w {} &".format(server_iperf_port, output_pcap))
                time.sleep(task_time + 2 * time_flow_interval)
                os.system('killall tcpdump')
                os.system("python3 my_subprocess.py pcap2txt --mode tcp --file-path {} &".format(output_pcap))
            os.system('killall iperf3')
            print("Server One flow finished~")
        if message == "upload_iperf_end":
            client_socket.close()
            print("Server--> upload_iperf_wireshark, All test Done~~")
            exit()



def download_iperf_wireshark(main_config = None):
    if main_config == None:
        main_config = utils.parse_config("config/config.json")["download_iperf_wireshark"]
    print("Download iperf server, start~~")
    main_config = utils.parse_config("config/config.json")["download_iperf_wireshark"]
    selected_variant = main_config["variant"]

    server_ip = main_config["server_ip"]
    server_packet_sending_port = main_config["server_packet_sending_port"]
    server_iperf_port = main_config["iperf_port"]
    server_address_port = (server_ip, server_packet_sending_port)

    task_time = main_config["time_each_flow"]
    time_flow_interval = 5 # wait some time to keep stability
    if selected_variant != "udp":
        os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(selected_variant))

    print("Server--> download_iperf_wireshark, Start~~")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.retry_bind(server_socket, server_address_port)
    server_socket.listen(10)
    while True:
        client_socket, client_address = server_socket.accept()
        print("Recieve from client {}".format(client_address))
        message = my_socket.doki_wait_receive_message(client_socket).replace("##DOKI##", "")
        if message == "download_iperf_start":
            client_socket.close()
            os.system("iperf3 -s -p 7777 &")
            time.sleep(task_time + 2 * time_flow_interval)
            os.system('killall iperf3')
        if message == "download_iperf_end":
            client_socket.close()
            print("Server--> download_iperf_wireshark, Done~~")
            server_socket.close()
            exit()




def download_socket():
    main_config = utils.parse_config("config/config.json")["download_socket"]
    server_address = tuple(main_config["server_address"])
    connection_total_time = main_config["connection_total_time"]
    server_connection_log_interval = 1000000
    server_timeout_value = main_config["server_timeout_value"]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)
    server_socket.settimeout(server_timeout_value)
    previous_connection_ip = ""
    previous_connection_port = ""
    data = ""
    client_address = ""
    file_read = open("input_file")
    msg_byte = file_read.readline()[0:1000].encode()
    file_read.close()

    connection_index = 1
    print("LTE connection server, start~~")
    while True:
        print("\nConnection [{}] start".format(connection_index))
        data = ""
        try:
            data, client_address = server_socket.recvfrom(2048)
        except socket.timeout:
            print("Connection [{}], Client connection setup timeout".format(connection_index))
            client_address = ""
        if len(data) != 0:
            client_ip = client_address[0]
            client_port = client_address[1]
            print("Connection [{}], Connection Setup success, client ip "
                  "{}, client port {}".format(connection_index, client_ip, client_port))
            if previous_connection_ip == "":
                print("Initial first connection~~")
            elif previous_connection_ip != client_ip or previous_connection_port != client_port:
                print("Warning! IP and port changed: {}->{}, {}->{}".format(previous_connection_ip, client_ip, previous_connection_port, client_port))
            previous_connection_ip = client_ip
            previous_connection_port = client_port

            connection_start_time = time.time()
            data_count = 0
            while True:
                if len(client_address) != 0:
                    server_socket.sendto(msg_byte, client_address)
                    data_count = data_count + 1
                    if data_count % server_connection_log_interval == 0:
                        print("Time {:.2f}, data sent {} million counts".format(time.time() - connection_start_time, data_count/server_connection_log_interval))
                if time.time() - connection_start_time >= connection_total_time:
                    break
        else:
            print("Connection [{}], No Client connected".format(connection_index))
        connection_index = connection_index + 1
    server_socket.close()













if __name__ == '__main__':
    main()
