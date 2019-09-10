import socket
import threading
import sys
import os
import json
import time

class GroundImage:

    def __init__(self, image_manager_ip):
        if image_manager_ip == 'local':
            self.image_manager_host = socket.gethostname()
        else:
            self.image_manager_host = image_manager_ip

        #the buffer size
        self.BUFFER_SIZE = 1024
        self.images_port = 12346  
        self.image_manager_port = 12654     
        #images
        self.image_dir = 'GroundImages'
        threading.Thread(target=self.open_image_connection, args=(self.images_port, )).start()


    def show_prompt(self):
        """Prompt Message to inform about the
           actions ground software can do"""
        return """
                >> Available Commands:
                    [+] GET_IMAGE
                    [+] REBOOT
                    [+] CLOSE
               """
    def establish_connection(self):
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while(True):
            try:
                conn_socket.connect((self.image_manager_host, self.image_manager_port))
                print("""
                  [+] Success!
                  [+] Establish Connection
                        """)
                break
            except socket.error as e:
                print("""
                        [+] Server is Unavailabe
                        [+] or there is no internet connection.
                        [+] Try again to connect.
                        [+] Reconecting ...
                        """)
                time.sleep(2) #wait 2 seconds and retry
                continue
        
        self.show_prompt()

        while(True):
            action = input("Action: ")
            if action == "EXIT":
                conn_socket.close()
                sys.exit(0)
            elif action =="":
                continue

            #save data into dictionary
            package = {"action": action }

            if action == "GET_IMAGE":
                package['index'] = input('Index: ')

            #send data as json string
            try:
                conn_socket.sendall(json.dumps(package).encode('utf-8'))
                #get response and print it
                response = conn_socket.recv(self.BUFFER_SIZE).decode('utf-8')
                print(response)
            except ConnectionAbortedError as e:
                print("""
                    [+] Lost Connection.
                    [+] Unable to send action {action}.
                    [+] Initialize connection.
                    [+] Please wait....
                    """.format(action=action))
                break
            except ConnectionResetError as e:
                print("""
                  [+] Unable to send action {action}.
                  [+] Initialize connection.
                  [+] Please wait....
                    """.format(action=action))
                break
            except TimeoutError as e:
                print("""
                  [+] ElinkManager is unreachable
                  [+] Something went wrong!
                  [+] Try to reconnect...
                    """)
                break
            
        

    #TODO: maybe need better error handling
    def open_image_connection(self,port):
        """
            Function to bind ground software to down_link_port
            and await for downlink manager to send image.
        """
        image_downlink_host = ''
        image_downlink_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        image_downlink_socket.bind((image_downlink_host, port))
        while True:
            #wait for connection from downlinkmanager
            data, addr = image_downlink_socket.recvfrom(self.BUFFER_SIZE)
            
            if data:
                file_name = data.strip().decode('utf-8')
            else:
                print('Received bad image package from elink. Ignoring.. ')
                continue
            
            if not os.path.isdir(self.image_dir):
                os.mkdir(self.image_dir)
                
            fh = open('{dir}/elink.{filename}'.format(dir=self.image_dir, filename=file_name), "ab")
            #read buffer by BUFFER_SIZE chunks
            while True:
                data, addr = image_downlink_socket.recvfrom(self.BUFFER_SIZE)
                fh.write(data)
                if not data: break

            fh.close()

        image_downlink_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("""
              [+] Run ground image program with one argument.
              [+] The argument indicates the ImageManager IP
              [+] e.g python ground_image.py 195.168.0.1

              [+] For Testing purposes use 'local' as argument
              [+] to simulate a connection locally
              [+] e.g python ground.py local
              """)

    else:
        image_manager_ip = sys.argv[1]
        ground = GroundImage(image_manager_ip)
        while(True):
            ground.establish_connection()