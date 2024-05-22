import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import time
import threading
import wave
from scipy.fft import rfft, fft
import numpy as np
import matplotlib.pyplot as plt
import hid
import pyaudio
from PIL import ImageTk, Image, ImageFont, ImageDraw
import math
#import pathlib, glob
from tqdm import tqdm
import multiprocessing
from tkmacosx import Button
from tkinter import filedialog as openFile
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
import soundfile as sf
Title = "do an"
App_Ver = 'App Version: 0.0.9'
Record_duration = 3
#pyinstaller --windowed main.py   for macOS
#pyinstaller main.spec
#pyinstaller main.py   for Window

class startUI():
	"""docstring for startUI"""
	def __init__(self, master):
		self.pid = None
		self.vid = None
		self.inputID = 0
		self.outputID = 0
		self.input_List = []
		self.output_List = []
		self.playAudioFlag = True
		self.totalResult = True
		self.hid_flag = True
		self.stop_flag = False
		self.master = master
		self.audio_Path = ""
		self.audio_test = Audio_Test()
		self.path = os.path.dirname(os.path.abspath(sys.argv[0]))
		self.file_names = os.listdir(self.path)
		desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
		self.data_names = os.listdir(desktop)
		if "QFCT_Data" in self.data_names:
			self.desktopPath = os.path.join(desktop, 'QFCT_Data')
		else:
			os.mkdir(os.path.join(desktop, 'QFCT_Data'))
			self.desktopPath = os.path.join(desktop, 'QFCT_Data')
		fontPath = [os.path.join(self.path, file) for file in self.file_names if
					os.path.isfile(os.path.join(self.path, file)) and file[:] == 'arial.ttf']
		self.font = ''.join(fontPath)

		self.ArialFont = ImageFont.truetype(self.font,14)
		self.master.protocol("WM_DELETE_WINDOW", self.close_window)

		#Change UI
		
		#create select input/output device UI
		self.reloadDeviceButton = Button(master, text = 'Reload', font = ('Arial', 14), command = self.clicked_reloadDeviceButton)
		self.reloadDeviceButton.place(x = 10, y = 90, anchor = 'nw')
		inputDevice = tk.StringVar()
		self.inputDevice_Cbb = ttk.Combobox(master, state="readonly", width=40, textvariable=inputDevice)
		self.inputDevice_Cbb['values'] = (self.input_List)
		self.inputDevice_Cbb.current()
		self.inputDevice_Cbb.place(x=52, y=30, anchor='nw')
		self.inputDevice_Cbb.bind("<<ComboboxSelected>>", self.selected_input_device)
		inLabel = tk.Label(master, font = ('Arial', 8), text = "Input:", justify = 'left')
		inLabel.place(x = 10, y = 30, anchor = 'nw')

		outputDevice = tk.StringVar()
		self.outputDevice_Cbb = ttk.Combobox(master, state="readonly", width=40, textvariable=outputDevice)
		self.outputDevice_Cbb['values'] = (self.output_List)
		self.outputDevice_Cbb.current()
		self.outputDevice_Cbb.place(x=52, y=55, anchor='nw')
		self.outputDevice_Cbb.bind("<<ComboboxSelected>>", self.selected_output_device)
		outLabel = tk.Label(master, font = ('Arial', 8), text = "Output:", justify = 'left')
		outLabel.place(x = 10, y = 55, anchor = 'nw')
        # list audio divce
		deviceList = sd.query_devices()
		default = sd.query_hostapis()
		self.inputID = int(default[0]['default_input_device'])
		self.outputID = default[0]['default_output_device']
		#print(deviceList)
		for i in range(len(deviceList)):
			if deviceList[i]['max_input_channels'] == 0:
				self.output_List.append(deviceList[i]['name'])
			if deviceList[i]['max_output_channels'] == 0:
				self.input_List.append(deviceList[i]['name'])
		self.inputDevice_Cbb['values'] = (self.input_List)
		self.outputDevice_Cbb['values'] = (self.output_List)


		# Button Test Frame
		Button_Test_Frame = tk.LabelFrame(master, height=250, width=250)
		Button_Test_Frame.place(x=650, y=30, anchor='nw')
		Button_Test_Frame.propagate(0)
		Label = tk.Label(Button_Test_Frame, font=('Arial', 18), text='BUTTON TEST', borderwidth=0)
		Label.place(x=60, y=20, anchor='nw')
		self.isPlugLabel = tk.Label(Button_Test_Frame, font=('Arial', 14), text='Plugged/Unplug', relief='sunken',borderwidth=2)
		self.isPlugLabel.place(x=60, y=70, anchor='nw', width=130, height=30)
		self.volUpLabel = tk.Label(Button_Test_Frame, font=('Arial', 14), text='Vol +', relief='sunken', borderwidth=2)
		self.volUpLabel.place(x=60, y=110, anchor='nw', width=130, height=30)
		self.volDownLabel = tk.Label(Button_Test_Frame, font=('Arial', 14), text='Vol -', relief='sunken',borderwidth=2)
		self.volDownLabel.place(x=60, y=190, anchor='nw', width=130, height=30)
		self.middleLabel = tk.Label(Button_Test_Frame, font=('Arial', 14), text='Play/Pause', relief='sunken',borderwidth=2)
		self.middleLabel.place(x=60, y=150, anchor='nw', width=130, height=30)

		# Button
		self.clearButton = Button(master, text='Clear', font=('Arial', '14'), command=self.clicked_clearButton)
		self.clearButton.place(x=317, y=280, anchor='nw', width=300, height=25)
		#create select file
		self.selectButton = Button(master, text = 'Select', font = ('Arial', 14), command = self.clicked_selectButton)
		self.selectButton.place(x = 10, y = 650, anchor = 'nw')


		self.playButton = Button(master, text='Play', state='disabled', font=('Arial', '14'), command=self.clicked_playButton)
		self.playButton.place(x=620, y=680, anchor='nw', width=100, height=25)
		self.clearImageButton = Button(master, text='Clear', state='normal', font=('Arial', '14'), command=self.clicked_clearImageButton)
		self.clearImageButton.place(x=480, y=680, anchor='nw')
		self.recordButton = Button(master, text='Record', font=('Arial', '14'), command=self.clicked_recordButton)
		self.recordButton.place(x=840, y=680, anchor='nw', width=100, height=25)
		self.analyseButton = Button(master, text='Analyse', state='disabled', font=('Arial', '14'), command=self.clicked_analyseButton)
		self.analyseButton.place(x=730, y=680, anchor='nw', width=100, height=25)
        #show audio_Path label
		self.path_label = tk.StringVar()
		self.audio_Path_Label = tk.Label(master, font = ('Arial', 14), justify = 'left', relief = 'groove', borderwidth = 1, textvariable = self.path_label)
		self.audio_Path_Label.place(x = 160, y = 650, anchor = 'nw', width = 770, height = 25)



		# Text Log View   show list audio device and button test
		self.TextLogFrame = tk.LabelFrame(master, text='', width=340, height=250)
		self.TextLogFrame.place(x=320, y=30, anchor='nw')
		self.scrollbarText = tk.Scrollbar(self.TextLogFrame)
		self.scrollbarText.place(x=320, y=0, anchor='nw', width=20, height=245)
		self.textView = tk.Text(self.TextLogFrame, borderwidth=0, font=('Arial', 8), bg=bgWindow, state='normal',yscrollcommand=self.scrollbarText.set)
		self.textView.place(x=10, y=0, anchor='nw', width=300, height=240)
		self.scrollbarText.config(command=self.textView.yview)

		# Label
		self.TitleLbl = tk.Label(master, font=('Arial', 14), text=Title, compound='left', justify='left', borderwidth=0)
		self.TitleLbl.place(x=320, y=17, anchor='w')
		self.appVerLbl = tk.Label(master, font=('Arial', 14), text=App_Ver, compound='left', justify='left', borderwidth=0)
		self.appVerLbl.place(x=760, y=17, anchor='w')
		

		# Canvas View vẽ đồ thị
		self.FrameCanvas = tk.LabelFrame(master, text='', height=320, width=930)
		self.FrameCanvas.place(x=10, y=320, anchor='nw')
		self.FrameCanvas.propagate(0)

		self.WaveFormCanvas = tk.LabelFrame(self.FrameCanvas, height=315, width=455)
		self.WaveFormCanvas.place(x=0, y=0, anchor='nw')

		self.FFTCanvas = tk.LabelFrame(self.FrameCanvas, height=315, width=460)
		self.FFTCanvas.place(x=460, y=0, anchor='nw')

		self.waveform_label = tk.Label(self.WaveFormCanvas)
		self.FFT_label = tk.Label(self.FFTCanvas)

		
		self.HID_Thread = threading.Thread(target=self.USBHID)
		self.HID_Thread.daemon = True
		self.HID_Thread.start()

	def currentTime(self):
		timeNow = datetime.now()
		self.fileTime = timeNow.strftime("%Y-%m-%d_%H%M%S")

	# Clear Text View
	def clicked_clearButton(self):
		self.textViewInsertData(True, '')

	def clicked_playButton(self):  # Play Audio
		if self.playButton.cget('text') == "Play":
			self.playButton.configure(text='Stop')
			print("Play audio")
		
			self.playAudioFlag = True
			audio_thread = threading.Thread(target = self.play_audio_callback)
			audio_thread.start()

		else:
			self.playButton.configure(text='Play')
			self.playAudioFlag = False

	def clicked_clearImageButton(self):
		self.waveform_label.image = None
		self.FFT_label.image = None
		
		

	def clicked_recordButton(self):  # Record audio file
		self.currentTime()
		self.MIC_record(Record_duration)
		self.audio_test.FFT_Function(self.tpath,self.tpath, "\\MIC_record.wav","record")
		analyze_Thread = threading.Thread(target=self.Audio_analyze, args=("record","MIC_record.wav"))
		analyze_Thread.start()

	def clicked_analyseButton(self):
		self.currentTime()
		self.tpath = os.path.join(self.desktopPath, self.fileTime)
		print('self.tpath',self.tpath)
		try:
			if not os.path.exists(self.tpath):
				os.mkdir(self.tpath)
			else:
				print("Directory already exists:", self.tpath)
		except: 
			pass
		self.nameList = self.audio_Path.split('/')
		print('self.nameList',self.nameList)
		self.nameStr = self.nameList[-1]
		print('self.nameStr',len(self.nameStr))
		self.namePath = self.audio_Path.split(self.nameStr)
		print('self.namePath',self.namePath)
		self.audio_test.FFT_Function(self.tpath, self.namePath[0], self.nameList[-1], "analyse")
		analyseButtonThread = threading.Thread(target=self.Audio_analyze, args=("analyse", self.nameList[-1]))
		analyseButtonThread.start()


	def Audio_analyze(self,flag, wavName):  # Play audio through output ID 0 and record audio through input ID 1 then analyze record file
		if flag == "record":
			FFT_results = self.audio_test.Get_FFT_Results(self.tpath,self.tpath, wavName,flag)
		else:
			FFT_results = self.audio_test.Get_FFT_Results(self.tpath,self.namePath[0], wavName,flag)

		Level_result = self.audio_test.Get_level_from_FFT_result(1000, FFT_results,44100)
		THD_result = self.audio_test.Get_THD_from_FFT_result(1000, FFT_results,44100)
		Vrms = pow(10,(Level_result/20)) 
		open_waveform = Image.open(self.tpath + "\\WaveForm.png")
		# else:
		# 	open_waveform = Image.open(self.tpath + "/Original_WaveForm.png")
		#open_waveform = open_waveform.resize((450, 310), Image.ANTIALIAS)
		open_waveform = open_waveform.resize((450, 310))
		waveform_img = ImageTk.PhotoImage(open_waveform)
		self.waveform_label.configure(image=waveform_img)
		self.waveform_label.image = waveform_img
		self.waveform_label.pack()

		# if "MIC_record.wav" in wavName:
		open_FFT = Image.open(self.tpath + "\\FFT.png")
		draw = ImageDraw.Draw(open_FFT)
		draw.text((100,5), "Level:%0.2f dBV   Vrms:%0.9fV  \nTHD+N:%0.2f dB\n" % (Level_result,Vrms,THD_result), (0,0,0), font=self.ArialFont)
		open_FFT.save(self.tpath + "\\FFT.png")
		
		#open_FFT = open_FFT.resize((450, 310), Image.ANTIALIAS)
		open_FFT = open_FFT.resize((450, 310))
		FFT_img = ImageTk.PhotoImage(open_FFT)
		self.FFT_label.configure(image=FFT_img) 
		self.FFT_label.image = FFT_img
		self.FFT_label.pack()  

	def testFinish(self, totalResult):  # Finish test and show result
		if totalResult == True:
			self.textViewInsertData(False, "Test PASS")
			self.statusLbl.configure(background="green", font=('Arial', 14), text="PASS")
		else:
			self.textViewInsertData(False, "Test FAIL")
			self.statusLbl.configure(background="red", font=('Arial', 14), text="FAIL")
		self.hid_flag = True

	# self.HID_Thread.start()

	def textViewInsertData(self, isClear, data):  # insert text log to text view
		self.textView.config(state='normal')
		if isClear == True:
			self.textView.delete(0.5, 'end')
		self.textView.insert(tk.END, str(data) + '\n')
		self.textView.see('end')

	def addLogInfo(self, strLog, log):  # add log info to save log file - not use
		global logData
		# print(getCurrentTime("%Y-%m-%d_%H:%M:%S") + ": " + strLog)
		if log == True:
			# logData.append(getCurrentTime("%Y-%m-%d_%H:%M:%S") + ": " + strLog)
			logData.append(strLog)

	
	def close_window(self):
		self.hid_flag = False
		self.master.quit()

	def USBHID(self):  # communicate with USB device through PID & VID
		isPressUp = False
		isPressDown = False
		isPressMid = False
		while self.hid_flag == True:
			time.sleep(0.1)
			self.isPlugLabel.configure(text='Unplug')
			#for hid_interface in hid.enumerate(0x05AC, 0x110B):
			#for hid_interface in hid.enumerate(0x1611, 0x020F):
			for hid_interface in hid.enumerate(0x31B2, 0x0111):
				if hid_interface['interface_number'] != 3:
					continue
				hid_device = hid.device()
				hid_device.open_path(hid_interface['path'])
				self.isPlugLabel.configure(text='Plugged')
				try:
					while self.hid_flag == True:
						hid_data = hid_device.read(1024)
						if hid_data:
							self.textViewInsertData(False, 'HID Data: "{}"'.format(hid_data))
							if format(hid_data) == "[1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]":
								isPressUp = True
								self.volUpLabel.configure(background="green")
								self.textViewInsertData(False, "Vol + Pressed")
							if format(hid_data) == "[1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0]":
								isPressMid = True
								self.middleLabel.configure(background="green")
								self.textViewInsertData(False, "Middle Pressed")
							if format(hid_data) == "[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0]":
								isPressDown = True
								self.volDownLabel.configure(background="green")
								self.textViewInsertData(False, "Vol - Pressed")
							if format(hid_data) == "[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]":
								if isPressUp == True:
									self.volUpLabel.configure(background="white")
									self.textViewInsertData(False, "Vol + Released")
									isPressUp = False
								if isPressMid == True:
									self.middleLabel.configure(background="white")
									self.textViewInsertData(False, "Middle Released")
									isPressMid = False
								if isPressDown == True:
									self.volDownLabel.configure(background="white")
									self.textViewInsertData(False, "Vol - Released")
									isPressDown = False
				except Exception as e:
					# self.textViewInsertData("error ", e)
					hid_device.close()

	def play_audio_callback(self): # play audio through output ID
		CHUNK = 1024
		wavefile = wave.open(self.audio_Path, 'rb')
		p = pyaudio.PyAudio()

		def callback(in_data, frame_count, time_info, status):
			data = wavefile.readframes(frame_count)
			return (data, pyaudio.paContinue)

		stream = p.open(format=p.get_format_from_width(wavefile.getsampwidth()), channels=wavefile.getnchannels(),
						rate=wavefile.getframerate(), output_device_index = self.outputID, output=True, stream_callback=callback)

		stream.start_stream()
		while stream.is_active():
			time.sleep(0.1)
			if self.playAudioFlag == False:
				break
		stream.stop_stream()
		stream.close()
		p.terminate()

	def MIC_record(self, duration):  # record audio through input ID 
		self.tpath = self.desktopPath + "\\" + self.fileTime
		os.mkdir(self.desktopPath + "\\" + self.fileTime)
		wave_Path = self.tpath + "\\MIC_record.wav"
		self.textViewInsertData(False, wave_Path)
		CHUNK = 1024
		FORMAT = pyaudio.paInt16
		CHANNELS = 1
		RATE = 44100
		p = pyaudio.PyAudio()
		try:
			stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=self.inputID, frames_per_buffer=CHUNK)
		except:
			self.textViewInsertData(False, "* recording error")
		wf = wave.open(wave_Path, 'wb')
		wf.setnchannels(CHANNELS)
		wf.setsampwidth(p.get_sample_size(FORMAT))
		wf.setframerate(RATE)
		self.textViewInsertData(False, "* recording")
		for i in tqdm(range(0, int(RATE / CHUNK * duration))):
			data = stream.read(CHUNK)
			wf.writeframes(data)
		self.textViewInsertData(False, "* done recording")
		stream.stop_stream()
		stream.close()
		p.terminate()
		wf.close()
		




	##### ADD Function #####
	def clicked_selectButton(self):
		filetypes = [('WAV File', '*.wav')]
		self.audio_Path = openFile.askopenfilename(title = 'Select File', initialdir='\\', filetypes=filetypes)
		# self.audio_Path_Label.configure(text = self.audio_Path)
		self.path_label.set("%s" % self.audio_Path)
		self.audio_Path_Label.configure(textvariable = self.path_label)
		if self.audio_Path != '':
			self.analyseButton.configure(state='normal')
			self.playButton.configure(state='normal')

	def clicked_reloadDeviceButton(self):
		if(self.isPlugLabel['text'] == 'Unplug'):
			print('unplug unplug unplug')
			self.playAudioFlag = False
		self.input_List = []
		self.output_List = []
		sd._terminate()
		sd._initialize()
		# print("----------Reload Device----------")
		self.textViewInsertData(False, "\n-----------------Reload Device-----------------")
		deviceList = sd.query_devices()
		self.textViewInsertData(False, sd.query_devices())
		default = sd.query_hostapis()
		self.inputID = int(default[0]['default_input_device'])
		self.outputID = default[0]['default_output_device']
		# print(deviceList)
		for i in range(len(deviceList)):
			if deviceList[i]['max_input_channels'] == 0:
				self.output_List.append(deviceList[i]['name'])
			if deviceList[i]['max_output_channels'] == 0:
				self.input_List.append(deviceList[i]['name'])
		self.inputDevice_Cbb['values'] = (self.input_List)
		self.outputDevice_Cbb['values'] = (self.output_List)

	def selected_input_device(self, a):
		selected = self.inputDevice_Cbb.get()
		# print("\nSelected Input Device:" , selected)
		self.textViewInsertData(False, "-----------------------------------------------------")
		self.textViewInsertData(False, "\nSelected Input Device: %s" % selected)
		deviceList = sd.query_devices()
		for i in range(len(deviceList)):
			if deviceList[i]['max_output_channels'] == 0 and deviceList[i]['name'] == selected:
				self.inputID = deviceList[i]['index']
		# print("\nSet default device : intput = %d, output = %d\nReload device:" % (self.inputID, self.outputID))
		self.textViewInsertData(False, "\nSet default device : intput = %d, output = %d\nReload device:" % (self.inputID, self.outputID))
		sd.default.device = (self.inputID, self.outputID)


	def selected_output_device(self, a):
		selected = self.outputDevice_Cbb.get()
		# print("\nSelected Output Device:" , selected)
		self.textViewInsertData(False, "-----------------------------------------------------")
		self.textViewInsertData(False, "\nSelected Output Device: %s" % selected)
		deviceList = sd.query_devices()
		for i in range(len(deviceList)):
			if deviceList[i]['max_input_channels'] == 0 and deviceList[i]['name'] == selected:
				self.outputID = deviceList[i]['index']
		# print("\nSet default device : intput = %d, output = %d\nReload device:" % (self.inputID, self.outputID))
		self.textViewInsertData(False, "\nSet default device : intput = %d, output = %d\nReload device:" % (self.inputID, self.outputID))
		sd.default.device = (self.inputID, self.outputID)


