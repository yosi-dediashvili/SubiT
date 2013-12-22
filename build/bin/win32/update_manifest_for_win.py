import os
import sys
import time

subit_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
subit_path = subit_dir + "\\SubiT.exe"
config_path = os.path.join(subit_dir, 'Settings', 'config.ini')
subit_exe_current_stat = os.stat(subit_path)
config_current_stat = os.stat(config_path)
subit_task_name = "SubiTAssociateTask"
batch_file_path = os.path.join(subit_dir, "subit-associate.bat")

time_plus_30_secs = time.localtime(int(time.time() + 60))
time_str = str(time_plus_30_secs.tm_hour).rjust(2, "0")
time_str += ":"
time_str += str(time_plus_30_secs.tm_min).rjust(2, "0")
time_str += ":"
time_str += str(time_plus_30_secs.tm_sec).rjust(2, "0")

with open(batch_file_path, 'w') as bf:
	bf.write("\"%s\" -associate\n" % subit_path)
	bf.write("schtasks.exe /delete /tn %s /f\n" % subit_task_name)
	bf.write("del /f \"%s\"\n" % batch_file_path)

command = ("schtasks.exe /create /tn %s /tr \"%s\" /sc ONCE /st %s" % 
			(subit_task_name, batch_file_path, time_str))

os.system(command)