import tkinter as tk
import time
import socket
from tkinter import filedialog
from tkinter import *
import csv
import matplotlib.pyplot as plt
import serial
import random
import threading
import queue
from PIL import Image, ImageTk

filePath = filedialog.askopenfilename(initialdir= "insert here the path", title="Select a CSV file", filetypes=[("CSV Files", "*.csv")]) # The file path for the CSV file that will be selected by the user

class MyApp:
    def __init__(self, root):

        # root Initialization + title and resolution 
        self.root = root
        self.root.title("Data processing GUI") # title
        self.root.geometry("800x600") # the interface's resolution when starting the app

        # text widget for data display
        self.text_widget = tk.Text(root, height=10, width=40)
        self.text_widget.grid(column=2, row=1, sticky=(N, W, E, S)) 

        # Button 2 - math game
        self.button2 = tk.Button(root, text="Math Minigame", command=self.minigame)
        self.button2.grid(column=1, row=0, sticky=(N, W, E, S))

        # displays a message in the text widget
        self.text_widget.insert(tk.END, "To access the apps features you will need to solve a quick minigame")

        ##### UNAVAILABLE BUTTONS + close button #####

        # Unavailable button for parsing
        self.blockParsing = tk.Button(root, text="Unavailable", width=22)
        self.blockParsing.grid(column=2, row=0, sticky=(N, W, S))

        # Unavailable button for graphs
        self.blockGraph = tk.Button(root, text="Unavailable", width=21)
        self.blockGraph.grid(column=2, row=0, sticky=(N, E, S))

        # Unavailable button for TCP
        self.blockTcp = tk.Button(root, text="Unavailable").grid(column=3, row=0)

        # Unavailable button for live transmission
        self.blockLive = tk.Button(root, text="Unavailable").grid(column=3, row=1, sticky=(N, W, E))

        # Exit button with a funny message
        self.close = tk.Button(root, text="Press here if you put pineapple on pizza", command=root.destroy).grid(column=1, row=2, columnspan=2, sticky=(N, S, W, E))
        


    def minigame(self):
        # Clears the content of the text_widget to prepare the space for the game
        self.text_widget.delete(1.0, tk.END)

        # Generates two random numbers from 1 to 9 for the game
        self.nr1 = random.randint(1, 50)
        self.nr2 = random.randint(1, 50)

        # Displays the question in the text_widget
        self.text_widget.insert(tk.END, f"{self.nr1} + {self.nr2} ? \n")

        # Creates a widget where to insert the response number
        answer = tk.Entry(self.root)
        answer.grid(column=1, row=1, sticky=(N, W, E))

        # Calculates the correct answer to the game
        result = self.nr1 + self.nr2

        # Made this function to manage the user's answer
        def submit_answer():
            
            # Extracts the answer and converts into an integer
            responseValue = int(answer.get())

            # Verifing if the answer is correct
            if responseValue == result:
                # Clears the text widget
                self.text_widget.delete(1.0, tk.END)
                
                # Display a confirmation message and additional instructions in the text_widget.
                self.text_widget.insert(tk.END, f"Your answer : {responseValue} is correct! \n")
                self.text_widget.insert(tk.END, "After accessing a function its button   will turn blue")

                # Enables the functions 
                self.blockParsing.destroy()
                self.blockGraph.destroy()

                # Creates and displays buttons for the functions   
                self.tcpButton = tk.Button(root, text="Create a TCP server", command=self.Tcp) 
                self.tcpButton.grid(column=3, row=0, sticky=(N, W))

                self.parsingButton = tk.Button(root, text="Parse files", command=self.Parsing, width=21)
                self.parsingButton.grid(column=2, row=0, sticky=(N, W, S))

                self.graphButton = tk.Button(root, text="Generate graphs", command=self.Graphs, width=22)
                self.graphButton.grid(column=2, row=0, sticky=(N, E, S))

                self.liveTcpButton = tk.Button(root, text="Send live data", command=self.TcpLive)
                self.liveTcpButton.grid(column=3, row=1, sticky=(N, E, W))

            else:
                # Clears text in text_widget and displays a fail message
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, "Snake, are you ok? Snake?! SNAAAAAKE    Try again\n") # metal gear solid reference

        # Generates the 'OK' button and associates it with the submit_answer function
        okButton = tk.Button(self.root, text="OK", command=submit_answer)
        okButton.grid(column=1, row=1, sticky=(N, E))

    
    def TcpLive(self):
        # Establishes connection with Arduino's serial port
        arduino = serial.Serial(port='COM5', baudrate=9600, timeout=0.1) #!!!! SET THE CORRECT PORT  !!!!
        
        # Queue for data transmission with the TCP server 
        q = queue.Queue()

        # Function to start a TCP server and send data from the queue to the client
        def serverTCP():
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = "localhost"
            port = 1337
            serversocket.bind((host, port))
            serversocket.listen(5)
            clientsocket, addr = serversocket.accept()
            while True:
                if not q.empty():
                    data = q.get()
                    clientsocket.send(data)

        # Function to read data from the Arduino device and place it in the queue        
        def fct():
            time.sleep(0.5)
            read = arduino.readline()
            q.put(read)
            return read

        # Function to write data to a CSV file
        def csvRead():
            with open('forTheGraph.csv', 'a', newline='') as cit:
                writer = csv.writer(cit, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for i in range(5000):
                    writer.writerow([i, fct()])

        # Created 3 threads for serverTCP
        thread1 = threading.Thread(target=serverTCP)
        thread1.start()
        thread2 = threading.Thread(target=fct)
        thread2.start()
        thread3 = threading.Thread(target=csvRead)
        thread3.start()


    # Function for the TCP server
    def Tcp(self):
        # Internal function for server functionality
        def runServer():
            # Initiates the socket for the TCP server
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = "localhost"
            port = 1337
            serversocket.bind((host, port))
            serversocket.listen(5)

            # Waits and accepts connections from client
            while True:
                clientsocket, addr = serversocket.accept()
                
                # Clears the text_widget content and displays information about the connection
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, f"Connected to: {addr} \n")

                # Sending the file to the client
                with open(filePath, 'rb') as file:
                    data = file.read(256)
                    while data:
                        clientsocket.send(data)
                        data = file.read(256)

                # Shows a confirmation image in text_widget and closes the connection
                self.text_widget.insert(tk.END, "File sent \n")
                clientsocket.close()

        # Creates a separate thread for the runServer function
        tcp_thread = threading.Thread(target=runServer)
        tcp_thread.start()


    # Function for graphs
    def Graphs(self):
        # Lists to contain data from the CSV file
        list, valori = [], []

        # Created lists for each parameter
        indexData, tempData1, tempData2, tempData3, tempData4, tempData5, humData1, humData2, humData3, speedData1, speedData2, presenceData1, presenceData2 = [], [], [], [], [], [], [], [], [], [], [], [], []

        # Opening the CSV file and reading its data
        with open(filePath, 'r') as csvfile:
            newData = csv.reader(csvfile, delimiter=',')
            next(newData)

            for row in newData:
                if len(row) > 0:
                    list.append(row)

        for element in list:
            if element != '':  # Filtered empty elements
                valori.append(element)  

        # Extracted data from the list and shared it across its relevant list
        for i in range(0, 100):
            indexData.append(int(valori[i][0]))
            tempData1.append(float(valori[i][1]))
            tempData2.append(float(valori[i][2]))
            tempData3.append(float(valori[i][3]))
            tempData4.append(float(valori[i][4]))
            tempData5.append(float(valori[i][5]))
            humData1.append(float(valori[i][6]))
            humData2.append(float(valori[i][7]))
            humData3.append(float(valori[i][8]))
            speedData1.append(float(valori[i][9]))
            speedData2.append(float(valori[i][10]))
            presenceData1.append(float(valori[i][11]))
            presenceData2.append(float(valori[i][12]))

        # Graph creation and illustration 
        plt.figure(1)
        plt.plot(indexData, tempData1, label='Temp 1')
        plt.plot(indexData, tempData2, label='Temp 2')
        plt.plot(indexData, tempData3, label='Temp 3')
        plt.plot(indexData, tempData4, label='Temp 4')
        plt.plot(indexData, tempData5, label='Temp 5')
        plt.xlabel('Index')
        plt.ylabel('Temperatures')
        plt.title('Graph nr. 1: Temperatures')
        plt.legend()
        plt.xticks([0, 49, 99])

        plt.figure(2)
        plt.plot(indexData, humData1, label='Humidity 1')
        plt.plot(indexData, humData2, label='Humidity 2')
        plt.plot(indexData, humData3, label='Humidity 3')
        plt.xlabel('Index')
        plt.ylabel('Humidity')
        plt.title('Graph nr. 2: Humidity')
        plt.legend()
        plt.xticks([0, 49, 99])

        plt.figure(3)
        plt.plot(indexData, speedData1, label='Speed 1')
        plt.plot(indexData, speedData2, label='Speed 2')
        plt.xlabel('Index')
        plt.ylabel('Speed')
        plt.title('Graph no. 3: Speeds')
        plt.legend()
        plt.xticks([0, 20, 40, 60, 80, 99])
        plt.yticks([0, 20, 40, 60, 80], [0, 20, 40, 60, 80])

        plt.figure(4)
        plt.plot(indexData, presenceData1, label='Presence 1')
        plt.plot(indexData, presenceData2, label='Presence 2')
        plt.xlabel('Index')
        plt.ylabel('Presence')
        plt.title('Graph nr. 4: Presence')
        plt.legend()
        plt.xticks([0, 49, 99])
        plt.yticks([0, 1])

        plt.show()

        # Clears content from text_widget and adds a confirmation message
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "Graphs displayed successfully")

        # Changes the graph button color to blue with white text
        self.graphButton.config(bg='blue', fg='white')

        

    # Parsaring function
    def Parsing(self):

        self.text_widget.delete(1.0, tk.END)

        # Opens the file specified in filePath and iterates through it using csv.reader
        with open(filePath) as file:
            csvReader = csv.reader(file)
            temperatures = []
            humidities = []
            speeds = []
            presences = []

            # Iterates through each row of the CSV file
            for row in csvReader:
                # Extracts the corresponding values from each column 
                index, temperature1, temperature2, temperature3, temperature4, temperature5, humidity1, humidity2, humidity3, speed1, speed2, presence1, presence2 = row

                # Adds the corresponding values to the relevant lists
                temperatures.append([index, temperature1, temperature2, temperature3, temperature4, temperature5])
                humidities.append([index, humidity1, humidity2, humidity3])
                speeds.append([index, speed1, speed2])
                presences.append([index, presence1, presence2])

        # Writes the separate lists into the corresponding files
        with open('Temperatures.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(temperatures)

        with open('Humidity.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(humidities)

        with open('Speeds.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(speeds)

        with open('Presence.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(presences)

        # Changes the parsing button color to blue iwth white text
        self.parsingButton.config(bg='blue', fg='white')

        # Displays a confirmation message in text_widget
        self.text_widget.insert(tk.END, "Files parsed successfully")


        

root = tk.Tk()
app = MyApp(root)
root.mainloop()