class Audio_Test():
	"""docstring for Audio_Test"""

	def Get_wave_data(self,path_file, wavName,flag):
		if flag == "record":
			file = wave.open(path_file + "\\MIC_record.wav", "rb")
		else:
			file = wave.open(path_file +"\\"+ wavName, "rb")
		frames_data = file.readframes(file.getnframes()).hex()
		final_data = []
		for i in range(0, len(frames_data), 4):
			wave_data = frames_data[i:i + 4]
			#print("doi 1",wave_data)
			wave_data = wave_data[2:] + wave_data[:2] # đổi ví dụ B4FA => FAB4
			#print("doi 2",wave_data)
			wave_data = int(wave_data, 16) # ép theo định dạng số nguyên 16 bit
			if wave_data > 32767:
				wave_data = wave_data - 65536
			final_data.append(wave_data)

		return final_data[24000:56768]
	

	def FFT_Function(self,savePath,path_file,wavName,flag):
		#print("FFT ",savePath,path_file,wavName,flag)
		fft_input_raw_data = self.Get_wave_data(path_file, wavName,flag)
		# Add window, Blackman-Nutall window function
		a0 = 0.3635819
		a1 = 0.4891775
		a2 = 0.1365995
		a3 = 0.0106411
		FFT_point = 32768  # Điểm thứ 683 là 1k
		plt.ioff()
		f1, test1 = plt.subplots()
		plt.plot(np.array(fft_input_raw_data) / (FFT_point-1))
		test1.set_title("WaveForm", fontsize=10)
		test1.set_ylabel('Amplitude(dBV)', rotation=90, labelpad=5)
		test1.set_xlabel('Time(s)', rotation=0, labelpad=5)
		plt.grid(True)
		#wavePath = savePath + "\WaveForm.png"
		wavePath = os.path.join(savePath, 'WaveForm.png')
		plt.savefig(wavePath)
		#plt.show()
		#plt.close()
		fft_input_data = fft_input_raw_data
		for i in range(0, FFT_point):
			fft_input_data[i] = fft_input_data[i] * (a0 - a1 * np.cos(2 * i * np.pi / FFT_point) + a2 * np.cos(4 * i * np.pi / FFT_point) - a3 * np.cos(6 * i * np.pi / FFT_point))# window_signal = signal * window
		fft_output_data = fft(fft_input_data, FFT_point) # phân tích FFT của tín hiệu
		
		fft_output_data_amplitude = np.abs(fft_output_data) # lấy module của số phức để tính biên độ
		
		fft_output_data_amplitude = 2*fft_output_data_amplitude / FFT_point
		fft_output_data_amplitude[0] = fft_output_data_amplitude[0] / 2
		fft_output_data_amplitude = fft_output_data_amplitude / ((FFT_point-1)*a0)
		fft_output_data_amplitude = 20 * np.log10(fft_output_data_amplitude)

        # Tim tan so
		n = np.linspace(0, int(FFT_point / 2), int(FFT_point / 2)+1 ,endpoint=False)
		frequency = n * 44100/ FFT_point
		f2, test2 = plt.subplots()
		# fig2 = plt.figure()
		plt.semilogx(frequency, fft_output_data_amplitude[0:int(FFT_point / 2) + 1])
		test2.set_title("FFT", fontsize=10)
		test2.set_ylabel('Amplitude(dBV)', rotation=90, labelpad=5)
		test2.set_xlabel('Frequency(Hz)', rotation=0, labelpad=5)
		test2.set_xticks([10, 100, 1000, 10000,20000], ['10', '100', '1K', '10K','20k'])
		plt.grid(True)
		fftPath = savePath + "\\FFT.png"
		plt.savefig(fftPath)
		plt.close()

	def Get_FFT_Results(self, savePath,path_file, wavName,flag):
		file = open(savePath + "\\FFT_Result.txt", "w", encoding="utf-8")
		fft_input_raw_data = self.Get_wave_data(path_file, wavName,flag)
		a0 = 0.3635819
		a1 = 0.4891775
		a2 = 0.1365995
		a3 = 0.0106411
		FFT_point = 32768  # 第683个点是1k
		fft_input_data = fft_input_raw_data
		for i in range(0, FFT_point):
			fft_input_data[i] = fft_input_data[i] * (a0 - a1 * np.cos(2 * i * np.pi / FFT_point) + a2 * np.cos(4 * i * np.pi / FFT_point) - a3 * np.cos(6 * i * np.pi / FFT_point))
		fft_output_data = fft(fft_input_data, FFT_point)
		fft_output_data_amplitude = np.abs(fft_output_data)
		fft_output_data_amplitude = 2*fft_output_data_amplitude / FFT_point 
		fft_output_data_amplitude[0] = fft_output_data_amplitude[0] / 2
		fft_output_data_amplitude = fft_output_data_amplitude/(FFT_point-1)/a0 # tin hiệu= tín hiệu gốc * window= tin hiệu gốc * (L-1)*a0
		fft_output_data_amplitude = 20 * np.log10(fft_output_data_amplitude)
		n = np.linspace(0, int(FFT_point / 2), int(FFT_point / 2) + 1)# tọa độ các điểm của trục tần số cách đều nhau bắt đầu từ 0 kết thúc ở FFT_point/2 và mỗi điểm cách đều nhau 1 khoảng là FFT_point/2 +1
		frequency = n * 44100/ FFT_point# tính ra các tần số lưu vào mảng frequency
		for i in range(0, int(FFT_point / 2), 1):# viết ra các điểm tần số và điểm biên độ tương ứng
			file.write(str(frequency[i]) + "\t" + str(fft_output_data_amplitude[i]) + "\n")
		file.close()
		return fft_output_data_amplitude[0:int(FFT_point / 2)]
		

	def Get_level_from_FFT_result(self, frequency, FFT_result,Sample_Rate): # đi tìm biên độ lớn nhất ứng với tần số frequency
		notch = 7
		FFT_point = 32768
		position = int(frequency * FFT_point/ Sample_Rate)  # 取左右各7个点，找最大值 Lấy 7 điểm ở bên trái và bên phải và tìm giá trị lớn nhất
		print("max level",)
		max_value = max(FFT_result[position - notch:position + notch + 1])
		return max_value

	def Get_THD_from_FFT_result(self, frequency, FFT_result,Sample_Rate):
		notch = 7
		FFT_point = 32768
		position = int(frequency * FFT_point/Sample_Rate) 
		Fundamental=0
		Fundamental = max(FFT_result[position - notch:position + notch + 1])
		Fundamental=pow(10,(Fundamental/20)) 
		# 从第一个点开始
		sum_noise = 0
		# for i in range(14, length):
		for i in range(14, 13654):
			if i < position - notch or i > position + notch:
				sum_noise = sum_noise + (10 ** (FFT_result[i] / 20)) ** 2
			else:
				sum_noise = sum_noise + 0
		sum_noise = sum_noise ** 0.5
		THD_value = 20 * math.log10(sum_noise / Fundamental)
		return THD_value

if __name__ == '__main__':
	multiprocessing.freeze_support()
	window = tk.Tk()
	window.title("Audio Analysis Software")
	window_width = 950
	window_height = 720
	screenWidth = window.winfo_screenwidth()
	screenHeight = window.winfo_screenheight()
	window.geometry('%dx%d+%d+%d' % (window_width, window_height, (screenWidth - window_width) / 2, ((screenHeight - window_height) / 2) - 50))
	window.resizable(0, 0)
	bgWindow = window['bg']
	UI = startUI(window)
	window.mainloop()

